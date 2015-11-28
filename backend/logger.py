from logging import getLogger, DEBUG, INFO, NullHandler, StreamHandler, Formatter

def getlogger(loglevel=DEBUG, handler=NullHandler()):
    logger = getLogger(__name__)
    logger.setLevel(loglevel)
    ch = handler
    #ch = StreamHandler()
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    #logger.addHandler(ch)
    return logger

