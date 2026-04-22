import ptf.testutils as testutils
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import bfrt_grpc.client as gc
import p4testutils.misc_utils as misc_utils

from base_test import FlowTest

program_name = testutils.test_param_get("p4_name")
num_pkts = int(testutils.test_param_get("num_pkts", "1001"))
mirror_session_id = int(testutils.test_param_get("mirr_sesid", 13))
mirror_type = int(testutils.test_param_get("mirr_type", 3))
sflow_freq = int(testutils.test_param_get("sflow_freq", "512"))

logger = misc_utils.get_logger()

EGR_PORT_MIRROR = 1

class SampleProgramTest(FlowTest):

    def _program_sample_flow_table(self):
        logger.info("Programming sample flow table for the test...")
        self.sample_flow_count.info.key_field_annotation_add(
            'hdr.ethernet.src_addr', 'mac')
        key = self.sample_flow_count.make_key([
            gc.KeyTuple('hdr.ethernet.src_addr', self.source_mac)])
        data = self.sample_flow_count.make_data(
            # separate flow_id from watchlist, use same value for convenience
            [gc.DataTuple('flow_id', self.flow_id)],
            "Egress.ixp_egr_tail.packet_sample_egress.trigger_sflow_count")
        self.sample_flow_count.entry_add(self.dev_target, [key], [data])

    def _program_sample_event_table(self):
        logger.info("Programming sample event table for the test...")
        key = self.sample_flow_event.make_key([
            gc.KeyTuple('flow_idx', self.flow_id),
            gc.KeyTuple('ixp_eg_res.sflow_count', value=0, mask=sflow_freq-1),
            gc.KeyTuple('eg_dprsr_md.drop_ctl', value=0, mask=0)])
        data = self.sample_flow_event.make_data(
            [], "Egress.ixp_egr_tail.packet_sample_egress.mirror_sample")
        self.sample_flow_event.entry_add(self.dev_target, [key], [data])

    def setUp(self):
        FlowTest.setUp(self)
        self.dev_target = gc.Target(device_id=0)
        self.bfrt_info = self.interface.bfrt_info_get(program_name)
        self.sample_flow_count = self.bfrt_info.table_get(
            "Egress.ixp_egr_tail.packet_sample_egress.sample_flow_count")
        self.sample_flow_event = self.bfrt_info.table_get(
            "Egress.ixp_egr_tail.packet_sample_egress.sample_flow_event")

    # Remove all table entries
    def _clean_up(self):
        self.sample_flow_count.entry_del(self.dev_target, [])
        self.sample_flow_event.entry_del(self.dev_target, [])

    def tearDown(self):
        self._clean_up()
        FlowTest.tearDown(self)

class INTEventTest(SampleProgramTest):

    def _program_sample_mirror_table(self):
        logger.info("Programming sample mirror table for the test...")
        key = self.sample_mirror.make_key([
            gc.KeyTuple('mirror_type', EGR_PORT_MIRROR)])
        data = self.sample_mirror.make_data(
            [gc.DataTuple('int_mirror_session', mirror_session_id)],
            "Egress.int_event_egress.mirror")
        self.sample_mirror.entry_add(self.dev_target, [key], [data])

    def _program_mirror_session_table(self):
        logger.info("Programming mirror session table for the test...")
        key = self.mirror_cfg.make_key([
            gc.KeyTuple('$sid', mirror_session_id)])
        mirror_cfg_bfrt_data = self.mirror_cfg.make_data([
            gc.DataTuple('$direction', str_val="EGRESS"),
            gc.DataTuple('$ucast_egress_port', 68),
            gc.DataTuple('$ucast_egress_port_valid', bool_val=True),
            gc.DataTuple('$session_enable', bool_val=True),
            gc.DataTuple('$max_pkt_len', 1000),
            ], "$normal")
        self.mirror_cfg.entry_add(self.dev_target, [key], [mirror_cfg_bfrt_data])

    def setUp(self):
        super().setUp()
        self.sample_mirror = self.bfrt_info.table_get(
            "Egress.int_event_egress.sample_mirror")
        self.mirror_cfg = self.bfrt_info.table_get("$mirror.cfg")

    def runTest(self):
        pkt = testutils.simple_tcp_packet(
            eth_src=self.source_mac, eth_dst=self.dest_mac,
            dl_vlan_enable=True, vlan_vid=self.vlan_vid)
        FlowTest.program_mac_forward_table(self)
        FlowTest.check_port_forwarding(self, pkt)

        FlowTest.program_flow_watchlist_table(self)
        self._program_sample_flow_table()
        self._program_sample_event_table()
        self._program_sample_mirror_table()
        self._program_mirror_session_table()

        logger.info("Sending packets...")
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
        self.sample_mirror.entry_del(self.dev_target, [])
        self.mirror_cfg.entry_del(self.dev_target, [])
        super().tearDown()
