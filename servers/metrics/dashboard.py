import math
import logging
import time
from datetime import timedelta

from settings import (
    METRICS_SERVER_TOTAL_GRAPH_POINTS as TOTAL_GRAPH_POINTS,
)

from .helpers import (
    floor_float,
    get_active_topic_names_for_sec,
    get_full_history_topic_offsets,
    get_offsets_from_timestamp,
)
from .schemas import (
    OffsetMetrics,
    TopicStatus,
    LineGraph,
    Totals,
)


logger = logging.getLogger(__name__)


class ThinnedHistory(list):
    """The list class that has methods for thinning down a sequence.

    Attributes:
        target_len (int): The target length to which the sequence should be
            thinned.

    """
    def __init__(self, seq: list, target_len: int = 100):
        self.to = target_len
        self.extend(seq)

    def get_seq(self) -> list:
        """Retrieves the thinned sequence based on the specified target length.

        Returns:
            list: A thinned version of the original sequence.
        """
        out = []
        step = math.ceil(len(self) / self.to) or 1
        for i in range(0, len(self), step):
            out.append(self[i])

        if len(out) >= self.to:
            out.pop(0)

        if out[0] != self[0]:
            out.insert(0, self[0])
        return out


class DashboardMetrics:
    """Class for collecting and managing dashboard metrics data.

    This class is responsible for collecting and managing metrics data for
    various Kafka topics in a dashboard. It provides methods for initializing,
    refreshing, and retrieving the metrics data.

    Attributes:
        state (dict | None): A dict containing metrics and totals data.
        history (dict | None): A dict containing historical data for each
            topic.

    """
    state = None
    history = None

    def __init__(self):
        self.state = {"metrics": {}, "totals": {}}
        self.history = {}

        # Get topic names that was collected within last 2 days.
        active_topics_names = get_active_topic_names_for_sec(
            2 * 24 * 60 * 60
        )

        for name in active_topics_names:
            self._init_topic_metrics(name)
        self._init_totals()

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
            processed_percent = floor_float(processed / total * 100, 2)

        current_load_speed, current_processing_speed = self._get_speeds(
                total, processed, prev_total, prev_processed, gap_sec
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
                time_left = float(
                    round(remaining / actual_processing_speed, 2)
                )

        if time_left == "inf":
            finishes = "inf"
        else:
            finishes = requested + timedelta(seconds=time_left)

        return {
            "total": total,
            "processed": processed,
            "queued": remaining,
            "processed_precent": processed_percent,
            "current_load_speed": current_load_speed,
            "current_processing_speed": current_processing_speed,
            "last_requested": requested,
            "time_left": time_left,
            "finishes": finishes,
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

    def _get_speeds(
            self,
            total: int,
            processed: int,
            prev_total: int | None,
            prev_processed: int | None,
            gap_sec: int | None,
    ) -> tuple[int | float | None, int | float | None]:
        """Gets current load and processing speeds.

        Args:
            total: Current total tasks.
            processed: Current processed tasks.
            prev_total: Total tasks in a previous record.
            prev_processed: Total processed tasks in a previous record.
            gap_sec: Time between current and previous record in seconds.

        Returns:
            A tuple - first is load speed, second is processing speed.
        """
        if gap_sec is None or prev_total is None:
            current_load_speed = None
            current_processing_speed = None
        elif gap_sec == 0:
            current_load_speed = total - prev_total
            current_processing_speed = processed - prev_processed
        else:
            current_load_speed = round((total - prev_total) / gap_sec, 2)
            current_processing_speed = round(
                (processed - prev_processed) / gap_sec, 2
            )
        return current_load_speed, current_processing_speed

    def _get_tasks_graps(self, name):
        history = self.history.get(name, [])
        if history:
            history = history.get_seq()

        labels = []
        graph_lines = {
            "total": [], "processed": [], "queued": []
        }

        for offset in history:
            processed, remaining, requested = offset[:3]

            labels.append(requested.strftime("%m.%d %H:%M"))

            graph_lines["total"].append(processed + remaining)
            graph_lines["processed"].append(processed)
            graph_lines["queued"].append(remaining)
        return LineGraph(labels=labels, lines=graph_lines)

    def _get_speed_graps(self, name):
        history = self.history.get(name, [])
        if history:
            history = history.get_seq()

        labels = []
        speed_lines = {"load_speed": [], "processing_speed": []}

        for offset in history:
            (
                processed, remaining, requested,
                gap_sec, prev_processed, prev_remaining
            ) = offset

            total = processed + remaining
            if prev_processed is None:
                prev_total = None
            else:
                prev_total = prev_processed + prev_remaining

            load_speed, processing_speed = self._get_speeds(
                total, processed, prev_total, prev_processed, gap_sec
            )

            labels.append(requested.strftime("%m.%d %H:%M"))
            speed_lines["load_speed"].append(load_speed or 0)
            speed_lines["processing_speed"].append(processing_speed or 0)
        return LineGraph(labels=labels, lines=speed_lines)

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

        self.history[name] = ThinnedHistory(
            reversed(full_history), target_len=TOTAL_GRAPH_POINTS
        )
        tasks_graph_data = self._get_tasks_graps(name)
        speeds_graph_data = self._get_speed_graps(name)

        if len(full_history) > 2:
            started = full_history[-2][2]
        else:
            started = info["last_requested"]

        self.state["metrics"][name] = OffsetMetrics(
            name=name,
            **info,
            status=status,
            started=started,
            full_tasks_graphs=tasks_graph_data,
            full_speeds_graphs=speeds_graph_data,
        )

    def _init_totals(self):
        totals = Totals()

        for data in self.state["metrics"].values():
            totals.total += data.total
            totals.processed += data.processed
            totals.queued += data.queued

            if data.status == TopicStatus.ACTIVE:
                totals.active += 1
            elif data.status == TopicStatus.DONE:
                totals.done += 1
            elif data.status == TopicStatus.DEAD:
                totals.dead += 1
        self.state["totals"] = totals

    def _refresh_topic(self, name):
        metrics = self.state["metrics"][name]
        new_offsets = get_offsets_from_timestamp(name, metrics.last_requested)

        if len(new_offsets) < 3:  # Not enough data for further processing.
            return

        new_offsets.pop()  # Last row can have NULLs.

        info = self._get_general_topic_info(new_offsets[0])
        status = self._get_topic_status(
            info["total"], info["processed"], new_offsets[1][0]
        )

        self.history[name].extend(reversed(new_offsets))
        tasks_graph_data = self._get_tasks_graps(name)
        speeds_graph_data = self._get_speed_graps(name)

        self.state["metrics"][name] = OffsetMetrics(
            name=name,
            **info,
            status=status,
            started=metrics.started,
            full_tasks_graphs=tasks_graph_data,
            full_speeds_graphs=speeds_graph_data,
        )

    def refresh(self, interval):
        while True:
            time.sleep(interval)
            for name in self.state["metrics"].keys():
                self._refresh_topic(name)
            self._init_totals()
            logger.info("Metrics updated.")

    def get_state(self):
        status_order = {
            TopicStatus.ACTIVE: 1, TopicStatus.DEAD: 2, TopicStatus.DONE: 3
        }
        self.state["metrics"] = dict(sorted(
            self.state["metrics"].items(),
            key=lambda x: (status_order[x[1].status], x[1].name),
        ))
        return self.state
