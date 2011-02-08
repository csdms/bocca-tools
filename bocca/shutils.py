#!/bin/env python2.6

from __future__ import print_function

import subprocess
from subprocess import PIPE

import os
import os.path
import sys
import shutil
import optparse
import tarfile
import tempfile
import types
import re

from commands import getstatusoutput
from bocca.verbose import Verbose

class Error (Exception):
  pass

class RunError (Error):
  def __init__ (self, status, stderr):
    self.status = status
    self.stderr = stderr

def is_sane (bocca_cmd, verbose=Verbose ()):
  (status, output) = getstatusoutput (bocca_cmd+ ' --version')
  verbose (2, output)
  return status == 0

def exists (bocca_obj, bocca='bocca', verbose=Verbose ()):
  (status, output) = getstatusoutput (' '.join ([bocca, 'whereis', bocca_obj]))
  verbose (2, output)
  return status == 0

def copy (src, dest, bocca='bocca', verbose=Verbose ()):
  cmd_str = ' '.join ([bocca, 'copy', src, dest])
  verbose (1, cmd_str)

  p = subprocess.Popen (cmd_str.split (), stdout=PIPE, stderr=PIPE)
  (stdout, stderr) = p.communicate ()
  status = p.returncode
  verbose (2, stdout)

  if status != 0:
    raise RunError (status, stderr)

  return status==0

def touch (obj, bocca='bocca', verbose=Verbose ()):
  cmd_str = ' '.join ([bocca, 'edit', '--touch', obj])
  verbose (1, cmd_str)

  p = subprocess.Popen (cmd_str.split (), stdout=PIPE, stderr=PIPE)
  (stdout, stderr) = p.communicate ()
  status = p.returncode
  verbose (2, stdout)

  if status != 0:
    raise RunError (status, stderr)

  return status==0

def impl_files (obj, bocca='bocca', verbose=Verbose ()):
  import shlex
  file = []

  command_line = ' '.join ([bocca, 'display', '--files', obj])
  verbose (1, command_line)

  args = shlex.split (command_line)
  p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  (stdout, stderr) = p.communicate ()
  status = p.returncode
  verbose (2, stdout)

  if status != 0:
    raise RunError (status, stderr)

  files = stdout.split ()

  return files

