import logging, os, psutil, time
from configparser import ConfigParser
import subprocess
import qemu.qmp as qmp
from libs.console import QEMUConsole

# Establish logging
from libs.logger import logger
logger = logger.getChild('backup')



class QEMUBackup(QEMUConsole):

    def __init__(self) -> None:
        super().__init__()

