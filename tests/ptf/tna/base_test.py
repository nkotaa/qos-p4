import ptf.testutils as testutils
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.client as gc
import p4testutils.misc_utils as misc_utils

program_name = testutils.test_param_get("p4_name")

sw_ports = misc_utils.get_sw_ports()
ingress_port = int(testutils.test_param_get("igr_port", sw_ports[1]))
egress_port = int(testutils.test_param_get("egr_port", sw_ports[2]))
vlan_vid = int(testutils.test_param_get("vlanid", 1))
flow_id = int(testutils.test_param_get("flow_id", 60))

logger = misc_utils.get_logger()

class FlowTest(BfRuntimeTest):

    ingress_port = ingress_port
    egress_port = egress_port
    vlan_vid = vlan_vid
    flow_id = flow_id
    source_mac = testutils.test_param_get("src_mac", "11:33:55:77:99:00")
    dest_mac = testutils.test_param_get("dst_mac", "00:11:22:33:44:55")

    def program_flow_watchlist_table(self):
        logger.info("Programming flow watchlist table for the test...")
        self.flow_watchlist.info.key_field_annotation_add(
            'hdr.ethernet.src_addr', 'mac')
        self.flow_watchlist.info.key_field_annotation_add(
            'hdr.ethernet.dst_addr', 'mac')
        key = self.flow_watchlist.make_key([
            gc.KeyTuple('hdr.ethernet.src_addr', self.source_mac),
            gc.KeyTuple('hdr.ethernet.dst_addr', self.dest_mac),
            gc.KeyTuple('hdr.vlan.vid', vlan_vid)])
        data = self.flow_watchlist.make_data(
            [gc.DataTuple('flow_id', flow_id)],
            "Ingress.ixp_ingr_head.flow_watchlist_ingress.set_flow_id")
        self.flow_watchlist.entry_add(self.dev_target, [key], [data])

    def program_mac_forward_table(self):
        logger.info("Programming mac forwarding table for the test...")
        self.mac_forward.info.key_field_annotation_add(
            'hdr.ethernet.dst_addr', 'mac')
        key = self.mac_forward.make_key([
            gc.KeyTuple('hdr.ethernet.dst_addr', self.dest_mac)])
        data = self.mac_forward.make_data(
            [gc.DataTuple('egress_port', egress_port)],
            "Ingress.ixp_ingr_tail.forward_frame.set_dest_port")
        self.mac_forward.entry_add(self.dev_target, [key], [data])

    def check_port_forwarding(self, pkt):
        logger.info("Checking if MAC forwarding rules present in switch")
        testutils.send_packet(self, ingress_port, pkt)
        testutils.verify_packets(self, pkt, [egress_port])

    def setUp(self):
        BfRuntimeTest.setUp(self, client_id=0, p4_name=program_name)
        logger.info("Test called with params %s", str(testutils.test_params_get()))
        self.dev_target = gc.Target(device_id=0)
        self.bfrt_info = self.interface.bfrt_info_get(program_name)
        self.flow_watchlist = self.bfrt_info.table_get(
            "Ingress.ixp_ingr_head.flow_watchlist_ingress.flow_watchlist")
        self.mac_forward = self.bfrt_info.table_get(
            "Ingress.ixp_ingr_tail.forward_frame.dest_mac")

    def tearDown(self):
        # Remove all table entries
        self.flow_watchlist.entry_del(self.dev_target, [])
        self.mac_forward.entry_del(self.dev_target, [])
        BfRuntimeTest.tearDown(self)
