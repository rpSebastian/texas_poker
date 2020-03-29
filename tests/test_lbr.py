import os
import sys
import random

os.chdir('..')
sys.path.append( os.path.join(os.getcwd()) )

from poker_server.eval.lbr import LocalBestResbonse

process = LocalBestResbonse(None)
process.start()