"""
OpenNetMon.Forwarding

Requires openflow.discovery
"""

from collections import defaultdict
from collections import namedtuple

import pox.openflow.libopenflow_01 as of
from pox.core import core
from pox.lib.revent.revent import EventMixin, Event

from algorithms.RoutingController import RoutingController
from network.WeightsMatrixParser import WeightsMatrixParser

log = core.getLogger()

switches = {}
switch_ports = {}
adj = defaultdict(lambda: defaultdict(lambda: None))
weights = defaultdict(lambda: defaultdict(lambda: None))

mac_learning = {}


def _install_path(path, match):
    dst_sw = path.source
    cur_sw = path.destination
    dst_pck = match.dl_dst

    msg = of.ofp_flow_mod()
    msg.match = match
    msg.idle_timeout = 10
    msg.flags = of.OFPFF_SEND_FLOW_REM
    msg.actions.append(of.ofp_action_output(port=mac_learning[dst_pck].port))
    log.debug("Installing forward from switch s%s to output port %s", cur_sw,
              mac_learning[dst_pck].port)
    switches[dst_sw].connection.send(msg)

    next_sw = cur_sw
    cur_sw = path.previous_sequence[next_sw]
    while cur_sw is not None:  # for switch in path.keys():
        msg = of.ofp_flow_mod()
        msg.match = match
        msg.idle_timeout = 10
        msg.flags = of.OFPFF_SEND_FLOW_REM
        log.debug("Installing forward from switch s%s to switch s%s output port %s", cur_sw,
                  next_sw, adj[cur_sw][next_sw])
        msg.actions.append(of.ofp_action_output(port=adj[cur_sw][next_sw]))
        switches[cur_sw].connection.send(msg)
        next_sw = cur_sw
        cur_sw = path.previous_sequence[next_sw]


class NewFlowEvent(Event):
    def __init__(self, path, match, adj):
        Event.__init__(self)
        self.match = match
        self.path = path
        self.adj = adj


class Switch(EventMixin):
    _eventMixin_events = {NewFlowEvent}

    def __init__(self, connection, l3_matching=False):
        self._routing_controller = RoutingController(switches, adj, weights, log)
        self.connection = connection
        self.l3_matching = l3_matching
        connection.addListeners(self)
        for p in self.connection.ports.itervalues():
            self.enable_flooding(p.port_no)

    def __repr__(self):
        return 's%s' % self.connection.dpid

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

        def forward(port):
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port=port))
            if event.ofp.buffer_id is not None:
                msg.buffer_id = event.ofp.buffer_id
            else:
                msg.data = event.ofp.data
            msg.in_port = event.port
            self.connection.send(msg)

        def flood():
            # forward(of.OFPP_FLOOD)
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

        log.debug("Received PacketIn")
        packet = event.parsed

        SwitchPort = namedtuple('SwitchPoint', 'dpid port')

        if (event.dpid, event.port) not in switch_ports:
            mac_learning[packet.src] = SwitchPort(event.dpid, event.port)

        if packet.effective_ethertype == packet.LLDP_TYPE:
            drop()
        elif packet.dst.is_multicast:
            flood()
        elif packet.dst not in mac_learning:
            flood()
        elif packet.effective_ethertype == packet.ARP_TYPE:

            drop()
            dst = mac_learning[packet.dst]
            msg = of.ofp_packet_out()
            msg.data = event.ofp.data
            msg.actions.append(of.ofp_action_output(port=dst.port))
            switches[dst.dpid].connection.send(msg)
        else:
            dst = mac_learning[packet.dst]

            if not self._routing_controller.is_segmented:
                self._routing_controller.compute_islands()

            path_dpids = self._routing_controller.compute_path(self.connection.dpid, dst.dpid)
            if path_dpids is None:
                flood()
                return

            log.debug("Path from %s to %s over path %s", packet.src, packet.dst, path_dpids)
            match = of.ofp_match.from_packet(packet)
            _install_path(path_dpids, match)
            drop()
            dst = mac_learning[packet.dst]
            msg = of.ofp_packet_out()
            msg.data = event.ofp.data
            msg.actions.append(of.ofp_action_output(port=dst.port))
            switches[dst.dpid].connection.send(msg)

            self.raiseEvent(NewFlowEvent(path_dpids, match, adj))

    def _handle_ConnectionDown(self, event):
        log.debug("Switch s%s going down", self.connection.dpid)
        del switches[self.connection.dpid]


class NewSwitchEvent(Event):
    def __init__(self, switch):
        Event.__init__(self)
        self.switch = switch


class Forwarding(EventMixin):
    _core_name = "sdnrouting_forwarding"
    _eventMixin_events = {NewSwitchEvent}

    def __init__(self, l3_matching):
        log.debug("Forwarding coming up")

        def startup():
            core.openflow.addListeners(self)
            core.openflow_discovery.addListeners(self)

            parser = WeightsMatrixParser(weights, log)
            parser.read_matrix_from("weights_matrix.txt")
            log.debug("Forwarding started")

        self.l3_matching = l3_matching
        core.call_when_ready(startup, 'openflow', 'openflow_discovery')

    def _handle_LinkEvent(self, event):
        link = event.link
        if event.added:
            log.debug("Received LinkEvent, Link Added from s%s to s%s over port %d", link.dpid1,
                      link.dpid2, link.port1)
            adj[link.dpid1][link.dpid2] = link.port1
            switch_ports[link.dpid1, link.port1] = link
        else:
            log.debug("Received LinkEvent, Link Removed from s%s to s%s over port %d", link.dpid1,
                      link.dpid2, link.port1)

    def _handle_ConnectionUp(self, event):
        log.debug("New switch connection: %s", event.connection)
        switch = Switch(event.connection, l3_matching=self.l3_matching)
        switches[event.dpid] = switch
        self.raiseEvent(NewSwitchEvent(switch))


def launch(l3_matching=False):
    core.registerNew(Forwarding, l3_matching)
