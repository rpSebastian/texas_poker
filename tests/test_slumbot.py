import os
import sys
os.chdir('..')
sys.path.append( os.path.join(os.getcwd()) )

from poker_server.kernel.slumbotkernel import SlumbotKernel

kernel = SlumbotKernel("1", " 2")
kernel.start()