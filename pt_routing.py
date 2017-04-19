from collections import defaultdict
from collections import namedtuple
import random
from algorithms.PairTransitionsAlgorithm import PairTransitionsAlgorithm

import pox.openflow.libopenflow_01 as of
from pox.openflow.libopenflow_01 import ofp_flow_mod_flags_rev_map
from pox.core import core
from pox.lib.revent.revent import EventMixin, Event

from network.MetricDataParser import MetricDataParser
from network.Sender import Sender

pox_logger = core.getLogger()

switch_objects = {}
switch_ports = {}
port_map = defaultdict(lambda: defaultdict(lambda: None))
weight_map = defaultdict(lambda: defaultdict(lambda: None))
mac_table = {}

alg = PairTransitionsAlgorithm(switch_objects, weight_map)


def _install_route(path, match):
    destination_switch_index = path.destination
    current_switch_index = path.source
    destination_package = match.dl_dst
    message = build_flow_install_message(match, mac_table[destination_package].port)
    switch_objects[destination_switch_index].connection.send(message)

    iterator = path.vertex_iterator
    while iterator.move_next():
        next_switch_index = iterator.current
        message = build_flow_install_message(match, port_map[current_switch_index][next_switch_index])
        switch_objects[current_switch_index].connection.send(message)
        current_switch_index = next_switch_index


def build_flow_install_message(match, outport):
    msg = of.ofp_flow_mod()
    msg.match = match
    msg.idle_timeout = 10
    msg.flags = ofp_flow_mod_flags_rev_map["OFPFF_SEND_FLOW_REM"]
    msg.actions.append(of.ofp_action_output(port=outport))
    return msg


class NewFlowEvent(Event):
    def __init__(self, path, match, adj):
        Event.__init__(self)
        self.match = match
        self.path = path
        self.adj = adj


class SwitchObject(EventMixin):
    _eventMixin_events = {NewFlowEvent}
    can_recompute = False
    changes_number = 25

    def __init__(self, connection, l3_matching=False):
        super(SwitchObject, self).__init__()
        self.connection = connection
        self.l3_matching = l3_matching
        connection.addListeners(self)

    def __repr__(self):
        return 's{}'.format(self.connection.dpid)

    def _handle_PacketIn(self, event):

        def flood():
            for (dpid, switch) in switch_objects.iteritems():
                msg = of.ofp_packet_out()
                if switch == self:
                    if event.ofp.buffer_id is not None:
                        msg.buffer_id = event.ofp.buffer_id
                    else:
                        msg.data = event.ofp.data
                    msg.in_port = event.port
                else:
                    msg.data = event.ofp.data
                ports = [p for p in switch.connection.ports if (dpid, p) not in switch_ports]
                if len(ports) > 0:
                    for p in ports:
                        msg.actions.append(of.ofp_action_output(port=p))
                    switch_objects[dpid].connection.send(msg)

        def drop():
            if event.ofp.buffer_id is not None:
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                event.ofp.buffer_id = None
                msg.in_port = event.port
                self.connection.send(msg)

        packet = event.parsed
        SwitchPort = namedtuple('SwitchPoint', 'dpid port')

        if (event.dpid, event.port) not in switch_ports:
            mac_table[packet.src] = SwitchPort(event.dpid, event.port)

        if packet.effective_ethertype == packet.LLDP_TYPE:
            drop()
        elif packet.dst.is_multicast:
            flood()
        elif packet.dst not in mac_table:
            flood()
        elif packet.effective_ethertype == packet.ARP_TYPE:
            drop()
            dst = mac_table[packet.dst]
            msg = of.ofp_packet_out()
            msg.data = event.ofp.data
            msg.actions.append(of.ofp_action_output(port=dst.port))
            switch_objects[dst.dpid].connection.send(msg)
        else:
            dst = mac_table[packet.dst]
            route = alg.compute_shortest_route(src=self.connection.dpid, dst=dst.dpid)
            alg.collect_statistics()
            if not route:
                flood()
                return
            print "Computed route from h{} to h{}: {}".format(
                str(packet.src)[-1], str(packet.dst)[-1], route)
            match = of.ofp_match.from_packet(packet)
            _install_route(route, match)
            Sender(pox_logger).send_path(route.__repr__())
            drop()
            dst = mac_table[packet.dst]
            msg = of.ofp_packet_out()
            msg.data = event.ofp.data
            msg.actions.append(of.ofp_action_output(port=dst.port))
            switch_objects[dst.dpid].connection.send(msg)
            self.raiseEvent(NewFlowEvent(route, match, port_map))
            # if ControllerEventHandler.can_recompute:
            #     core.callDelayed(6, self.recompute, packet, event)
            # else:
            #     ControllerEventHandler.can_recompute = True

    def recompute(self, packet, event):
        self.change_metric()
        route = alg.recompute_shortest_route()

        print "Computed route from h{} to h{}: {}".format(
            str(packet.src)[-1], str(packet.dst)[-1], route)

        match = of.ofp_match.from_packet(packet)
        _install_route(route, match)
        Sender(pox_logger).send_path(route.__repr__())
        dst = mac_table[packet.dst]
        msg = of.ofp_packet_out()
        msg.data = event.ofp.data
        msg.actions.append(of.ofp_action_output(port=dst.port))
        switch_objects[dst.dpid].connection.send(msg)
        self.raiseEvent(NewFlowEvent(route, match, port_map))
        pt = alg.count_pair_transitions()
        print pt
        Sender(pox_logger).send_pt(pt)
        if SwitchObject.changes_number > 0:
            core.callDelayed(6, self.recompute, packet, event)
        SwitchObject.changes_number -= 1

    def change_metric(self):
        tmp = random.choice(weight_map.items())
        weight_map[tmp[0]][random.choice(tmp[1].keys())] = \
            random.randint(1, 15)

    def _handle_ConnectionDown(self, event):
        del switch_objects[self.connection.dpid]


class SwitchConnectedEvent(Event):
    def __init__(self, switch):
        Event.__init__(self)
        self.switch = switch


class Forwarding(EventMixin):
    _core_name = "sdnrouting_pt"
    _eventMixin_events = {SwitchConnectedEvent}

    def __init__(self):
        super(Forwarding, self).__init__()
        pox_logger.debug("Forwarding coming up")

        def startup():
            core.openflow.addListeners(self)
            core.openflow_discovery.addListeners(self)

            parser = MetricDataParser(weight_map)
            parser.read_matrix_from("metric_data.txt")
            pox_logger.debug("Forwarding started")

        core.call_when_ready(startup, 'openflow', 'openflow_discovery')

    def _handle_LinkEvent(self, event):
        link = event.link
        if event.added:
            port_map[link.dpid1][link.dpid2] = link.port1
            switch_ports[link.dpid1, link.port1] = link

    def _handle_ConnectionUp(self, event):
        print "New switch connection: {}".format(event.connection)
        switch = SwitchObject(event.connection)
        switch_objects[event.dpid] = switch
        self.raiseEvent(SwitchConnectedEvent(switch))


def launch():
    core.registerNew(Forwarding)
