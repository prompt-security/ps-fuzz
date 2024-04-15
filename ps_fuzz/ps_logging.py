import logging
from logging.handlers import RotatingFileHandler

LOG_FILE_PATH = "prompt_security_fuzzer.log"

def setup_logging(debug_level: int):
    # Set up logging with specific debug_level
    allowed_logging_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging_level = allowed_logging_levels[debug_level]

    # Create file handler with rotation
    file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=5)
    file_handler.setLevel(logging_level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s')
    file_handler.setFormatter(formatter)

    # Configure the root logger to use the file handler
    logging.basicConfig(level=logging_level, format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s', handlers=[file_handler])
