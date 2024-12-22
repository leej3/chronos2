import sys
import logging
from chronos.config import cfg
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
logging.getLogger("socketIO-client").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("pymodbus").setLevel(logging.ERROR)
log_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S")
root_logger = logging.getLogger()


def ensure_log_path(path: Path):
    candidates = [
        path,
        Path.cwd() / path.name,
        Path("/tmp") / path.name
    ]
    for p in candidates:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            # Test writing the file to ensure we have permission
            with p.open('a'):
                pass
            return p
        except Exception as e:
            print(f"Warning:log file won't work at {p}: {e}")

    # If all fail, exit or raise an exception
    print("Could not create a suitable log file path.")
    sys.exit(1)




# Ensure the log path and use the returned path
final_log_path = ensure_log_path(Path(cfg.files.log_path))

root_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
rotate_logs_handler = TimedRotatingFileHandler(final_log_path, when="midnight", backupCount=3)
rotate_logs_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)
root_logger.addHandler(rotate_logs_handler)
