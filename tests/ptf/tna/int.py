import ptf.testutils as testutils
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import bfrt_grpc.client as gc
import p4testutils.misc_utils as misc_utils

program_name = testutils.test_param_get("p4_name")
pkt_len = int(testutils.test_param_get("pkt_len", "128"))
num_pkts = int(testutils.test_param_get("num_pkts", "1"))

sw_ports = misc_utils.get_sw_ports()
ingress_port = int(testutils.test_param_get("igr_port", sw_ports[1]))
egress_port = int(testutils.test_param_get("egr_port", sw_ports[2]))
vlan_vid = int(testutils.test_param_get("vlanid", 1))
source_mac = testutils.test_param_get("src_mac", "11:33:55:77:99:00")
dest_mac = testutils.test_param_get("dst_mac", "00:11:22:33:44:55")
mirror_session_id = int(testutils.test_param_get("mirr_sesid", 13))
flow_id = 60 # must be FLOW_COUNT_INDEX_WIDTH bits

logger = misc_utils.get_logger()
logger.info("Test called with params %s", str(testutils.test_params_get()))

class INTProgramTest(BfRuntimeTest):

    def _program_flow_watchlist_table(self):
        logger.info("Programming flow watchlist table for the test...")
        data1 = self.flow_watchlist.make_data(
            [gc.DataTuple('flow_id', flow_id)],
            "Ingress.flow_watchlist_ingress.set_flow_id")
        self.flow_watchlist.entry_add(self.dev_target, [self.key1], [data1])

    def _program_int_source_table(self):
        logger.info("Programming int source table for the test...")
        data2 = self.int_source.make_data(
            [], "Ingress.int_source_ingress.stage_metadata")
        self.int_source.entry_add(self.dev_target, [self.key2], [data2])

    def _program_sample_flow_table(self):
        logger.info("Programming sample flow table for the test...")
        data3 = self.sample_flow_count.make_data(
            [], "Egress.int_event_egress.trigger_sflow_count")
        self.sample_flow_count.entry_add(self.dev_target, [self.key3], [data3])

    def _program_int_event_table(self):
        logger.info("Programming int event table for the test...")
        data4 = self.int_event_trigger.make_data(
            [gc.DataTuple('int_mirror_session', mirror_session_id)],
            "Egress.int_event_egress.mirror")
        self.int_event_trigger.entry_add(self.dev_target, [self.key4], [data4])

    def setUp(self):
        BfRuntimeTest.setUp(self, client_id=0, p4_name=program_name)
        self.dev_target = gc.Target(device_id=0)
        self.bfrt_info = self.interface.bfrt_info_get(program_name)
        self.flow_watchlist = self.bfrt_info.table_get(
            "Ingress.flow_watchlist_ingress.flow_watchlist")
        self.int_source = self.bfrt_info.table_get(
            "Ingress.int_source_ingress.int_source")
        self.sample_flow_count = self.bfrt_info.table_get(
            "Egress.int_event_egress.sample_flow_count")
        self.int_event_trigger = self.bfrt_info.table_get(
            "Egress.int_event_egress.int_event_trigger")
        self.key1 = self.flow_watchlist.make_key([
            gc.KeyTuple('ig_intr_md.ingress_port', ingress_port),
            gc.KeyTuple('ig_tm_md.ucast_egress_port', egress_port),
            gc.KeyTuple('hdr.vlan.vid', vlan_vid)])
        self.key2 = self.int_source.make_key([
            gc.KeyTuple('flow_id', flow_id)])
        self.key3 = self.sample_flow_count.make_key([
            gc.KeyTuple('telem_md_ingr.flow_id', flow_id)])
        self.key4 = self.int_event_trigger.make_key([
            gc.KeyTuple('is_sflow', True)])

    # Remove all table entries
    def _clean_up(self):
        self.flow_watchlist.entry_del(self.dev_target, [])
        self.int_source.entry_del(self.dev_target, [])
        self.sample_flow_count.entry_del(self.dev_target, [])
        self.int_event_trigger.entry_del(self.dev_target, [])

    def tearDown(self):
        self._clean_up()
        BfRuntimeTest.tearDown(self)
