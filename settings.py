import configparser
import logging.config
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv


# Parse a `.env` file and load the variables into environment valriables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
LOGGING_CONFIG = os.path.join(BASE_DIR, "logging.yml")
CONFIG = os.path.join(BASE_DIR, "dev.conf")

# Logger config read
if os.path.isfile(LOGGING_CONFIG) and os.access(LOGGING_CONFIG, os.R_OK):
    _lc_stream = open(LOGGING_CONFIG, 'r')
    _lc_conf = yaml.load(_lc_stream, Loader=yaml.FullLoader)
    _lc_stream.close()
    logging.config.dictConfig(_lc_conf)
else:
    print(
        "ERROR: logger config file '%s' not eixsts or not readable\n" %
        LOGGING_CONFIG
    )
    sys.exit(1)

# Server config read
if os.path.isfile(CONFIG) and os.access(CONFIG, os.R_OK):
    _config = configparser.SafeConfigParser()
    _config.read(CONFIG)
else:
    print(
        "ERROR: application config file '%s' not eixsts or not readable\n" %
        CONFIG
    )
    sys.exit(1)

TIMEZONE = os.getenv("TZ", "Europe/Moscow")

# Database
DB_USER = os.getenv("POSTGRES_USER")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PATH = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if not all((DB_USER, DB_NAME, DB_PASSWORD, DB_HOST, DB_PORT)):
    print(
        f"Bad db config: {DB_USER=} {DB_NAME=} {DB_PASSWORD=} {DB_HOST=} "
        f"{DB_PORT=}."
    )
    sys.exit(1)

TEMPLATES_PATH = os.path.join(BASE_DIR, "templates")

# Metrics Server
METRICS_SERVER_HOST = (
    os.getenv("METRICS_SERVER_HOST") or _config.get("metrics_server", "host")
)
METRICS_SERVER_PORT = _config.getint("metrics_server", "port")
METRICS_SERVER_REFRESH_METRICS_SEC = _config.getint(
    "metrics_server", "refresh_metrics_sec", fallback=10
)
METRICS_SERVER_TOTAL_GRAPH_POINTS = _config.getint(
    "metrics_server", "total_graph_points", fallback=40
)

API_BASE_URL = os.getenv("API_BASE_URL")
