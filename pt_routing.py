from collections import defaultdict
from collections import namedtuple
import random
from algorithms.PairTransitionsAlgorithm import PairTransitionsAlgorithm

import pox.openflow.libopenflow_01 as of
from pox.core import core
from pox.lib.revent.revent import EventMixin, Event

from network.MetricDataParser import MetricDataParser
from network.Sender import Sender

pox_logger = core.getLogger()

switches = {}
switch_ports = {}
port_map = defaultdict(lambda: defaultdict(lambda: None))
weight_map = defaultdict(lambda: defaultdict(lambda: None))
mac_table = {}

alg = PairTransitionsAlgorithm(switches, weight_map)


def _install_route(path, match):
    destination_switch_index = path.destination
    current_switch_index = path.source
    destination_package = match.dl_dst
    pox_logger.debug("Installing forward from switch s%s to output port %s",
                     current_switch_index, mac_table[destination_package].port)
    message = build_flow_install_message(match, mac_table[destination_package].port)
    switches[destination_switch_index].connection.send(message)

    iterator = path.vertex_iterator
    while iterator.move_next():
        next_switch_index = iterator.current
        pox_logger.debug("Installing forward from switch s%s to switch s%s output port %s",
                         current_switch_index, next_switch_index,
                         port_map[current_switch_index][next_switch_index])
        message = build_flow_install_message(match, port_map[current_switch_index][next_switch_index])
        switches[current_switch_index].connection.send(message)
        current_switch_index = next_switch_index


def build_flow_install_message(match, outport):
    message = of.ofp_flow_mod()
    message.match = match
    message.idle_timeout = 10
    message.flags = of.OFPFF_SEND_FLOW_REM
    message.actions.append(of.ofp_action_output(port=outport))
    return message


class NewFlowEvent(Event):
    def __init__(self, path, match, adj):
        Event.__init__(self)
        self.match = match
        self.path = path
        self.adj = adj


class ControllerEventHandler(EventMixin):
    _eventMixin_events = {NewFlowEvent}
    # мои костыли
    can_recompute = False
    changes_number = 25

    def __init__(self, connection, l3_matching=False):
        super(ControllerEventHandler, self).__init__()
        self.connection = connection
        self.l3_matching = l3_matching
        connection.addListeners(self)
        for p in self.connection.ports.itervalues():
            self.enable_flooding(p.port_no)

    def __repr__(self):
        return 's{}'.format(self.connection.dpid)

    def disable_flooding(self, port):
        msg = of.ofp_port_mod(port_no=port,
                              hw_addr=self.connection.ports[port].hw_addr,
                              config=of.OFPPC_NO_FLOOD,
                              mask=of.OFPPC_NO_FLOOD)
        self.connection.send(msg)

    def enable_flooding(self, port):
        msg = of.ofp_port_mod(port_no=port,
                              hw_addr=self.connection.ports[port].hw_addr,
                              config=0,  # opposite of of.OFPPC_NO_FLOOD,
                              mask=of.OFPPC_NO_FLOOD)
        self.connection.send(msg)

    def _handle_PacketIn(self, event):

        def flood():
            for (dpid, switch) in switches.iteritems():
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
                    switches[dpid].connection.send(msg)

        def drop():
            if event.ofp.buffer_id is not None:
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                event.ofp.buffer_id = None
                msg.in_port = event.port
                self.connection.send(msg)

        packet = event.parsed
        pox_logger.debug("Received packet [SRC: h%s(%s) DST: h%s(%s)]",
                         str(packet.src)[-1], packet.src,
                         str(packet.dst)[-1], packet.dst)

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
            switches[dst.dpid].connection.send(msg)
        else:
            dst = mac_table[packet.dst]

            route = alg.compute_shortest_route(src=self.connection.dpid, dst=dst.dpid)
            alg.collect_statistics()
            if not route:
                flood()
                return

            pox_logger.debug("Computed route from h%s to h%s: %s",
                             str(packet.src)[-1], str(packet.dst)[-1], route)

            match = of.ofp_match.from_packet(packet)
            _install_route(route, match)
            Sender(pox_logger).send_path(route.__repr__())
            drop()
            dst = mac_table[packet.dst]
            msg = of.ofp_packet_out()
            msg.data = event.ofp.data
            msg.actions.append(of.ofp_action_output(port=dst.port))
            switches[dst.dpid].connection.send(msg)

            self.raiseEvent(NewFlowEvent(route, match, port_map))

            if ControllerEventHandler.can_recompute:
                core.callDelayed(6, self.recompute, packet, event)
            else:
                ControllerEventHandler.can_recompute = True

    def recompute(self, packet, event):
        self.change_metric()
        route = alg.recompute_shortest_route()

        pox_logger.debug("Computed route from h%s to h%s: %s",
                         str(packet.src)[-1], str(packet.dst)[-1], route)

        match = of.ofp_match.from_packet(packet)
        _install_route(route, match)
        Sender(pox_logger).send_path(route.__repr__())
        dst = mac_table[packet.dst]
        msg = of.ofp_packet_out()
        msg.data = event.ofp.data
        msg.actions.append(of.ofp_action_output(port=dst.port))
        switches[dst.dpid].connection.send(msg)
        self.raiseEvent(NewFlowEvent(route, match, port_map))
        pt = alg.count_pair_transitions()
        print pt
        Sender(pox_logger).send_pt(pt)
        if ControllerEventHandler.changes_number > 0:
            core.callDelayed(6, self.recompute, packet, event)
        ControllerEventHandler.changes_number -= 1

    def change_metric(self):
        tmp = random.choice(weight_map.items())
        weight_map[tmp[0]][random.choice(tmp[1].keys())] = \
            random.randint(1, 15)

    def _handle_ConnectionDown(self, event):
        pox_logger.debug("Switch s%s going down", self.connection.dpid)
        del switches[self.connection.dpid]


class SwitchConnectedEvent(Event):
    def __init__(self, switch):
        Event.__init__(self)
        self.switch = switch


class Forwarding(EventMixin):
    _core_name = "sdnrouting_pt"
    _eventMixin_events = {SwitchConnectedEvent}

    def __init__(self, l3_matching):
        pox_logger.debug("Forwarding coming up")

        def startup():
            core.openflow.addListeners(self)
            core.openflow_discovery.addListeners(self)

            parser = MetricDataParser(weight_map)
            parser.read_matrix_from("metric_data.txt")
            pox_logger.debug("Forwarding started")

        self.l3_matching = l3_matching
        core.call_when_ready(startup, 'openflow', 'openflow_discovery')

    def _handle_LinkEvent(self, event):
        link = event.link
        if event.added:
            pox_logger.debug("Received LinkEvent, Link Added from s%s to s%s over port %d", link.dpid1,
                             link.dpid2, link.port1)
            port_map[link.dpid1][link.dpid2] = link.port1
            switch_ports[link.dpid1, link.port1] = link
        else:
            pox_logger.debug("Received LinkEvent, Link Removed from s%s to s%s over port %d", link.dpid1,
                             link.dpid2, link.port1)

    def _handle_ConnectionUp(self, event):
        pox_logger.debug("New switch connection: %s", event.connection)
        switch = ControllerEventHandler(event.connection, l3_matching=self.l3_matching)
        switches[event.dpid] = switch
        self.raiseEvent(SwitchConnectedEvent(switch))


def launch(l3_matching=False):
    core.registerNew(Forwarding, l3_matching)
