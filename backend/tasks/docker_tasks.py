from docker import Client
from datetime import datetime
from time import mktime

from ..logger import getlogger
import logging
logger = getlogger()

from ..celery import app

@app.task(soft_time_limit=600)
def container_killer(ttl):
    cli = Client(base_url='unix://var/run/docker.sock')
    cs = cli.containers(all=True)
    for c in cs:
        n = int(mktime(datetime.now().timetuple()))
        if n - c["Created"] > ttl:
            try:
                cli.stop(c["Id"], timeout=300)
                cli.remove_container(c["Id"], force=True)
                logger.debug("Container removed: " + str(c["Id"]))
            except Exception as e:
                logger.debug("Failed: " + str(e))
                
if __name__ == '__main__':
    container_killer()
