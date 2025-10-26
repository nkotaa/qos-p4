from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SetUpRequest(_message.Message):
    __slots__ = ("a_side_id", "b_side_id", "bandwidth_kbps")
    A_SIDE_ID_FIELD_NUMBER: _ClassVar[int]
    B_SIDE_ID_FIELD_NUMBER: _ClassVar[int]
    BANDWIDTH_KBPS_FIELD_NUMBER: _ClassVar[int]
    a_side_id: int
    b_side_id: int
    bandwidth_kbps: int
    def __init__(self, a_side_id: _Optional[int] = ..., b_side_id: _Optional[int] = ..., bandwidth_kbps: _Optional[int] = ...) -> None: ...

class SetUpResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class TearDownRequest(_message.Message):
    __slots__ = ("a_side_id", "b_side_id")
    A_SIDE_ID_FIELD_NUMBER: _ClassVar[int]
    B_SIDE_ID_FIELD_NUMBER: _ClassVar[int]
    a_side_id: int
    b_side_id: int
    def __init__(self, a_side_id: _Optional[int] = ..., b_side_id: _Optional[int] = ...) -> None: ...

class TearDownResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...
