'''
>>> import sys

>>> verbose = Verbose (log=sys.stdout)
>>> verbose (0, 'Level 0')
Level 0
>>> verbose (1, 'Level 1')

>>> verbose = Verbose (1, sys.stdout)
>>> verbose (0, 'Level 0')
Level 0
>>> verbose (1, 'Level 1')
Level 1
'''

from __future__ import print_function

import sys
import types

class Verbose (object):
  def __init__ (self, verbosity=0, log=sys.stderr):
    if isinstance (verbosity,types.BooleanType):
      if verbosity is True:
        self._verbosity = sys.maxint
      else:
        self._verbosity = 0
    else:    
      self._verbosity = verbosity
    self._log = log
  def __call__(self, verbosity, msg):
    if verbosity <= self._verbosity:
      print (msg, file=self._log)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

