import os
import sys


os.chdir('../server')
sys.path.append( os.path.join(os.getcwd()) )

from logs import logger

logger.info("test {}", 1)