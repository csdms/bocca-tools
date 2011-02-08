"""
>>> d = {'quick':'slow', 'dog':'cat'}
>>> s = 'The quick brown fox jumps over the lazy dog.'

>>> t = Translate (d)
>>> t.string (s)
'The slow brown fox jumps over the lazy cat.'


Translate the longest string.  'dog' is replaced before 'do'.

>>> d = {'quick':'slow', 'dog':'cat', 'do':'groundho'}
>>> t = Translate (d)
>>> t.string (s)
'The slow brown fox jumps over the lazy cat.'


Dictionaries lack an order, so it shouldn't matter.

>>> d = {'quick':'slow', 'do':'groundho', 'dog':'cat'}
>>> t = Translate (d)
>>> t.string (s)
'The slow brown fox jumps over the lazy cat.'


Replacements don't have to be whole words.

>>> d = {'quick':'slow', 'do':'groundho'}
>>> t = Translate (d)
>>> t.string (s)
'The slow brown fox jumps over the lazy groundhog.'


Be careful with special characters.  They might have to be escaped.

>>> d = {'quick':'slow', 'do':'groundho', '\.':'!!!'}
>>> t = Translate (d)
>>> t.string (s)
'The slow brown fox jumps over the lazy groundhog!!!'

"""


import re
import fileinput
import types
import sys
import os.path

from verbose import Verbose

class Translate (object):
  def __init__ (self, dict):
    self._dict = dict
    self._keys = dict.keys ()
    self._keys.sort (lambda a, b: cmp (len (b), len (a)))

  def string (self, str):
    for key in self._keys:
      str = re.sub (key, self._dict[key], str)
    return str

  def files (self, files, verbose=Verbose ()):
    if type (files) in types.StringTypes:
      files = [files]

    f = fileinput.input (files, inplace=1)
    for line in f:
      if f.isfirstline ():
        verbose (1, 'Translating %s' % os.path.basename (f.filename ()))
      sys.stdout.write (self.string (line))
    f.close ()

if __name__ == "__main__":
    import doctest
    doctest.testmod()

