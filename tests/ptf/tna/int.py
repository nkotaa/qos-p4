import ptf.testutils as testutils
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import bfrt_grpc.client as gc
import p4testutils.misc_utils as misc_utils

from base_test import FlowTest

program_name = testutils.test_param_get("p4_name")
num_pkts = int(testutils.test_param_get("num_pkts", "1001"))
source_mac = testutils.test_param_get("src_mac", "11:33:55:77:99:00")
dest_mac = testutils.test_param_get("dst_mac", "00:11:22:33:44:55")
mirror_session_id = int(testutils.test_param_get("mirr_sesid", 13))

logger = misc_utils.get_logger()

class INTProgramTest(FlowTest):

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

    def _program_mirror_session_table(self):
        logger.info("Programming mirror session table for the test...")
        mirror_cfg_bfrt_data = self.mirror_cfg.make_data([
            gc.DataTuple('$direction', str_val="EGRESS"),
            gc.DataTuple('$ucast_egress_port', 68),
            gc.DataTuple('$ucast_egress_port_valid', bool_val=True),
            gc.DataTuple('$session_enable', bool_val=True),
            gc.DataTuple('$max_pkt_len', 1000),
            ], "$normal")
        self.mirror_cfg.entry_add(self.dev_target, [self.key5], [ mirror_cfg_bfrt_data ])

    def setUp(self):
        FlowTest.setUp(self)
        self.dev_target = gc.Target(device_id=0)
        self.bfrt_info = self.interface.bfrt_info_get(program_name)
        self.int_source = self.bfrt_info.table_get(
            "Ingress.int_source_ingress.int_source")
        self.sample_flow_count = self.bfrt_info.table_get(
            "Egress.int_event_egress.sample_flow_count")
        self.int_event_trigger = self.bfrt_info.table_get(
            "Egress.int_event_egress.int_event_trigger")
        self.mirror_cfg = self.bfrt_info.table_get("$mirror.cfg")
        self.key2 = self.int_source.make_key([
            gc.KeyTuple('flow_id', self.flow_id)])
        self.key3 = self.sample_flow_count.make_key([
            gc.KeyTuple('flow_id', self.flow_id)])
        self.key4 = self.int_event_trigger.make_key([
            gc.KeyTuple('is_sflow', True)])
        self.key5 = self.mirror_cfg.make_key([
            gc.KeyTuple('$sid', mirror_session_id)])

    # Remove all table entries
    def _clean_up(self):
        self.int_source.entry_del(self.dev_target, [])
        self.sample_flow_count.entry_del(self.dev_target, [])
        self.int_event_trigger.entry_del(self.dev_target, [])
        self.mirror_cfg.entry_del(self.dev_target, [])

    def tearDown(self):
        self._clean_up()
        FlowTest.tearDown(self)

class INTEventTest(INTProgramTest):

    def setUp(self):
        super().setUp()

    def runTest(self):
        pkt = testutils.simple_tcp_packet(eth_src=source_mac, eth_dst=dest_mac,
                                          dl_vlan_enable=True, vlan_vid=self.vlan_vid)
        super().check_port_forwarding(pkt)

        self._program_int_source_table()
        self._program_sample_flow_table()
        self._program_int_event_table()
        self._program_mirror_session_table()

        testutils.send_packet(self, self.ingress_port, pkt, count=num_pkts)
        testutils.verify_each_packet_on_each_port(self, [pkt] * num_pkts,
                                                  [self.egress_port] * num_pkts)

        logger.info("Receiving digest reports...")
        learn_filter = self.bfrt_info.learn_get("telem_digest")
        digest_list = list(self.interface.digest_get_iterator())
        for digest in digest_list:
            data_list = learn_filter.make_data_list(digest)
            for i in range(len(data_list)):
                data_dict = data_list[i].to_dict()
                print(data_dict)

    def tearDown(self):
        super().tearDown()
