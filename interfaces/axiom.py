# -*- coding: UTF-8 -*-
#!/usr/bin/env python

__author__ = "Kurt Pagani <pagani@scios.ch>"
__svn_id__ = "$Id:$"


"""
--- #YAML
Axiom0:
  - Low level class: with an instance of this class one can already
    communicate with Axiom on a send input string get output string
    basis.
Axiom1:
  - Input class
Axiom2:
    Output class
Axiom3:
    System commands

"""


import re
import sys
import time
import tempfile
import os, os.path
import termcolor

if os.name == 'nt':
  import winpexpect as xp
  spawn = xp.winspawn
else:
  import pexpect as xp
  spawn = xp.spawn



class fs:
  """
  --- #YAML: yaml.load(fs.__doc__.strip())
  Factory settings: >
    An instance of this (dummy) class is given as an argument to the
    init method of the base class and may be created e.g. internally
    or by a config file.
  """
  pass

# The name of the Axiom executable (eg. axiom, fricas, openaxiom)
# if the file is not in the system path then the full path is rquired.
# Even on win platforms use only forward slashes.
fs.appname = "openaxiom"

# The Axiom prompt has usually the form '(n) ->' (n an integer), so that
# the regexp pattern below should match.
fs.prompt_re = "\([0-9]+\) ->"

# Read quiet command (read in a file)
fs.cmd_read_quiet = ')read "{}" )quiet'

# Tempfile generation template (used by NamedTemporaryFile)
fs.tmpfile_kw = {'prefix':'ax$', 'suffix':'.input', 'delete':False}


class Axiom0():
  """
  Axiom base class. Handle the interaction with the console
  window and provide all low level routines for a device and
  os independent subclass.
    - start, stop
    - read header/banner
    - expect prompt
    - handle i/o (send input, read output)
    - detect/manage errors
    - store history
  """

  def __init__(self, cfg = fs()):
    """
    The argument cfg has to be an instance of the factory settings.
    E.g. cfg = mycfg, then mycfg is expected to have all porperties
    of fs.
    """

    # Publish the cfg instance
    self.cfg = cfg

    # Define the axiom process
    self.axp = None

    # The header/banner read when started
    self.banner = None

    # The current prompt
    self.prompt = None

    # Output caught after a command has been sent (always unmodified)
    self.output = None

    # Last error enountered (0: OK, 1: EOF, 2: TIMEOUT)
    self.error = None

    # Log file ([win]spawn)
    self.logfile = None


  def _axp_expect(self):
    """
    Return True if the prompt was matched otherwise return False and
    set the error=1 if EOF or error=2 if Timeout.
    """
    self.error = self.axp.expect([self.cfg.prompt_re, xp.EOF, xp.TIMEOUT])
    if self.error == 0:
      self.error = None
      return True
    else:
      return False


  def _axp_sendline(self, txt):
     """
     Send the text+os.linesep to Axiom and expect the prompt. Moreover
     reset the error state. Return is as in _axp_expect.
     """
     self.error = None
     n = self.axp.sendline(txt) #chk n>=len(txt) ?
     return self._axp_expect()


  def start(self, **kwargs):
    """
    --- #YAML
    Action: Start (spawning) Axiom.
    Return: True or False
    The following keywords (kwargs) may be used:
      args=[], timeout=30, maxread=2000, searchwindowsize=None
      logfile=None, cwd=None, env=None, username=None, domain=None
      password=None
    For details consult the pexpect manual as this parameters are the same
    as in the spawn/winspawn function respectively.
    Note: after started one may access the values as follows:
      <axiom_instance>.axp.<keyword>, e.g. a.axp.timeout -> 30.
    """
    if self.axp is None:
      self.axp = spawn(self.cfg.appname, **kwargs)
      if self._axp_expect():
        self.banner = self.axp.before
        self.prompt = self.axp.after
        return True
      else:
        return False


  def stop(self):
    """
    Stop Axiom (the hard way). One may also send the command ')quit'
    to Axiom using writeln for example.
    The return value is that of the isalive() function.
    """
    if self.axp is not None:
      self.axp.close()
      self.axp = None
    return not self.isalive()


  def isalive(self):
    """
    Check if Axiom is running.
    """
    if self.axp is not None:
      return self.axp.isalive()
    else:
      return False


  def haserror(self):
    """
    True if there was an error.
    """
    return self.error is not None


  def hasoutput(self):
    """
    True if there is output.
    """
    return self.output is not None


  def writeln(self, src):
    """
    Write a line to Axiom, i.e. as if it were entered into the interactive
    console. Output - if any - is (unmodified) stored in 'output'.
    Note: src should not contain any control characters; a newline (in fact
    os.linesep) will be added automatically. Axiom's continuation character,
    however, is no problem.
    """

    if self._axp_sendline(src):
      self.output = self.axp.before
      self.prompt = self.axp.after
      return True
    else:
      self.output = None
      return False


  def writef(self, filename):
    """
    Write the content of the file to Axiom, i.e. urge Axiom to read it in
    by itself.
    """

    if os.path.isfile(filename):
      return self.writeln(self.cfg.cmd_read_quiet.format(filename))
    else:
      return False


  def write(self, src):
    """
    Place the string src into a temp file and call writef, that is command
    Axiom to read in the temp file. Note: the temp file will be deleted
    after having been raed into Axiom.
    This command allows multiline input in SPAD/Aldor form.
    """

    tmpf = tempfile.NamedTemporaryFile(**self.cfg.tmpfile_kw)
    tmpf.write(src)
    tmpf.close()
    rc = self.writef(tmpf.name)
    os.unlink(tmpf.name)
    return rc




def main():
  pass

if __name__ == '__main__':
  main()
