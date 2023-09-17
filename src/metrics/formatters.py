def format_graph_init_values(offsets):
    offsets_dict = {}
    for offset in offsets:
        offset_ = offsets_dict.setdefault(
            offset.name,
            {"name": offset.name,
             "total": [],
             "queued": [],
             "processed": [],
             "requested": [],
             "processed_precent": []}
        )
        offset_["total"].append(
            offset.processed + offset.remaining
        )
        offset_["queued"].append(offset.remaining)
        offset_["processed"].append(offset.processed)
        offset_["requested"].append(offset.requested)
        try:
            offset_["processed_precent"].append(
                round(offset_["processed"][-1] * 100 / offset_["total"][-1], 2)
            )
        except ZeroDivisionError:
            offset_["processed_precent"].append(100)
    return offsets_dict
