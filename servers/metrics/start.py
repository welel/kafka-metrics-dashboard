import logging

import click

from settings import METRICS_SERVER_HOST, METRICS_SERVER_PORT

from .server import MetricsSocketServer


logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host", type=str, default=METRICS_SERVER_HOST,
    help="The host of the server."
)
@click.option(
    "--port", type=int, default=METRICS_SERVER_PORT,
    help="The port of the server."
)
def metrics_server(host, port):
    server = None
    try:
        logger.info(
            "Start the server initialization on (%s:%d)...", host, port
        )
        server = MetricsSocketServer((host, port))
        logger.info(
            "Start %s on %s:%d.", MetricsSocketServer.__name__, host, port
        )
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info(
            "Stop %s on %s:%d.", MetricsSocketServer.__name__, host, port
        )
    except Exception as e:
        logger.error(
            "Unexpectalbe stop %s on %s:%d with error: %s",
            MetricsSocketServer.__name__, host, port, e, exc_info=True
        )
    finally:
        if server is not None:
            server.shutdown()
