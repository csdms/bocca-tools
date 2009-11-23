#! /bin/env python

"""
This is the BoccaCmd module

>>> b = BoccaCmd (".",package="my.package")
>>> b.full_name ("func")
'my.package.func'
>>> b.short_name ("my.package.func")
'func'
"""

import subprocess
import os
import sys
import shutil
import optparse
import tarfile
import commands
from types import *

pass_pre = "\x1B[00;32m"
pass_post = "\x1B[00m"

fail_pre = "\x1B[00;31m"
fail_post = "\x1B[00m"

class BoccaObject (object):
  def __init__ (self, name, package=[]):
    self._vars = {}
    self._vars['name'] = name
    self._vars['package'] = package
    self._vars['extras'] = []

  def name (self):
    name = self._vars['name']
    if isinstance (name, ListType):
      return name[0]
    else:
      return name
  def package (self):
    package = self._vars['package']
    if isinstance (package, ListType):
      if len (package)>0:
        return package[0]
      else:
        return None
    else:
      return package

  def vars (self):
    return self._vars.keys ()
  def has_var (self, var_name):
    return self._vars.has_key ()
  def add_var (self, var_name, var):
    if self._vars.has_key (var_name):
      self._vars[var_name].append (var)
    else:
      self._vars[var_name] = [var]
  def get_var (self, var_name):
    if self._vars.has_key (var_name):
      return self._vars[var_name]
    else:
      return None
  def set_var (self, var_name, var):
    self._vars[var_name] = var

  def full_name (self):
    if self.package () is not None:
      return ".".join ([self.package (), self.name ()])
    else:
      return self.name ()
  def prepend_name (self, prefix):
    self._vars['name'] = '.'.join ([prefix, self.name ()])

  def root_dir (self):
    return None
  def impl_dir (self):
    return None
  def sidl_file (self):
    return None

class BoccaProject (BoccaObject):
  def __init__ (self, name, package=None):
    self._vars = {}
    self._vars['name'] = name
    self._vars['package'] = package
    self._vars['language'] = []
    self._vars['extras'] = []

  def full_name (self):
    return self.name ()
  def language (self):
    return self.get_var ('language')
  def root_dir (self, prefix=''):
    return os.path.join (prefix, '.')
  def noun (self):
    return "project"

class BoccaInterface (BoccaObject):
  def __init__ (self, name, package=[]):
    self._vars = {}
    self._vars['name'] = name
    self._vars['package'] = package
    self._vars['requires'] = []
    self._vars['extends'] = []
    self._vars['extras'] = []

  def noun (self):
    return "interface"
  def root_dir (self, prefix=''):
    return os.path.join (prefix, "ports", "sidl")

  def sidl_file (self, prefix=""):
    name = self.full_name ()
    return os.path.join (self.root_dir (prefix), name+'.sidl')

class BoccaClass (BoccaObject):
  def __init__ (self, name, package=[]):
    self._vars = {}
    self._vars['name'] = name
    self._vars['package'] = package
    self._vars['language'] = []
    self._vars['requires'] = []
    self._vars['implements'] = []
    self._vars['extras'] = []

  def noun (self):
    return "class"
  def sidl_file (self, prefix=""):
    name = self.full_name ()
    return os.path.join (prefix, "components", "sidl", name+".sidl")
  def root_dir (self, prefix=""):
    return os.path.join (prefix, "components", self.full_name ())
  def impl_dir (self, prefix=""):
    return self.root_dir (prefix)

class BoccaComponent (BoccaClass):
  def __init__ (self, name, package=[]):
    self._vars = {}
    self._vars['name'] = name
    self._vars['package'] = package
    self._vars['language'] = []
    self._vars['implements'] = []
    self._vars['requires'] = []
    self._vars['uses'] = []
    self._vars['provides'] = []
    self._vars['extras'] = []

  def noun (self):
    return "component"

class BoccaPort (BoccaInterface):
  def noun (self):
    return "port"

class BoccaEnum (BoccaInterface):
  def noun (self):
    return "enum"

if __name__ == "__main__":
  import doctest
  doctest.testmod ()

