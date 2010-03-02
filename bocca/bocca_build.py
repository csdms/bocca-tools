from __future__ import print_function
from bocca_command import *

pass_pre = "\x1B[00;32m"
pass_post = "\x1B[00m"

fail_pre = "\x1B[00;31m"
fail_post = "\x1B[00m"

hmmm_pre = "\x1B[00;33m"
hmmm_post = "\x1B[00m"

PASS = pass_pre + 'PASS' + pass_post
FAIL = fail_pre + 'FAIL' + fail_post
HMMM = hmmm_pre + '????' + hmmm_post

def print_status_desc (self, desc):
  max_len = 72 - len("[PASS]")
  status_str = desc[:max_len]
  status_str = status_str[:max_len]
  status_str += "."*(max_len - len(status_str))
  print (status_str, end='')
  sys.stdout.flush ()

def print_status_result (self, status):
  status_str = "["
  if status:
    status_str += pass_pre + "PASS" + pass_post
  else:
    status_str += fail_pre + "FAIL" + fail_post
  status_str += "]"
  print (status_str)

class BoccaCopyFile (BoccaHook):
  def __init__ (self, src, dest):
    self._src = src
    self._dest = dest

  def run (self, obj):
    srcdir = self._src
    dstdir = self._dest
    errors = []
    for file in obj.get_var ('extras'):
      try:
        src = os.path.join (obj.root_dir (srcdir), file)
        dst = os.path.join (obj.root_dir (dstdir), file)
        shutil.copyfile (src, dst)
        shutil.copystat (src, dst)
      except (IOError, os.error), why:
        errors.append((src, dst, str(why)))
      except OSError, why:
        errors.extend((src, dst, str(why)))
      except Error:
        errors.extend ((src, dst, 'Source and destination files are the same'))
      #except WindowsError:
      #  # can't copy file access times on Windows
      #  pass
    if errors:
      raise shutil.Error(errors)

  def __str__ (self, obj):
    srcdir = self._src
    destdir = self._dest
    s = ''
    for file in obj.get_var ('extras'):
      s = s + ' '.join(['cp', os.path.join (obj.root_dir (srcdir), file),
                              os.path.join (obj.root_dir (destdir), file)])
    return s

class BoccaBuild (object):
  def __init__ (self, project):
    self._name = project.name ()
    self._package = project.package ()
    self._language = project.language ()
    self._obj = project

    self._srcdir = os.path.abspath ('.')
    self._destdir = os.path.abspath (os.path.join ('.', self._name))

    self._nodes = []

  def name (self):
    return self._name

  def set_srcdir (self, src):
    self._srcdir = src
  def set_destdir (self, dest):
    self._destdir = dest

  def add_node (self, node):
    if node is None:
      print ('%s: Error adding node' % node.name ())
    else:
      node.prepend_name (self._package)
      self._nodes.append (node)

  def run (self):
    stat = StatusMessage ()
    cp = BoccaCopyFile (self._srcdir,self._destdir)

    try:
      stat.run ( ': '.join ([self._obj.noun (),self._obj.name ()]),
        BoccaCommand ('create', self._obj, hook=cp, srcdir=self._srcdir).run)
      os.chdir (self._name)
    except RunError as err:
      print ('Error %s: %s' % (err.status, err.stderr))
    except OSError:
      print ('%s: Unable to create project' % self._name)
    #except:
    #  print ('%s: Error running hook: %s' % (self._name,
    #                                         cp.__str__ (self._obj)))
    finally:
      try:
        for node in self._nodes:
          stat.run ( ': '.join ([node.noun (),node.name ()]),
            BoccaCommand ('create', node, hook=cp, srcdir=self._srcdir).run)
      except RunError as err:
        print ('Error %s: %s' % (err.status, err.stderr))
      except:
          raise

  def run_with_status (self, str, cmd):
    print_status_desc (str)
    status = self.run_command (cmd)
    print_status_result (status)

  def run_command (self, cmd):
    (status, output) = commands.getstatusoutput (cmd)
    #print (output)
    return status==0

  def dry_run (self):
    cp = BoccaCopyFile (self._srcdir,self._destdir)

    BoccaCommand ('create', self._obj, hook=cp, srcdir=self._srcdir).dry_run ()
    for node in self._nodes:
      BoccaCommand ('create', node, hook=cp, srcdir=self._srcdir).dry_run ()

  def __str__ (self):
    s = ''
    s = s + '%s: %s\n' % (self._obj.noun (), self._obj.full_name ())
    for node in self._nodes:
      s = s + ' |- %s: %s\n' % (node.noun (), node.full_name ())
    return s

class StatusMessage (object):
  def __init__ (self, result={0: FAIL,1: PASS}):
    self._result = result

  def run (self, message, command):
    self._message = message
    self.print_status ()
    try:
      result = command ()
    except (RunError, IOError, shutil.Error):
      self.print_result (0)
      raise
    else:
      self.print_result (result)

  def print_status (self):
    (cols, rows) = terminal_size ()
    max_len = cols - len("[PASS]")
    status_str = self._message[:max_len]
    status_str = status_str[:max_len]
    status_str += "."*(max_len - len(status_str))
    print (status_str, end='')
    sys.stdout.flush ()

  def print_result (self, status):
    if self._result.has_key (status):
      result_str = '[' + self._result[status] + ']'
    else:
      result_str = '[' + HMMM + ']'
    print (result_str)
    sys.stdout.flush ()

def ioctl_GWINSZ(fd): #### TABULATION FUNCTIONS
  try: ### Discover terminal width
    import fcntl, termios, struct, os
    cr = struct.unpack('hh',
    fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
  except:
    return None
  return cr

def terminal_size():
  ### decide on *some* terminal size
  # try open fds
  cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
  if not cr:
    # ...then ctty
    try:
      fd = os.open(os.ctermid(), os.O_RDONLY)
      cr = ioctl_GWINSZ(fd)
      os.close(fd)
    except:
      pass
    if not cr:
# env vars or finally defaults
      try:
        cr = (env['LINES'], env['COLUMNS'])
      except:
        cr = (25, 80)
# reverse rows, cols
  return int(cr[1]), int(cr[0])

