import grpc

from service import virtual_circuit_pb2
from service import virtual_circuit_pb2_grpc

def set_up_virtual_circuit(intserv, a_side_interface,
                           b_side_interface, bandwidth_kbps):
    try:
        flow_selector = intserv.create_flow_selector(
            ingress_port=a_side_interface.port,
            source_vlanid=a_side_interface.vlan_id,
            egress_port=b_side_interface.port,
            dest_vlanid=b_side_interface.vlan_id,
            )
        intserv.set_guaranteed(flow_selector, bandwidth_kbps=bandwidth_kbps)
    except RuntimeError as err:
        raise RuntimeError("Virtual circuit not set up")

def tear_down_virtual_circuit(intserv, a_side_interface,
                              b_side_interface):
    try:
        flow_selector = intserv.create_flow_selector(
            ingress_port=a_side_interface.port,
            source_vlanid=a_side_interface.vlan_id,
            egress_port=b_side_interface.port,
            dest_vlanid=b_side_interface.vlan_id,
            )
        intserv.set_best_effort(flow_selector)
    except RuntimeError as err:
        raise RuntimeError("Virtual circuit not torn down")

class VirtualCircuitServicer(virtual_circuit_pb2_grpc.VirtualCircuitServicer):

    def __init__(self, intserv, get_virtual_interface):
        self.intserv = intserv
        self.get_virtual_interface = get_virtual_interface

    def SetUp(self, request, context):
        is_virtual_circuit_set_up = False
        try:
            a_side_interface = self.get_virtual_interface(member_id=request.a_side_id)
            b_side_interface = self.get_virtual_interface(member_id=request.b_side_id)
            set_up_virtual_circuit(self.intserv, a_side_interface,
                                   b_side_interface, request.bandwidth_kbps)
            is_virtual_circuit_set_up = True
        except RuntimeError as err:
            raise NotImplementedError
        return virtual_circuit_pb2.SetUpResponse(
            is_success=is_virtual_circuit_set_up,
            )

    def TearDown(self, request, context):
        is_virtual_circuit_torn_down = False
        try:
            a_side_interface = self.get_virtual_interface(member_id=request.a_side_id)
            b_side_interface = self.get_virtual_interface(member_id=request.b_side_id)
            tear_down_virtual_circuit(self.intserv, a_side_interface,
                                      b_side_interface)
            is_virtual_circuit_torn_down = True
        except RuntimeError as err:
            raise NotImplementedError
        return virtual_circuit_pb2.TearDownResponse(
            is_success=is_virtual_circuit_torn_down,
            )
