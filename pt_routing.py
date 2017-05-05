import random
from collections import defaultdict, namedtuple

import pox.openflow.libopenflow_01 as of
from algorithms.PairTransitionsAlgorithm import PairTransitionsAlgorithm
from network.sending import *
from pox.core import core
from pox.lib.revent.revent import EventMixin
from pox.openflow.libopenflow_01 import ofp_flow_mod_flags_rev_map

port_map = defaultdict(lambda: defaultdict(lambda: None))
weight_map = defaultdict(lambda: defaultdict(lambda: None))
switch_objects = {}
switch_ports = {}
mac_table = {}
alg = PairTransitionsAlgorithm(switch_objects, weight_map)
SwitchPort = namedtuple("SwitchPort", ["dpid", "port"])


def read_matrix_from(filename):
    """ Reads weights from file 'filename' """

    def parse(entry):
        """ Parses entry in file with weights """
        args = entry.split(':')
        weight = float(args[1])
        args = args[0].split('-')
        s1 = int(args[0])
        s2 = int(args[1])
        weight_map[s1][s2] = weight
        weight_map[s2][s1] = weight

    try:
        with open(filename, 'r') as f:
            entries = f.readlines()
    except IOError as e:
        print e.message
        return

    for entry in entries:
        parse(entry)


read_matrix_from("metric_data.txt")


def install_route(path, match):
    def build_flow_install_message(match, outport):
        msg = of.ofp_flow_mod()
        msg.match = match
        msg.idle_timeout = 10
        msg.flags = ofp_flow_mod_flags_rev_map["OFPFF_SEND_FLOW_REM"]
        msg.actions.append(of.ofp_action_output(port=outport))
        return msg

    destination_switch_index = path.destination
    current_switch_index = path.source
    destination_package = match.dl_dst
    message = build_flow_install_message(match, mac_table[destination_package].port)
    switch_objects[destination_switch_index].connection.send(message)

    iterator = path.switch_iterator
    while iterator.move_next():
        next_switch_index = iterator.current
        message = build_flow_install_message(match, port_map[current_switch_index][next_switch_index])
        switch_objects[current_switch_index].connection.send(message)
        current_switch_index = next_switch_index


class SwitchObject(EventMixin):
    can_recompute = False
    changes_number = 100

    def __init__(self, connection):
        super(SwitchObject, self).__init__()
        self.connection = connection
        connection.addListeners(self)

    def __repr__(self):
        return 's{}'.format(self.connection.dpid)

    def flood(self, event):
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

    def drop(self, event):
        if not event.ofp.buffer_id:
            return
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        event.ofp.buffer_id = None
        msg.in_port = event.port
        self.connection.send(msg)

    def forward(self, event):
        packet = event.parsed
        dst = mac_table[packet.dst]
        msg = of.ofp_packet_out()
        msg.data = event.ofp.data
        msg.actions.append(of.ofp_action_output(port=dst.port))
        switch_objects[dst.dpid].connection.send(msg)

    def routing(self, event):
        packet = event.parsed
        route = alg.compute_shortest_route(
            src=self.connection.dpid, dst=mac_table[packet.dst].dpid)
        alg.collect_statistics()
        if not route:
            self.drop(event)
            return
        send_message("Computed route from h{} to h{}: {}".format(
            str(packet.src)[-1], str(packet.dst)[-1], route))
        send_message("")
        send_message("")
        match = of.ofp_match.from_packet(packet)
        install_route(route, match)
        send_tree(alg.tree)
        if SwitchObject.can_recompute:
            core.callDelayed(2, self.simulate_routing, event)
        else:
            SwitchObject.can_recompute = True

    def simulate_routing(self, event):

        def change_metric():
            tmp = random.choice(weight_map.items())
            s1 = tmp[0]
            s2 = random.choice(tmp[1].keys())
            new_metric = random.randint(20, 100)
            send_message("Link s{}-s{}: {} -> {}".format(
                s1, s2, weight_map[s1][s2], new_metric))
            weight_map[s1][s2] = new_metric
            send_metric(s1, new_metric, s2)

        change_metric()
        packet = event.parsed
        route = alg.recompute_shortest_route()
        match = of.ofp_match.from_packet(packet)
        install_route(route, match)
        self.forward(event)
        pt = alg.count_pair_transitions()
        send_message("Route from h{} to h{}: {}".format(
            str(packet.src)[-1], str(packet.dst)[-1], route))
        send_message("Pair transitions occurred: {}".format(pt))
        send_message("")
        send_message("")
        send_tree(alg.tree)
        send_pt(pt)
        if SwitchObject.changes_number > 0:
            core.callDelayed(2, self.simulate_routing, event)
        SwitchObject.changes_number -= 1

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if (event.dpid, event.port) not in switch_ports:
            mac_table[packet.src] = SwitchPort(event.dpid, event.port)
        if packet.effective_ethertype == packet.LLDP_TYPE:
            self.drop(event)
        elif packet.dst.is_multicast:
            self.flood(event)
        elif packet.dst not in mac_table:
            self.flood(event)
        elif packet.effective_ethertype == packet.ARP_TYPE:
            self.drop(event)
            self.forward(event)
        else:
            self.drop(event)
            self.forward(event)
            self.routing(event)

    def _handle_ConnectionDown(self, event):
        del switch_objects[self.connection.dpid]


class Forwarding(EventMixin):

    def __init__(self):
        super(Forwarding, self).__init__()

        def startup():
            core.openflow.addListeners(self)
            core.openflow_discovery.addListeners(self)

        core.call_when_ready(startup, 'openflow', 'openflow_discovery')

    def _handle_LinkEvent(self, event):
        link = event.link
        if event.added:
            port_map[link.dpid1][link.dpid2] = link.port1
            switch_ports[link.dpid1, link.port1] = link

    def _handle_ConnectionUp(self, event):
        switch = SwitchObject(event.connection)
        switch_objects[event.dpid] = switch


def launch():
    core.registerNew(Forwarding)
