import os
from xml.etree import ElementTree, ElementInclude

from bocca_xml import BoccaProject
from bocca_xml import bocca_object_names
from bocca_objects import new_object
from bocca_build import BoccaBuild

class Error (Exception):
  """Base class for exceptions in this module"""
  pass

import types

class UnexpectedElementError (Error):
  """Exception raised for an unexpected element"""
  def __init__ (self, expected, found):
    if type (expected) in types.StringTypes:
      self.msg = 'Expected %s but found %s' % (expected, found)
    else:
      expected = ', '.join (expected)
      self.msg = 'Expected one of %s but found %s' % (expected, found)

    self.expected = expected
    self.found = found

  def __str__ (self):
    return self.msg

class MissingElementError (Error):
  """Exception raised for a missing element that is required"""
  def __init__ (self, missing):
    self.msg = 'Missing element %s' % missing
    self.missing = missing

  def __str__ (self):
    return self.msg

class MissingAttributeError (Error):
  """Exception raised for a missing attribute that is required"""
  def __init__ (self, attrib):
    self.attrib = attrib
    self.msg = 'Missing required attribute %s' % attrib
  def __str__ (self):
    return self.msg

def project_from_element (element):
  if element.tag != 'project':
    raise UnexpectedElementError ('project', element.tag)

  if not element.attrib.has_key ('package'):
    element.attrib['package'] = None

  try:
    proj = BoccaProject (element.attrib['name'], element.attrib['package'])
  except KeyError as e:
    raise MissingAttributeError (e)

  for key in element.attrib.keys ():
    if key not in ['name', 'package']:
      proj.set_var (key, element.attrib[key])

  opts = {}
  for child in element.getchildren ():
    if child.tag in proj.valid_options ():
      if opts.has_key (child.tag):
        opts[child.tag].append (child.text)
      else:
        opts[child.tag] = [child.text]
  for (key, value) in opts.items ():
    proj.set_var (key, value)
      
  return proj

def object_from_element (element):
  if element.tag not in bocca_object_names:
    raise UnexpectedElementError (bocca_object_names, element.tag)

  try:
    obj = new_object (element.attrib['name'], element.tag)
  except KeyError as e:
    raise AttributError (e)
  except ObjectTypeError as e:
    raise

  for key in element.attrib.keys ():
    if key not in ['name']:
      obj.set_var (key, element.attrib[key])

  #for child in element.getchildren ():
  #  if child.tag in obj.valid_options ():
  #    obj.set_var (child.tag, child.text)

  opts = {}
  for child in element.getchildren ():
    if child.tag in obj.valid_options ():
      if opts.has_key (child.tag):
        opts[child.tag].append (child.text)
      else:
        opts[child.tag] = [child.text]
  for (key, value) in opts.items ():
    obj.set_var (key, value)

  return obj

  #vars = get_node_vars (node)

  #obj = objects[node.nodeName] (vars['name'])
  #for var_name in vars.keys ():
  #  obj.set_var (var_name, vars[var_name])

  #return obj

def parse_file (file, srcdir='.', dstdir='.', no_import=False):
  try:
    doc = ElementTree.parse (file)
  except IOError as e:
    raise
    #raise BadFileError (file, e.strerror)

  proj = doc.getroot ()

  if proj.tag != 'project':
    raise MissingElementError ('project')

  #print 'bocca create project %(name)s --language=%(language)s --package=%(package)s' % proj.attrib

  #for obj in get_bocca_objects (proj):
  #  obj.attrib['tag'] = obj.tag
  #  command_string = 'bocca create %(tag)s %(name)s' % obj.attrib
  #  for child in obj.getchildren ():
  #    command_string += ' --%s=%s' % (child.tag, child.text)
  #  print command_string

  build = BoccaBuild (project_from_element (proj), no_import=no_import)
  build.set_srcdir (os.path.abspath (srcdir))
  build.set_destdir (os.path.abspath (os.path.join (dstdir, build.name ())))

  #for node in proj.getchildren ():
  for node in get_bocca_objects (proj):
    build.add_node (object_from_element (node))

  return build

def get_bocca_objects (element):
  objs = []
  ElementInclude.include (element)
  for child in element.getchildren ():
    if child.tag == 'project':
      objs.extend (get_bocca_objects (child))
    elif child.tag in bocca_object_names:
      objs.append (child)
  return remove_dups (objs)

def remove_dups (objs, idfun=None):
  if idfun is None:
    def idfun (x): return x.attrib['name']
  seen = {}
  result = []
  for item in objs:
    marker = idfun (item)
    if marker in seen:
      continue
    seen[marker] = 1
    result.append (item)
  return result

