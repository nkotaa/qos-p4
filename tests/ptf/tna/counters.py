import ptf.testutils as testutils
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import bfrt_grpc.client as gc
import p4testutils.misc_utils as misc_utils

from base_test import FlowTest

try:
    import controller
except ImportError:
    import os
    import sys
    TESTDIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(TESTDIR, '..', '..', '..'))
from controller.switch_connection import BFRuntimeSwitchConnection
from controller.monitor import BFRuntimeMonitor

program_name = testutils.test_param_get("p4_name")
pkt_len = int(testutils.test_param_get("pkt_len", "128"))
num_pkts = int(testutils.test_param_get("num_pkts", "2"))

logger = misc_utils.get_logger()

def _set_up_monitor_controller():
    switch_connection = BFRuntimeSwitchConnection(program_name=program_name)
    return BFRuntimeMonitor(switch_connection)

class MonitorControllerTest(FlowTest):

    def setUp(self):
        FlowTest.setUp(self)
        self.monitor = _set_up_monitor_controller()

    def runTest(self):
        pkt = testutils.simple_tcp_packet(
            eth_src=self.source_mac, eth_dst=self.dest_mac,
            dl_vlan_enable=True, vlan_vid=self.vlan_vid,
            pktlen=pkt_len)
        FlowTest.program_mac_forward_table(self)
        FlowTest.check_port_forwarding(self, pkt)
        FlowTest.program_flow_watchlist_table(self)

        logger.info("Starting counters and sending packets...")
        self.monitor.start_rx_counter(self.flow_id)
        self.monitor.start_tx_counter(self.flow_id)
        testutils.send_packet(self, self.ingress_port, pkt, count=num_pkts)
        testutils.verify_each_packet_on_each_port(self, [pkt] * num_pkts,
                                                  [self.egress_port] * num_pkts)
        rx_count = self.monitor.read_rx_counter(self.flow_id)
        tx_count = self.monitor.read_tx_counter(self.flow_id)

        # Default packet size is pkt_len bytes and model adds 4 bytes of CRC
        pkt_size = pkt_len + 4
        expected_byte_count = num_pkts * pkt_size
        logger.info(
            "bytes sent = %s, received count = %s, transmitted count = %s",
            str(expected_byte_count), str(rx_count), str(tx_count))

    def tearDown(self):
        self.monitor.stop_rx_counter(self.flow_id)
        self.monitor.stop_tx_counter(self.flow_id)
        FlowTest.tearDown(self)
