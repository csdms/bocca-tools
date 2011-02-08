import os
import commands

import xml.dom.minidom

from bocca_command import *
from bocca_objects import *
from bocca_build import *

document = """\
<project>
  <name>csdms</name>
  <language>java</language>
  <package>edu.csdms</package>
  <extras>make.vars.user</extras>

  <interface>
    <name>openmi.ITime</name>
    <imports>sidl</imports>
  </interface>
  <interface>
    <name>openmi.ITimeStamp</name>
    <imports>sidl</imports>
  </interface>
  <interface>
    <name>openmi.ITimeSpan</name>
    <imports>sidl</imports>
    <requires>openmi.ITimeStamp</requires>
  </interface>
  <interface>
    <name>openmi.ISpatialReference</name>
    <imports>sidl</imports>
  </interface>
  <enum>
    <name>openmi.ElementType</name>
    <imports>sidl</imports>
  </enum>
  <interface>
    <name>openmi.IValueSet</name>
    <imports>sidl</imports>
  </interface>
  <interface>
    <name>openmi.IScalarSet</name>
    <extends>IValueSet</extends>
    <imports>sidl</imports>
  </interface>
  <interface>
    <name>openmi.IVector</name>
    <imports>sidl</imports>
  </interface>
  <interface>
    <name>openmi.IVectorSet</name>
    <requires>IValueSet</requires>
    <requires>IVector</requires>
    <extends>IValueSet</extends>
    <imports>sidl</imports>
  </interface>
  <interface>
    <name>openmi.IElementSet</name>
    <requires>ISpatialReference</requires>
    <requires>ElementType</requires>
    <imports>sidl</imports>
  </interface>

  <class>
    <name>openmi.Time</name>
    <language>java</language>
    <implements>ITime</implements>
  </class>
  <class>
    <name>openmi.TimeStamp</name>
    <language>java</language>
    <implements>ITimeStamp</implements>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.TimeSpan</name>
    <language>java</language>
    <implements>ITimeSpan</implements>
    <requires>TimeStamp</requires>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.SpatialReference</name>
    <language>java</language>
    <implements>ISpatialReference</implements>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.ValueSet</name>
    <language>java</language>
    <implements>IValueSet</implements>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.ScalarSet</name>
    <language>java</language>
    <implements>IScalarSet</implements>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.Vector</name>
    <language>java</language>
    <implements>IVector</implements>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.VectorSet</name>
    <language>java</language>
    <implements>IVectorSet</implements>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.Vertex</name>
    <language>java</language>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.Element</name>
    <language>java</language>
    <requires>Vertex</requires>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.ElementSet</name>
    <language>java</language>
    <implements>IElementSet</implements>
    <requires>ISpatialReference</requires>
    <requires>SpatialReference</requires>
    <requires>Element</requires>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>
  <class>
    <name>openmi.ElementMapper</name>
    <language>java</language>
    <requires>Element</requires>
    <requires>ElementSet</requires>
    <requires>ScalarSet</requires>
    <requires>IScalarSet</requires>
    <requires>IValueSet</requires>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </class>

  <component>
    <name>openmi.OpenMITestC</name>
    <language>c</language>
    <provides>gov.cca.ports.GoPort@Start</provides>
    <requires>TimeStamp</requires>
    <requires>TimeSpan</requires>
    <requires>Vector</requires>
    <requires>IScalarSet</requires>
    <requires>ScalarSet</requires>
    <requires>IValueSet</requires>
    <requires>ValueSet</requires>
    <requires>Vertex</requires>
    <requires>VectorSet</requires>
    <requires>Element</requires>
    <requires>ElementSet</requires>
    <requires>ElementMapper</requires>
    <requires>ElementType</requires>
    <imports>sidl</imports>
    <imports>impl</imports>
    <extras>make.vars.user</extras>
  </component>

  <port>
    <name>ports.grid</name>
    <imports>sidl</imports>
  </port>
  <port>
    <name>ports.IRFPort</name>
    <requires>IElementSet</requires>
    <requires>IValueSet</requires>
    <requires>ElementType</requires>
    <requires>ISpatialReference</requires>
    <imports>sidl</imports>
  </port>
  <port>
    <name>ports.PrinterPort</name>
    <imports>sidl</imports>
  </port>
</project>
"""

class Error (Exception):
  """Base class for exceptions in this module"""
  pass

class BadFileError (Error):
  """Exception raised for error in input files"""
  def __init__ (self, file, msg):
    self.file = file
    self.msg = msg

class ParseError (Error):
  """Exception raised if an input file has trouble parsing"""
  def __init__ (self, file, msg):
    self.file = file
    self.msg = msg

def parse_project_node (node):
  vars = get_node_vars (node)

  if node.nodeName != 'project':
    print 'Error: this is not a project node'

  proj = BoccaProject (vars['name'], vars['package'])
  for var_name in vars.keys ():
    proj.set_var (var_name, vars[var_name])

  return proj

objects = { 'interface': BoccaInterface,
            'enum': BoccaEnum,
            'port': BoccaPort,
            'class': BoccaClass,
            'component': BoccaComponent,
            'project': BoccaProject}

def parse_object_node (node):
  vars = get_node_vars (node)

  #if not vars.has_key ('language'):
  #  vars['language'] = get_node_var (node.parentNode, 'language',
  #                                   is_unique=True)

  obj = objects[node.nodeName] (vars['name'])
  for var_name in vars.keys ():
    obj.set_var (var_name, vars[var_name])
  return obj

class BoccaNode (object):
  def __init__ (self, node):
    self._name = get_node_var (node, 'name', is_unique=True)
    self._package = get_node_var (node, 'package', is_unique=True)
    self._language = get_node_var (node, 'language', is_unique=True)
    self._implements = get_node_var (node, 'implements', is_unique=True)
    self._extras = get_node_var (node, 'extras')
    self._requires = get_node_var (node, 'requires')
    self._imports = get_node_var (node, 'imports')
    self._type = node.nodeName

    if self._package is None:
      self._package = get_node_var (node.parentNode, 'package',
                                    is_unique=True)
    if self._language is None:
      self._language = get_node_var (node.parentNode, 'language',
                                     is_unique=True)

  def __str__ (self):
    s = ''
    s = s + 'Name: %s (%s)\n' % (self._name, self._type)
    s = s + '  Language: %s\n' % self._language
    s = s + '  Package: %s\n' % self._package
    s = s + '  Requires: %s\n' % self._requires
    s = s + '  Extras: %s\n' % self._extras
    return s

  def is_type (self, type):
    return self._type == type

  def bocca_object (self):
    if self.is_type ('interface'):
      obj = bocca_cmd.BoccaInterface (self._name, package=self._package)
    elif self.is_type ('enum'):
      obj = bocca_cmd.BoccaEnum (self._name, package=self._package)
    elif self.is_type ('port'):
      obj = bocca_cmd.BoccaPort (self._name, package=self._package)
    elif self.is_type ('class'):
      obj = bocca_cmd.BoccaClass (self._name, package=self._package)
    elif self.is_type ('component'):
      obj = bocca_cmd.BoccaComponent (self._name, package=self._package)
    elif self.is_type ('project'):
      obj = bocca_cmd.BoccaProj (self._name, package=self._package)
    else:
      print '%s: Unknown bocca object' % self._type
      obj = None

    if self._requires is not None:
      obj.set_requires (self._requires)
    if self._implements is not None:
      obj.set_implements (self._implements)
    if self._language is not None:
      obj.set_language (self._language)
    if self._imports is not None:
      obj.set_srcdir ('../src/csdms')
    #if self._extras is not None:
    #  obj.set_extras (self._extras)

    return obj

  def bocca_command (self, command):
    cmd = bocca_cmd.BoccaCommand (command, self.bocca_object ())
    return cmd

#dom = xml.dom.minidom.parseString (document)

def get_text (nodelist):
  rc = ""
  #for node in nodelist:
  if node.nodeType == node.TEXT_NODE:
    rc = rc + node.data
  return rc

def get_text (nodelist):
  rc = ''
  for node in nodelist:
    if node.nodeType == node.TEXT_NODE:
      rc = rc + node.data
  return rc.strip ()

def handle_project_name (name):
  print "Project name is", get_text(name.childNodes)

def handle_project_language (name):
  print "--language=%s" % get_text(name.childNodes)

def handle_project_package (name):
  print "--package=%s" % get_text(name.childNodes)

def handle_project_extras (extras):
  for extra in extras:
    print "Copy file %s" % get_text(extra.childNodes)

def handle_interface_name (name):
  print "Interface name is", get_text(name.childNodes).strip ()

def handle_interface_imports (name):
  print "Import ", get_text(name.childNodes).strip ()

def handle_interface_requires (name):
  print "Requires ", get_text(name.childNodes).strip ()

def handle_project_interface (interfaces):
  for interface in interfaces:
    handle_interface_name (interface.getElementsByTagName ('name')[0])
    handle_interface_imports (interface.getElementsByTagName ('imports')[0])
    handle_interface_requires (interface.getElementsByTagName ('requires')[0])

def get_node_var (node, var_name, is_unique=False):
  vars = []
  elements = node.getElementsByTagName (var_name)
  if elements is not None:
    for element in elements:
      if element.parentNode.isSameNode (node):
        vars.append (get_text (element.childNodes))
  if is_unique:
    if len (vars)==0:
      vars = None
    else:
      vars = vars[0]
  return vars

def get_node_child_nodes (node, child_name):
  children = []
  elements = node.getElementsByTagName (child_name)
  if elements is not None:
    for element in elements:
      if element.parentNode.isSameNode (node):
        children.append (element)
  return children

bocca_object_names = ['interface', 'enum', 'port', 'class', 'component']
def get_bocca_objects (parent):
  children = []
  for child in parent.childNodes:
    if child.nodeName in bocca_object_names:
      children.append (child)
  return children

def get_node_vars (node):
  vars = {}
  for var in node.childNodes:
    if (var.nodeType == node.ELEMENT_NODE and 
        var.nodeName not in bocca_object_names):
      var_name = var.nodeName
      var_val = get_text (var.childNodes)
      if vars.has_key (var_name):
        vars[var_name].append (var_val)
      else:
        vars[var_name] = [var_val]
  return vars

def handle_project (project):
  project = project.childNodes
  if len (project)>1:
    print 'Too many projects!'
  elif len (project)==0:
    print 'Not enough projects!'
  else:
    project = project[0]

  build = BoccaBuild (BoccaNode (project))
  for i in get_bocca_objects (project):
    build.add_node (BoccaNode (i))
  build.make ()

def parse_string (string):
  dom = xml.dom.minidom.parseString (string)
  project = dom.childNodes
  if len (project)>1:
    print 'Too many projects!'
  elif len (project)==0:
    print 'Not enough projects!'
  else:
    project = project[0]

  build = BoccaBuild (parse_project_node (project))
  build.set_srcdir (os.path.abspath ('../../src/csdms'))
  build.set_destdir ('.')
  for i in get_bocca_objects (project):
    build.add_node (parse_object_node (i))
  return build

def parse_file (file, srcdir='.', no_import=False):
  try:
    dom = xml.dom.minidom.parse (file)
  except IOError as err:
    raise BadFileError (file, err.strerror)
  else:
    project = dom.childNodes
    if len (project)>1:
      raise ParseError (file, "XML build file contains more than one project")
    elif len (project)==0:
      raise ParseError (file, "XML build file does not contain a project")
    else:
      project = project[0]

    build = BoccaBuild (parse_project_node (project), no_import=no_import)
    build.set_srcdir (os.path.abspath (srcdir))
    for node in get_bocca_objects (project):
      build.add_node (parse_object_node (node))

    return build

from xml.etree import ElementTree, ElementInclude

def parse (file, srcdir='.', no_import=False):
  try:
    doc = ElementTree.parse (file)
  except IOError as e:
    raise BadFileError (file, e.strerror)
    
  if doc.tag != 'project':
    raise ParseError (file, 'Build file does not contain a project')

  proj = doc.get_root ()

  build = BoccaBuild (proj.attrib, no_import=no_import)
  build.set_srcdir (os.path.abspath (srcdir))

  for node in proj.getchildren ():
    build.add_node (node)

def get_bocca_objects (element):
  objs = []
  ElementInclude.include (element)
  for child in element.getchildren ():
    if child.tag == 'project':
      objs.extend (get_bocca_objects (child))
    elif child.tag in bocca_object_names:
      objs.append (child)
  return objs

#handle_project (dom)

