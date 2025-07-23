# logger.py

import logging

logger = logging.getLogger("rubika-api-bot")

# Remove any pre-existing handlers to ensure clean configuration
if logger.handlers:
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.setLevel(logging.NOTSET) 
ch.setLevel(logging.NOTSET) 


def debugging(is_debugging: bool):
    """
    Configures the logger's verbosity based on the debugging mode.
    This function should be called after importing logger.py in your main script.

    Args:
        is_debugging (bool): If True, sets log level to DEBUG. If False, sets to CRITICAL.
    """
    if is_debugging:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL) 
        ch.setLevel(logging.CRITICAL) 