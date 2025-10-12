import random
from dataclasses import dataclass

INGRESS_METER_TABLE_BFRUNTIME = "Ingress.flow_meters_ingress.execute_ig_meter"
EGRESS_METER_TABLE_BFRUNTIME = "Egress.flow_meters_egress.execute_eg_meter"

# From rfc1633: "flow" abstraction as a distinguishable stream of related
# datagrams that results from a single user activity and requires the same QoS.
@dataclass
class DataFlow:
    ingress_port: int = None
    source_vlanid: int = None
    egress_port: int = None
    dest_vlanid: int = None

class BFRuntimeIntServ:

    import bfrt_grpc.client as gc

    def __init__(self, device_id=0, program_name=None, pipe_name='pipe'):
        bfrt_interface = self.gc.ClientInterface(
            grpc_addr='localhost:50052',
            client_id=random.randint(9, 65535),
            device_id=device_id,
            perform_subscribe=False,
            )
        self.bfrt_info = bfrt_interface.bfrt_info_get(p4_name=program_name)
        self.program_name = self.bfrt_info.p4_name_get()
        self.dev_target = self.gc.Target(device_id)
        self.ingress_meter_table = self.bfrt_info.table_get(
            pipe_name + '.' + INGRESS_METER_TABLE_BFRUNTIME)
        self.egress_meter_table = self.bfrt_info.table_get(
            pipe_name + '.' + EGRESS_METER_TABLE_BFRUNTIME)

    def create_flow_selector(self, ingress_port=None, source_vlanid=None,
                             egress_port=None, dest_vlanid=None):
        flow = DataFlow(ingress_port, source_vlanid, egress_port, dest_vlanid)
        return flow

    def set_guaranteed(self, flow_selector, bandwidth_kbps):
        ingress_meter_table_keys = [self.ingress_meter_table.make_key([
            self.gc.KeyTuple('hdr.vlan.vid', flow_selector.source_vlanid),
            self.gc.KeyTuple('meta.pipe_id', pipe_id),
            self.gc.KeyTuple('ig_tm_md.ucast_egress_port',
                        flow_selector.egress_port),
            ]
            ) for pipe_id in range(2)]
        ingress_meter_table_data = self.ingress_meter_table.make_data([
            self.gc.DataTuple('$METER_SPEC_CIR_KBPS', 0),
            self.gc.DataTuple('$METER_SPEC_PIR_KBPS', 25000000),
            self.gc.DataTuple('$METER_SPEC_CBS_KBITS', 100000),
            self.gc.DataTuple('$METER_SPEC_PBS_KBITS', 1000000),
            ],
            'Ingress.flow_meters_ingress.invoke_flow_meter'
            )
        egress_meter_table_key = self.egress_meter_table.make_key([
            self.gc.KeyTuple('hdr.vlan.vid', flow_selector.source_vlanid),
            self.gc.KeyTuple('eg_intr_md.egress_port',
                             flow_selector.egress_port),
            ]
            )
        egress_meter_table_data = self.egress_meter_table.make_data([
            self.gc.DataTuple('$METER_SPEC_CIR_KBPS', bandwidth_kbps),
            self.gc.DataTuple('$METER_SPEC_PIR_KBPS', 25000000),
            self.gc.DataTuple('$METER_SPEC_CBS_KBITS', 100000),
            self.gc.DataTuple('$METER_SPEC_PBS_KBITS', 1000000),
            ],
            'Egress.flow_meters_egress.invoke_flow_meter'
            )

        self.ingress_meter_table.entry_add(
            self.dev_target, ingress_meter_table_keys,
            [ingress_meter_table_data, ingress_meter_table_data],
            p4_name = self.program_name)
        self.egress_meter_table.entry_add(
            self.dev_target, [egress_meter_table_key],
            [egress_meter_table_data], p4_name = self.program_name)

    def set_best_effort(self, flow_selector):
        ingress_meter_table_keys = [self.ingress_meter_table.make_key([
            self.gc.KeyTuple('hdr.vlan.vid', flow_selector.source_vlanid),
            self.gc.KeyTuple('meta.pipe_id', pipe_id),
            self.gc.KeyTuple('ig_tm_md.ucast_egress_port',
                        flow_selector.egress_port),
            ]
            ) for pipe_id in range(2)]
        egress_meter_table_key = self.egress_meter_table.make_key([
            self.gc.KeyTuple('hdr.vlan.vid', flow_selector.source_vlanid),
            self.gc.KeyTuple('eg_intr_md.egress_port',
                             flow_selector.egress_port),
            ]
            )
        self.ingress_meter_table.entry_del(
            self.dev_target, ingress_meter_table_keys,
            p4_name = self.program_name)
        self.egress_meter_table.entry_del(
            self.dev_target, [egress_meter_table_key],
            p4_name = self.program_name)
