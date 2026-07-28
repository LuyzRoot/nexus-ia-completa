import logging
from logging.handlers import RotatingFileHandler
import os
from config.paths import ROOT

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

def configure_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    fh = RotatingFileHandler(LOG_DIR / "nexus.log", maxBytes=10_000_000, backupCount=5)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)
