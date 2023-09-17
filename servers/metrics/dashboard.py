import math
import logging

from .helpers import (
    get_active_topic_names_for_sec,
    get_full_history_topic_offsets,
)
from .schemas import (
    OffsetMetrics,
    TopicStatus,
    LineGraph,
)


logger = logging.getLogger(__name__)


class ThinnedSequence(list):
    def __init__(self, seq, to=100):
        self.to = to
        self.extend(seq)

    def get_seq(self):
        out = []
        step = math.ceil(len(self) / self.to) or 1
        for i in range(0, len(self), step):
            out.append(self[i])
        return out


class DashboardMetrics:
    state = None
    history = None

    def __init__(self):
        self.state = {"metrics": {}}
        self.metrics = self.state["metrics"]
        self.history = {}

        # Get topic names that was collected within last 2 days.
        active_topics_names = get_active_topic_names_for_sec(
            2 * 24 * 60 * 60
        )

        for name in active_topics_names:
            offsets = self._init_topic_metrics(name)

            if offsets is None:
                print(name, "TODO: handle the error")
            else:
                self.metrics[name] = offsets
                return

    def _get_general_topic_info(self, offset):
        (
            processed, remaining, requested,
            gap_sec, prev_processed, prev_remaining
        ) = offset

        total = processed + remaining
        if prev_processed is None:
            prev_total = None
        else:
            prev_total = prev_processed + prev_remaining

        if total == 0:
            processed_percent = 100
        else:
            processed_percent = round(processed / total * 100, 2)

        if gap_sec is None or prev_total is None:
            current_load_speed = None
            current_processing_speed = None
        if gap_sec == 0:
            current_load_speed = total - prev_total
            current_processing_speed = processed - prev_processed
        else:
            current_load_speed = round((total - prev_total) / gap_sec, 2)
            current_processing_speed = round(
                (processed - prev_processed) / gap_sec, 2
            )

        if (
                current_load_speed is not None
                and current_processing_speed is not None
        ):
            actual_processing_speed = (
                current_processing_speed - current_load_speed
            )
            if actual_processing_speed <= 0:
                if remaining == 0:
                    time_left = 0
                else:
                    time_left = "inf"
            else:
                time_left = round(remaining / actual_processing_speed, 2)
        return {
            "total": total,
            "processed": processed,
            "queued": remaining,
            "processed_precent": processed_percent,
            "current_load_speed": current_load_speed,
            "current_processing_speed": current_processing_speed,
            "last_requested": requested,
            "time_left": time_left,
        }

    def _get_topic_status(self, total, processed, prev_processed):
        if total == processed:
            return TopicStatus.DONE
        elif prev_processed is not None and processed > prev_processed:
            return TopicStatus.ACTIVE
        elif prev_processed is not None and processed == prev_processed:
            return TopicStatus.DEAD
        else:
            return TopicStatus.ACTIVE

    def _get_tasks_graps(self, name):
        history = self.history.get(
            name, LineGraph(labels=[], lines={})
        ).get_seq()

        labels = []
        graph_lines = {
            "total": [], "processed": [], "queued": []
        }

        for offset in reversed(history):
            processed, remaining, requested = offset[:3]

            labels.append(requested.strftime("%m.%d %H:%M"))

            graph_lines["total"].append(processed + remaining)
            graph_lines["processed"].append(processed)
            graph_lines["queued"].append(remaining)
        return LineGraph(labels=labels, lines=graph_lines)

    def _init_topic_metrics(self, name):
        full_history = get_full_history_topic_offsets(name)

        if full_history is None:
            return

        info = self._get_general_topic_info(full_history[0])
        if len(full_history) > 1:
            status = self._get_topic_status(
                info["total"], info["processed"], full_history[1][0]
            )
        else:
            status = TopicStatus.ACTIVE

        self.history[name] = ThinnedSequence(full_history, to=40)
        tasks_grap_data = self._get_tasks_graps(name)

        return OffsetMetrics(
            name=name, **info, status=status,
            full_tasks_graphs=tasks_grap_data,
        )

    def get_state(self):
        return self.state
