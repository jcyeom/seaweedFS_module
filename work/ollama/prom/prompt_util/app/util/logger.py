import logging
import sys

def factory(name, level='DEBUG'):
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
            )
        )
        logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, level.upper()))
    
    return logger