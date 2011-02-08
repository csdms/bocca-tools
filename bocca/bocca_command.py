from bocca_objects import *
from subprocess import Popen, PIPE

class Error (Exception):
  pass

class RunError (Error):
  def __init__ (self, status, stderr):
    self.status = status
    self.stderr = stderr

class BoccaOptionError (Error):
  def __init__ (self, option, msg):
    self._option = option
    self._msg = msg
  def __str__ (self):
    return '%s: %s' % (self._option, self._msg)

class ProjectExistsError (RunError):
  def __init__ (self, status, stderr):
    self.status = status
    self.stderr = stderr

def impl_import (obj, prefix=''):
  if obj.impl_dir () is not None:
    return '@'.join ([obj.full_name (), obj.impl_dir (prefix)])

def sidl_import (obj,prefix=''):
  if obj.sidl_file () is not None:
    return '@'.join ([obj.full_name (), obj.sidl_file (prefix)])

class BoccaHook (object):
  def run (self, obj):
    pass
  def __str__ (self, obj):
    return ''

def prepend_symbols (prefix, symbols):
  if symbols is not None:
    if isinstance (symbols, ListType):
      s = []
      for symbol in symbols:
        s.append (prefix+symbol)
    else:
      s = [prefix+symbols]
    return ' '.join (s)
  else:
    return ''

def prepend_symbol (prefix, symbol):
  s = prefix+symbol

def provide_opts (symbols):
  return prepend_symbols ('--provides=', symbols)
def uses_opts (symbols):
  return prepend_symbols ('--uses=', symbols)
def requires_opts (symbols):
  return prepend_symbols ('--requires=', symbols)
def package_opt (symbol):
  return prepend_symbol ('--package=', symbol)
def language_opt (symbol):
  return prepend_symbol ('--language=', symbol)
def implements_opt (symbol):
  return prepend_symbol ('--implements=', symbol)
def import_impl_opt (symbol):
  return prepend_symbol ('--import-impl=', symbol)
def import_sidl_opt (symbol):
  return prepend_symbol ('--import-sidl=', symbol)

#bocca_options = ['package', 'language', 'implements', 'uses', 'provides',
#                 'requires', 'extends', 'no-merge-buildfiles']

# All valid options for bocca
bocca_opts_all = set (['package', 'language', 'implements', 'uses', 'provides',
                       'requires', 'extends', 'no-merge-buildfiles',
                       'import-impl', 'import-sidl'])

# All valid options for bocca that require an argument
bocca_opts_arg = set (['package', 'language', 'implements', 'uses', 'provides',
                       'requires', 'extends', 'import-impl', 'import-sidl'])

# bocca options that import something
bocca_opts_import = set (['import-impl', 'import-sidl'])

def build_options (obj):
  s = []
  for option in obj.vars ():
    #if option not in import_opts:
    if option in bocca_opts_all-bocca_opts_import:
      val = obj.get_var (option)
      if option in bocca_opts_arg:
        if len (val)>0:
          s.append (prepend_symbols ('--'+option+'=', obj.get_var (option)))
      else:
        if len (val)>0:
          raise BoccaOptionError (option, 'Option does not take an argument')
        else:
          s.append ('--'+option)
  return ' '.join (s)

def import_options (obj, prefix=''):
  s = []
  if obj.impl_dir () is not None:
    if os.path.isdir (obj.impl_dir (prefix)):
      s.append (prepend_symbols ('--import-impl=', impl_import (obj, prefix)))
  if obj.sidl_file () is not None:
    if os.path.isfile (obj.sidl_file (prefix)):
      s.append (prepend_symbols ('--import-sidl=', sidl_import (obj, prefix)))
  return ' '.join (s)

class BoccaCommand (object):
  def __init__ (self, verb, obj, which_bocca='bocca', hook=BoccaHook (),
                      srcdir='', no_import=False):
    self._bocca = which_bocca
    self._verb = verb
    self._object = obj
    self._hook = hook
    self._srcdir = srcdir
    self._no_import = no_import

  def set_srcdir (self, srcdir):
    self._srcdir = srcdir

  def language_opt (self):
    obj = self._object
    if obj.language () is not None:
      return '--language=' + obj.language ()
    else:
      return ''

  def requires_opt (self):
    cmd = []
    for obj in self._object.requires ():
      cmd.append ('--requires=' + obj)
    return " ".join (cmd)

  def implements_opt (self):
    obj = self._object
    if obj.implements () is not None:
      return '--implements=' + obj.implements ()
    else:
      return ''

  def import_sidl_opt (self):
    obj = self._object
    if obj.sidl_file () is not None:
      return "--import-sidl=" + sidl_import (obj,self._srcdir)
    else:
      return ''

  def import_impl_opt (self):
    obj = self._object
    if obj.impl_dir () is not None:
      return "--import-impl=" + impl_import (obj,self._srcdir)
    else:
      return ''

  def package_opt (self):
    obj = self._object
    if obj.package () is not None:
      return "--package=" + obj.package ()
    else:
      return ''

  def uses_opt (self):
    cmd = []
    for obj in self._object.uses ():
      cmd.append ('--uses=' + obj)
    return " ".join (cmd)

  def provides_opt (self):
    cmd = []
    for obj in self._object.provides ():
      cmd.append ('--provides=' + obj)
    return " ".join (cmd)

  def create_cmd (self):
    obj = self._object
    if self._no_import:
      cmd = " ".join ([self._bocca, self._verb, obj.noun (), obj.full_name (),
                       build_options (obj)])
    else:
      cmd = " ".join ([self._bocca, self._verb, obj.noun (), obj.full_name (),
                       build_options (obj), import_options (obj,self._srcdir)])
    return cmd.strip ()

  def dry_run (self):
    from textwrap import TextWrapper
    wrapper = TextWrapper ()
    wrapper.subsequent_indent = '  '
    wrapper.break_long_words = False
    wrapper.break_on_hyphens = False
    wrapper.width = 78

    commands = ['# Create %s' % self._object.full_name (),
                self.create_cmd (), self._hook.__str__ (self._object)]
    for command in commands:
      command.strip ()
      if len (command)>0:
        print ' \\\n'.join (wrapper.wrap (command))
    print ''

    #for line in wrapper.wrap (self.create_cmd ()):
    #  print line
    #for line in wrapper.wrap (self._hook.__str__ (self._object)):
    #  print line
    #print self.create_cmd ()
    #print self._hook.__str__ (self._object)

  def run (self):
    cmd_str = self.create_cmd ()
    p = Popen (cmd_str.split (), stdout=PIPE, stderr=PIPE)
    p.wait ()
    status = p.poll ()
    (stdout, stderr) = p.communicate ()
    if status == 0:
      try:
        self._hook.run (self._object)
      except:
        status = 1
        raise
    else:
      raise RunError (status, stderr)
    return status==0

  def __str__ (self):
    return self.create_cmd ()

