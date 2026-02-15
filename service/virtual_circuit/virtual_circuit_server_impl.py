import logging
import grpc

from service.virtual_circuit import virtual_circuit_pb2
from service.virtual_circuit import virtual_circuit_pb2_grpc

logger = logging.getLogger(__name__)

class VirtualCircuitServicer(virtual_circuit_pb2_grpc.VirtualCircuitServicer):

    def __init__(self, intserv):
        self.intserv = intserv

    def SetUp(self, request, context):
        logger.info('Received SetUpRequest: ' + str(request) + ' from ' + context.peer())
        is_virtual_circuit_set_up = False
        try:
            self.intserv.set_guaranteed(request.flow_selector, request.bandwidth_kbps)
            is_virtual_circuit_set_up = True
        except RuntimeError as err:
            raise RuntimeError("Virtual circuit not set up")
        return virtual_circuit_pb2.SetUpResponse(
            is_success=is_virtual_circuit_set_up,
            )

    def TearDown(self, request, context):
        logger.info('Received TearDownRequest: ' + str(request) + ' from ' + context.peer())
        is_virtual_circuit_torn_down = False
        try:
            self.intserv.set_best_effort(request.flow_selector)
            is_virtual_circuit_torn_down = True
        except RuntimeError as err:
            raise RuntimeError("Virtual circuit not torn down")
        return virtual_circuit_pb2.TearDownResponse(
            is_success=is_virtual_circuit_torn_down,
            )
