#ifndef __IXP_CORE__
#define __IXP_CORE__

#include "ixp_types.p4"

control ingress_rate_limit_aclT<H>(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        in H hdr,
        out bit<3> drop_ctl);

control flow_watchlist_ingressT<H>(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        in H hdr,
        out flow_count_idx_t flow_id_res);

control forward_frameT<H>(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        in H hdr,
        out bit<3> drop_ctl,
        out DigestType_t digest_type);

control egress_rate_limit_aclT<H>(
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in egress_intrinsic_metadata_for_output_port_t eg_oport_md,
        in H hdr,
        out bit<3> drop_ctl);

control packet_sampleT<H, M>(
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in egress_intrinsic_metadata_for_output_port_t eg_oport_md,
        in H hdr,
        in M meta,
        out MirrorType_t mirror_type,
        inout ixp_egress_results_t ixp_eg_res);

control IXPIngressHead<H, M>(
        inout H hdr,
        inout M meta,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        out ixp_ingress_results_t ixp_ig_res)(
            ingress_rate_limit_aclT<H> limit_acl_ingress,
            flow_watchlist_ingressT<H> flow_watchlist_ingress)
{
    apply {
        limit_acl_ingress.apply(ig_intr_md, ig_prsr_md, ig_dprsr_md, ig_tm_md,
                hdr, ig_dprsr_md.drop_ctl);
        flow_watchlist_ingress.apply(ig_intr_md, ig_tm_md, hdr,
                ixp_ig_res.flow_id);
    }
}

control IXPIngressTail<H, M>(
        inout H hdr,
        inout M meta,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        out ixp_ingress_results_t ixp_ig_res)(
            forward_frameT<H> forward_frame)
{
    apply {
        forward_frame.apply(ig_intr_md, ig_dprsr_md, ig_tm_md, hdr,
                ig_dprsr_md.drop_ctl, ig_dprsr_md.digest_type);
    }
}

control IXPEgressHead<H, M>(
        inout H hdr,
        inout M meta,
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        inout egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        inout egress_intrinsic_metadata_for_output_port_t eg_oport_md,
        out ixp_egress_results_t ixp_eg_res)(
            egress_rate_limit_aclT<H> limit_acl_egress)
{
    apply {
        limit_acl_egress.apply(eg_intr_md, eg_prsr_md, eg_dprsr_md,
                eg_oport_md, hdr, eg_dprsr_md.drop_ctl);
    }
}

control IXPEgressTail<H, M>(
        inout H hdr,
        inout M meta,
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        inout egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        inout egress_intrinsic_metadata_for_output_port_t eg_oport_md,
        out ixp_egress_results_t ixp_eg_res)(
            packet_sampleT<H, M> packet_sample_egress)
{
    apply {
        packet_sample_egress.apply(eg_intr_md, eg_prsr_md, eg_dprsr_md,
                eg_oport_md, hdr, meta, eg_dprsr_md.mirror_type,
                ixp_eg_res);
    }
}

#endif /* __IXP_CORE__ */
