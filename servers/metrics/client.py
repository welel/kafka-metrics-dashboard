import json
import logging
import socket

from .constants import ControlCommands
from .schemas import ResponseStatus


logger = logging.getLogger(__name__)


class MetricsClient:
    """A client for making requests to the metrics server.

    Attributes:
        host (str): A metric server host.
        port (int): A metric server port.
        timeout (int): A timeout for request to the server.
        buffer_size (int): A message buffer size.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.timeout = 3000
        self.buffer_size = 200000

    def get_dashboard_data(self) -> dict | None:
        """Gets general dashboard data from the metrics server via a socket.

        Returns:
            dict | None: Data if succeed, None otherwise.

        Raises:
            ConnectionError: A connection faild.
            json.decoder.JSONDecodeError: A response from the server isn't JSON
                serializable.
        """
        sock = None
        request = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            request = json.dumps({"command": ControlCommands.DASHBOARD})
            sock.sendall(request.encode("utf-8"))
            raw_data = sock.recv(self.buffer_size)

            raw_data = json.loads(raw_data)
            status = raw_data.get("status", ResponseStatus.ERROR)
            data = raw_data.get("data", "Missing data.")

            if status == ResponseStatus.OK:
                return data
            else:
                logger.error(
                    "Invalid response from the metrics server: %s", raw_data
                )
                return None

        except (ConnectionRefusedError, ConnectionError):
            logger.error(
                "No metrics server connection on (%s:%d).",
                self.host, self.port
            )
            raise
        except json.decoder.JSONDecodeError:
            logger.error("Json error.", exc_info=True)
            raise
        except Exception:
            logger.error(
                "Error requesting dashboard data. Metrics server address: "
                "(%s:%d). Request: %s.",
                self.host, self.port, request
            )
        finally:
            if sock:
                sock.close()
