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

def _match_to_keytuple(match):
    return [gc.KeyTuple(key, value) for key, value in match.items()]

class BFRuntimeSwitchConnection:

    def __init__(self, grpc_addr='localhost:50052', device_id=0,
                 program_name=None, pipe_name='pipe'):
        bfrt_interface = gc.ClientInterface(
            grpc_addr=grpc_addr,
            client_id=random.randint(9, 65535),
            device_id=device_id,
            perform_subscribe=False,
            )
        self.dev_target = gc.Target(device_id)
        self.bfrt_info = bfrt_interface.bfrt_info_get(p4_name=program_name)
        self.program_name = self.bfrt_info.p4_name_get()
        self.pipe_name = pipe_name

    def _table_get(self, table_name):
        return self.bfrt_info.table_get(self.pipe_name + '.' + table_name)

    def insert_table_entry(self, table_name, match_list, action_list):
        table_object = self._table_get(table_name)
        table_key_list = [table_object.make_key(
            _match_to_keytuple(match)) for match in match_list]
        table_action_list = [table_object.make_data(
            [gc.DataTuple(key, value) for key, value in action_data.items()],
            action_code
            ) for action_code, action_data in action_list]
        table_object.entry_add(self.dev_target, table_key_list,
                               table_action_list, p4_name=self.program_name)

    def remove_table_entry(self, table_name, match_list):
        table_object = self._table_get(table_name)
        table_key_list = [table_object.make_key(
            _match_to_keytuple(match)) for match in match_list]
        table_object.entry_del(self.dev_target, table_key_list,
                               p4_name=self.program_name)
