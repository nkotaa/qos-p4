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
    flow_id = flow_id

    def _program_flow_watchlist_table(self):
        logger.info("Programming flow watchlist table for the test...")
        key = self.flow_watchlist.make_key([
            gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
            gc.KeyTuple('ig_tm_md.ucast_egress_port', egress_port),
            gc.KeyTuple('vid', vlan_vid)])
        data = self.flow_watchlist.make_data(
            [gc.DataTuple('flow_id', flow_id)],
            "Ingress.flow_watchlist_ingress.set_flow_id")
        self.flow_watchlist.entry_add(self.dev_target, [key], [data])

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
            "Ingress.flow_watchlist_ingress.flow_watchlist")
        self._program_flow_watchlist_table()

    def tearDown(self):
        # Remove all table entries
        self.flow_watchlist.entry_del(self.dev_target, [])
        BfRuntimeTest.tearDown(self)
