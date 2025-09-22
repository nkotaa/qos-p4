import grpc

from service import virtual_circuit_pb2
from service import virtual_circuit_pb2_grpc

class VirtualCircuitServicer(virtual_circuit_pb2_grpc.VirtualCircuitServicer):

    def __init__(self, control_plane_interface):
        self.control_plane_interface = control_plane_interface

    def SetUp(self, request, context):
        is_virtual_circuit_set_up = False
        try:
            self.control_plane_interface.set_up_virtual_circuit(
                request.a_side_id,
                request.b_side_id,
                request.bandwidth_kbps,
                )
            is_virtual_circuit_set_up = True
        except RuntimeError as err:
            raise NotImplementedError
        return virtual_circuit_pb2.SetUpResponse(
            is_success=is_virtual_circuit_set_up,
            )

    def TearDown(self, request, context):
        is_virtual_circuit_torn_down = False
        try:
            self.control_plane_interface.tear_down_virtual_circuit(
                request.a_side_id,
                )
            is_virtual_circuit_torn_down = True
        except RuntimeError as err:
            raise NotImplementedError
        return virtual_circuit_pb2.TearDownResponse(
            is_success=is_virtual_circuit_torn_down,
            )
