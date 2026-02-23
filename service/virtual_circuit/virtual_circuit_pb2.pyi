import service.flow_pb2 as _flow_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetUpRequest(_message.Message):
    __slots__ = ("flow_selector", "bandwidth_kbps")
    FLOW_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    BANDWIDTH_KBPS_FIELD_NUMBER: _ClassVar[int]
    flow_selector: _flow_pb2.Flow
    bandwidth_kbps: int
    def __init__(self, flow_selector: _Optional[_Union[_flow_pb2.Flow, _Mapping]] = ..., bandwidth_kbps: _Optional[int] = ...) -> None: ...

class SetUpResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class TearDownRequest(_message.Message):
    __slots__ = ("flow_selector",)
    FLOW_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    flow_selector: _flow_pb2.Flow
    def __init__(self, flow_selector: _Optional[_Union[_flow_pb2.Flow, _Mapping]] = ...) -> None: ...

class TearDownResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...
