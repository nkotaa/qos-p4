import ptf.testutils as testutils
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import bfrt_grpc.client as gc
import p4testutils.misc_utils as misc_utils

try:
    import controller
except ImportError:
    import os
    import sys
    TESTDIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(TESTDIR, '..', '..', '..'))
from controller.switch_connection import BFRuntimeSwitchConnection
from controller.monitor import BFRuntimeMonitor
from controller.flow import DataFlow

program_name = testutils.test_param_get("p4_name")
pkt_len = int(testutils.test_param_get("pkt_len", "128"))

logger = misc_utils.get_logger()
logger.info("Test called with params %s", str(testutils.test_params_get()))

sw_ports = misc_utils.get_sw_ports()
ingress_port = int(testutils.test_param_get("igr_port", sw_ports[1]))
egress_port = int(testutils.test_param_get("egr_port", sw_ports[2]))

def _set_up_monitor_controller():
    switch_connection = BFRuntimeSwitchConnection(program_name=program_name)
    return BFRuntimeMonitor(switch_connection)

class ControllerTest(BfRuntimeTest):

    def setUp(self):
        client_id = 0
        BfRuntimeTest.setUp(self, client_id, program_name)
        self.monitor = _set_up_monitor_controller()
        self.flow_selector = DataFlow(ingress_port=ingress_port,
                                      egress_port=egress_port)

    def runTest(self):
        source_mac = "11:33:55:77:99:00"
        dest_mac = "00:11:22:33:44:55"

        logger.info("Checking if MAC forwarding rules present in switch")
        pkt = testutils.simple_tcp_packet(eth_src=source_mac, eth_dst=dest_mac)
        testutils.send_packet(self, ingress_port, pkt)
        testutils.verify_packets(self, pkt, [egress_port])

        pkt = testutils.simple_tcp_packet(eth_src=source_mac, eth_dst=dest_mac,
                                          pktlen=pkt_len)
        num_pkts = 2

        self.monitor.start_counter(self.flow_selector)
        testutils.send_packet(self, ingress_port, pkt, count=num_pkts)
        testutils.verify_each_packet_on_each_port(self, [pkt, pkt],
                                                  [egress_port, egress_port])
        rx_count = self.monitor.read_rx_counter(self.flow_selector)

        # Default packet size is pkt_len bytes and model adds 4 bytes of CRC
        pkt_size = pkt_len + 4
        expected_byte_count = num_pkts * pkt_size
        logger.info("bytes sent = %s received count = %s",
                    str(expected_byte_count), str(rx_count))

    def tearDown(self):
        self.monitor.stop_counter(self.flow_selector)
        BfRuntimeTest.tearDown(self)
