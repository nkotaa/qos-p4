import random

try:
    import bfrt_grpc.client as gc
except ImportError:
    import os
    import sys
    PYTHON3_VER = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
    SDE_PYTHON3 = os.path.join(os.getenv('SDE_INSTALL'), 'lib',
                               'python'+PYTHON3_VER, 'site-packages')
    sys.path.append(SDE_PYTHON3)
    sys.path.append(os.path.join(SDE_PYTHON3, 'tofino'))
    sys.path.append(os.path.join(SDE_PYTHON3, 'tofino', 'bfrt_grpc'))
    import bfrt_grpc.client as gc

class BFRuntimeSwitchConnection:

    def __init__(self, grpc_addr='localhost:50052', device_id=0,
                 program_name=None, address_prefix=None):
        bfrt_interface = gc.ClientInterface(
            grpc_addr=grpc_addr,
            client_id=random.randint(9, 65535),
            device_id=device_id,
            perform_subscribe=False,
            )
        self.dev_target = gc.Target(device_id)
        self.bfrt_info = bfrt_interface.bfrt_info_get(p4_name=program_name)
        self.program_name = self.bfrt_info.p4_name_get()
        self.address_prefix = address_prefix

    def _table_get(self, table_name):
        if self.address_prefix is None:
            return self.bfrt_info.table_get(table_name)
        return self.bfrt_info.table_get(self.address_prefix + '.' + table_name)

    def make_match(self, key_list):
        return [gc.KeyTuple(
            expr,
            value=match_kind.get("value"),
            mask=match_kind.get("mask"),
            prefix_len=match_kind.get("prefix_len"),
            low=match_kind.get("low"),
            high=match_kind.get("high"),
            is_valid=match_kind.get("is_valid")
            ) for (expr, match_kind) in key_list]

    def set_table_entries(self, table_name, match_list, action_list):
        table_object = self._table_get(table_name)
        table_key_list = [table_object.make_key(
            match) for match in match_list]
        table_action_list = [table_object.make_data(
            [gc.DataTuple(key, value) for key, value in action_data.items()],
            action_code
            ) for action_code, action_data in action_list]
        table_object.entry_add_or_mod(
            self.dev_target, table_key_list, table_action_list,
            p4_name=self.program_name)

    def remove_table_entries(self, table_name, match_list):
        table_object = self._table_get(table_name)
        table_key_list = [table_object.make_key(
            match) for match in match_list]
        try:
            table_object.entry_del(self.dev_target, table_key_list,
                                   p4_name=self.program_name)
        except gc.BfruntimeReadWriteRpcException as ex:
            if "Object not found" not in str(ex):
                raise(ex)
            print("Key already absent")

    def read_table_entries(self, table_name, match_list, from_hw=False,
                         action_list_filter=None):
        table_object = self._table_get(table_name)
        table_key_list = [table_object.make_key(
            match) for match in match_list]
        entry_list = [entry.to_dict() for entry, _ in table_object.entry_get(
            self.dev_target, table_key_list, flags={"from_hw": from_hw},
            required_data=action_list_filter,
            p4_name=self.program_name)]
        return entry_list
