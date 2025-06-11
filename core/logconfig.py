import logging
import os
from logging.handlers import RotatingFileHandler
import tomllib  # Python 3.11 이상
from datetime import datetime
from pathlib import Path

def load_logging_config():
    config_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    return config.get("tool", {}).get("logging", {})

def config_logging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    cfg = load_logging_config()

    log_level = getattr(logging, cfg.get("log_level", "INFO").upper(), logging.INFO)
    log_format = cfg.get("log_format", "[{asctime}] [{levelname}] {name} - {message}")
    use_file = cfg.get("use_file_handler", True)
    use_stream = cfg.get("use_stream_handler", True)
    formatter = logging.Formatter(log_format, style="{")
    handlers = []

    if use_file:
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_file_name = f"app_{now_str}.log"
        log_file = cfg.get("log_file", default_file_name)
        log_dir = cfg.get("log_dir", "logs")
        os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, log_file),
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    if use_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

    logging.basicConfig(level=log_level, handlers=handlers)
    logging.info('start logging')

class log:
    def instrument(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cls_name = type(result).__name__
            if hasattr(result, "model_dump"):
                fields = ',\n    '.join(f"{k}={repr(v)}" for k, v in result.model_dump().items())
                msg = f"state = {cls_name}(\n    {fields}\n)"
                logging.info(msg)
            return result
        return wrapper
    
