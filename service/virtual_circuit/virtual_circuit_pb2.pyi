from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataFlow(_message.Message):
    __slots__ = ("ingress_port", "source_vlanid", "egress_port", "dest_vlanid")
    INGRESS_PORT_FIELD_NUMBER: _ClassVar[int]
    SOURCE_VLANID_FIELD_NUMBER: _ClassVar[int]
    EGRESS_PORT_FIELD_NUMBER: _ClassVar[int]
    DEST_VLANID_FIELD_NUMBER: _ClassVar[int]
    ingress_port: int
    source_vlanid: int
    egress_port: int
    dest_vlanid: int
    def __init__(self, ingress_port: _Optional[int] = ..., source_vlanid: _Optional[int] = ..., egress_port: _Optional[int] = ..., dest_vlanid: _Optional[int] = ...) -> None: ...

class SetUpRequest(_message.Message):
    __slots__ = ("flow_selector", "bandwidth_kbps")
    FLOW_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    BANDWIDTH_KBPS_FIELD_NUMBER: _ClassVar[int]
    flow_selector: DataFlow
    bandwidth_kbps: int
    def __init__(self, flow_selector: _Optional[_Union[DataFlow, _Mapping]] = ..., bandwidth_kbps: _Optional[int] = ...) -> None: ...

class SetUpResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class TearDownRequest(_message.Message):
    __slots__ = ("flow_selector",)
    FLOW_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    flow_selector: DataFlow
    def __init__(self, flow_selector: _Optional[_Union[DataFlow, _Mapping]] = ...) -> None: ...

class TearDownResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...
