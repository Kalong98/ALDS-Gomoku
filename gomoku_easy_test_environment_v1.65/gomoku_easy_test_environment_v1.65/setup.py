from distutils.core import setup # Need this to handle modules
import py2exe 
import math # We have to import all modules used in our program

import sys
sys.setrecursionlimit(5000)
#import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

setup(console=['gomoku_easy_test_environment.py']) # Calls setup function to indicate that we're dealing with a single console application

#setup(windows=['gomoku_easy_test_environment.py']) # Calls setup function to indicate that we're dealing with a single console application