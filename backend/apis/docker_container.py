import os, sys
from docker import Client

import logging
from ..logger import getlogger
#logger = getlogger(logging.DEBUG, logging.StreamHandler())
logger = getlogger()
    
appdir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

def contra_container(cli):
    cli = Client(base_url='unix://var/run/docker.sock')
    cid = None
    if cli:
        container = cli.create_container(
        image="contra:latest",
        #name="contra",
        user="contra",
        working_dir="/home/contra/files",
        #command="/usr/bin/run.sh",
        stdin_open=True,
        tty=True,
        volumes=['/home/contra/artifacts'],
        host_config=cli.create_host_config(
            binds={
                appdir + '/static/artifacts': {
                        'bind': '/home/contra/artifacts',
                        'mode': 'rw',
                    },
            },
            privileged=True,
            ),
        )
        cid = container.get('Id')

    return cid

