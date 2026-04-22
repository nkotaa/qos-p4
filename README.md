# IXP4

P4 framework for network services at internet exchange points, targeting Portable Switch Architecture on Intel Tofino.

## Repo Structure

The framework consists of a top level pipeline, where users provide their own forwarding logic in control interfaces, and type definitions to pass state.
A library of features is provided for use with data plane portion called in the user-instantiated pipeline, along with corresponding control plane APIs.

The [example program](./p4src/example/ixp_fabric.p4) demonstrates how the framework can be used to write an L2 exchange fabric using all library features.
The Packet Testing Framework (PTF) tests the feature library as well as our example program.
```
p4src/
├── example                 example application code
├── include                 data plane feature library
│   ├── flow_counters.p4    packet counters
│   └── flow_meters.p4      packet meters
├── ixp_core.p4             control interfaces
└── ixp_types.p4            framework data types
controller/
├── intserv.py              service APIs for flow_counters.p4
├── monitor.py              service APIs for flow_meters.p4
└── switch_connection.py    hardware driver for table CRUD operations
tests/ptf/tna
├── base_test.py            base class to setup flow watchlist and port forwarding tables
├── counters.py             counter library tests
└── int.py                  packet sampling tests
```
