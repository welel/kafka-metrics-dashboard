import json
import logging
import socket

from .constants import ControlCommands


logger = logging.getLogger(__name__)


class MetricsClient:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.timeout = 3000
        self.buffer_size = 20000

    def get_dashboard_data(self):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))

            request = json.dumps({"command": ControlCommands.DASHBOARD})
            sock.sendall(request.encode("utf-8"))
            raw_data = sock.recv(self.buffer_size)

            data = json.loads(raw_data)
            status = data.get("status", "error")
            data = data.get("data", "Missing data.")

            if status == "ok":
                return data
            else:
                return None

        except ConnectionError:
            logger.error("No Metrics Server connection.")
            raise
        except json.decoder.JSONDecodeError:
            logger.error("Json error.", exc_info=True)
            raise
        finally:
            if sock:
                sock.close()
