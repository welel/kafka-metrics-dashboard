from statistics import mean

from .schemas import TopicStatus


async def offset_reports(offsets):
    """

    Returns:
        dict[str, ...]: A topic names and their report data.
    """
    offsets_dict = {}
    for offset in offsets:
        report = offsets_dict.setdefault(
            offset.name, {"first_processed": offset.processed}
        )

        if not report.get("requested"):
            report.update(
                processed=offset.processed,
                remaining=offset.remaining,
                total=offset.processed + offset.remaining,
                requested=offset.requested,
                load_speed=None,
                processing_speed=None,
                name=offset.name,
                label=offset.name,
            )
        elif report.get("load_speed") is None:
            time_gap = offset.requested - report["requested"]
            time_gap = time_gap.total_seconds()
            processed_for_gap = offset.processed - report["processed"]
            total = offset.processed + offset.remaining

            if time_gap == 0:
                load_speed = None
                processing_speed = None
            else:
                load_speed = (total - report["total"]) / time_gap
                processing_speed = processed_for_gap / time_gap

            report.update(
                processed=offset.processed,
                remaining=offset.remaining,
                requested=offset.requested,
                total=total,
                load_speed=load_speed,
                processing_speed=processing_speed,
            )
        else:
            time_gap = offset.requested - report["requested"]
            time_gap = time_gap.total_seconds()
            processed_for_gap = offset.processed - report["processed"]
            total = offset.processed + offset.remaining

            if time_gap == 0:
                load_speed = report["load_speed"]
                processing_speed = report["processing_speed"]
            else:
                load_speed = (total - report["total"]) / time_gap
                load_speed_avg = mean([load_speed, report["load_speed"]])
                processing_speed = processed_for_gap / time_gap
                processing_speed_avg = mean(
                    [processing_speed, report["processing_speed"]]
                )

            report.update(
                processed=offset.processed,
                remaining=offset.remaining,
                total=total,
                requested=offset.requested,
                load_speed=load_speed_avg,
                processing_speed=processing_speed_avg,
            )

            entry = report.setdefault("entry", 0)
            report["entry"] = entry + 1

    for offset in offsets_dict.values():
        first_processed = offset.pop("first_processed") != offset["processed"]
        if offset["remaining"] == 0:
            offset["status"] = TopicStatus.DONE
        elif first_processed != offset["processed"]:
            offset["status"] = TopicStatus.ACTIVE
        else:
            offset["status"] = TopicStatus.DEAD

        total = offset["processed"] + offset["remaining"]
        if total == 0:
            offset["processed_precent"] = 100
        else:
            offset["processed_precent"] = round(
                offset["processed"] / total * 100, 2
            )

        if (
                offset["load_speed"] is not None
                and offset["processing_speed"] is not None
        ):
            actual_processing_speed = (
                offset["processing_speed"] - offset["load_speed"]
            )
            if actual_processing_speed <= 0:
                if offset["remaining"] == 0:
                    offset["time_left"] = 0
                else:
                    offset["time_left"] = "inf"
            else:
                offset["time_left"] = (
                    offset["remaining"] / actual_processing_speed
                )
    return offsets_dict
