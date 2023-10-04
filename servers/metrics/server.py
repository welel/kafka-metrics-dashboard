import logging
import socketserver
import threading

from pydantic import ValidationError
from servers.mixins import LengthBasedCommunicationMixin

from settings import METRICS_SERVER_REFRESH_METRICS_SEC

from .constants import ControlCommands
from .dashboard import DashboardMetrics
from .schemas import OffsetsMetrics, Response, ResponseStatus, Request


logger = logging.getLogger(__name__)


class MetricsSocketServer(socketserver.ThreadingTCPServer):
    """Management server for a ...

    Args:
        server_address (tuple[str, int]): The server address to start
            host[:port].

    Attributes:
        ...

    """
    dashboard = None

    def __init__(self, server_address):
        try:
            self.create_dashboard()
        except Exception as e:
            logger.error(
                "Error while initializing the dashboard: %s", e, exc_info=True
            )
        super().__init__(server_address, MetricsTCPHandler)

    def create_dashboard(self):
        """Creates and initialize the dashboard."""
        self.dashboard = DashboardMetrics()
        threading.Thread(
            target=self.dashboard.refresh,
            args=(METRICS_SERVER_REFRESH_METRICS_SEC,)
        ).start()


class MetricsTCPHandler(
        LengthBasedCommunicationMixin, socketserver.BaseRequestHandler
):
    """The handler class of `MetricsSocketServer`.

    """

    def _send_response(self, response):
        """Sends a response to the client.

        Args:
            response (dict): The data to send.
        """
        try:
            response = Response(**response)
        except ValidationError as e:
            response = Response(
                status=ResponseStatus.INVALID,
                data={"errors": e.errors()},
                message="Invalid response."
            )

        try:
            response = response.model_dump_json()
        except Exception as e:
            response = Response(
                status=ResponseStatus.ERROR,
                message=f"Unexpected error: {e}."
            ).model_dump_json()
        self.send(self.request, response.encode("utf-8"))

    def _get_request(self):
        """Receives a request from a client.

        Returns:
            dict: Response data.
        """
        raw_data = self.recv(self.request).strip()
        try:
            return Request.model_validate_json(raw_data)
        except ValidationError as e:
            self._send_response({
                    "status": ResponseStatus.INVALID,
                    "data": {"errors": e.errors()},
                    "message": "Invalid request.",
            })

    def setup(self):
        """Initializing all commands for processing."""
        self.commands = {
            ControlCommands.DASHBOARD: self.get_dashboard_data,
        }
        logger.debug("[%s]: Start handling.", self.client_address)

    def handle(self):
        """Handles the next message from a client.

        Processing of the received request. Checking which command is in
        the request, processing this command. At the end, sending a message
        to the addressee based on the result of processing.
        """
        request = self._get_request()
        if request is None:
            return
        try:
            command, data = request.command, request.data

            if command in self.commands:
                response = self.commands[command](data)
            else:
                response = {
                    "status": ResponseStatus.INVALID,
                    "message": f"A command {command} doesn't exist."
                }

        except Exception as e:
            logger.error("Unexpected Error `%s`", e, exc_info=True)
            response = {
                "status": ResponseStatus.ERROR,
                "message": "Server error."
            }
        self._send_response(response)

    def get_dashboard_data(self, *args):
        """Gets current dashboard data state.

        Returns:
            dict: The dashboard data.
        """
        if self.server.dashboard is None:
            return {
                "status": ResponseStatus.ERROR,
                "message": "The dashboard is unavailable."
            }

        return {
            "status": "ok",
            "data": OffsetsMetrics(
                **self.server.dashboard.get_state()
            ).model_dump(mode="json")
        }
