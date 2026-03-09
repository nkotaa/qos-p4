#ifndef __INT_HEADERS__
#define __INT_HEADERS__

#define TELEMETRY_FIELDS \
    @flexible PortId_t ingress_port; \
    @flexible bit<48> ingress_global_tstamp; \
    @flexible bit<32> rx_count; \
    @flexible PortId_t egress_port; \
    @flexible bit<19> enq_qdepth; \
    @flexible bit<2> enq_congest_stat; \
    @flexible bit<19> deq_qdepth; \
    @flexible bit<2> deq_congest_stat; \
    @flexible bit<8> app_pool_congest_stat; \
    @flexible bit<18> deq_timedelta

struct telem_md_ingr_t {
    flow_count_idx_t flow_id;
    PortId_t ingress_port;
    bit<48> ingress_mac_tstamp;
    bit<48> ingress_global_tstamp;
    bit<32> rx_count;
}

struct telem_digest_t {
    TELEMETRY_FIELDS;
}

header egr_port_mirror_h {
    header_type_t header_type;
    TELEMETRY_FIELDS;
}

header int_report_h {
    header_type_t header_type;
    bit<7> pad0;
    PortId_t ingress_port;
    bit<48> ingress_global_tstamp;
    bit<32> rx_count;
    bit<7> pad1;
    PortId_t egress_port;
    bit<5> pad2;
    bit<19> enq_qdepth;
    bit<6> pad3;
    bit<2> enq_congest_stat;
    bit<5> pad4;
    bit<19> deq_qdepth;
    bit<6> pad5;
    bit<2> deq_congest_stat;
    bit<8> app_pool_congest_stat;
    bit<6> pad6;
    bit<18> deq_timedelta;
}

#endif /* __INT_HEADERS__ */
