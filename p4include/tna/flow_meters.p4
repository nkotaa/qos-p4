#ifndef __FLOW_METERS__
#define __FLOW_METERS__

control flow_meters_ingress(
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        in flow_count_idx_t flow_id,
        out bit<2> packet_color,
        out QueueId_t qid)
{
    DirectMeter(MeterType_t.BYTES) flow_meters;

    action set_color() {
        packet_color = (bit<2>)flow_meters.execute();
    }

    table execute_ig_meter {
        key = {
            flow_id: exact;
        }
        actions = {
            set_color;
        }
        meters = flow_meters;
        size = FLOW_COUNT;
    }

    apply {
        qid = 0;
        if (ig_dprsr_md.drop_ctl == 1) {
            return;
        }
        packet_color = 1;
        if (execute_ig_meter.apply().miss) {
            return;
        }
        if (packet_color == 0) {
            qid = 1;
        }
    }
}

#endif /* __FLOW_METERS__ */
