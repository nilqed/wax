# -*- coding: UTF-8 -*-
#!/usr/bin/env python

#++deprecated

__author__ = "Kurt Pagani <pagani@scios.ch>"
__svn_id__ = "$Id:$"


"""
Usage examples:

  -- a = Axiom()
  -- a.start()
  -- print a.banner
  -- a.cmdloop()
  -- a.stop()

todo:
  -- offline axiom -> python script -> axiom )read in -> show result
  -- cmdblock (piles)

"""



import re
import sys
import time
import tempfile
import os, os.path
import termcolor
import app_latex

if os.name == 'nt':
  import winpexpect as xp
  spawn = xp.winspawn
else:
  import pexpect as xp
  spawn = xp.spawn


#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
# Defaults (factory settings) ;;;
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
class fs: pass
fs.__doc__ = """app_axiom factory settings"""

if os.name == 'nt':
  fs.appname = 'openaxiom'
else:
  fs.appname = 'axiom'

fs.cmd_init = ""
fs.cmd_read_tpl = ")read %s"  #no crlf !!
fs.cmd_read_quiet_tpl = ")read %s )quiet"
fs.in_prefix = 'scios$oax_'
fs.in_suffix = '.input'
fs.prompt_re = "\([0-9]+\) ->"
fs.use_tex = False
fs.use_breqn = True
fs.mode = 0
fs.err_tpl_start = "Error: Axiom start: %s"
fs.err_tpl_block = "Error: Block input: %s"
fs.err_tpl_line = "Error: Line input: %s"
fs.err_msg = ["No errors.", "EOF encountered.", "Timeout."]
fs.use_termcolors = True
fs.color_prompt = 'magenta'
fs.color_input = 'red'
fs.color_output = 'blue'
fs.tmp_log = True

#;;;;;;;;;;;;;;;;
# Class Axiom ;;;
#;;;;;;;;;;;;;;;;
class Axiom():
  """
  Axiom base class.
  """
  def __init__(self, cfg = fs() ):

    # Config
    self.cfg = cfg

    # Application exe
    self.appname = cfg.appname

    # Init commands
    self.cmd_init = cfg.cmd_init

    # The axiom process
    self.p = None

    # Banner message of app
    self.banner = None

    # Output after command sent
    self.last_output = None
    self.output = None

    # TeX fragments in output
    self.tex = None

    # Text fragments in output
    self.txt = None

    # TeX instance
    self.tex_obj = None

    # Cmd templates to read in a file (within axiom)
    self.cmd_read_tpl = cfg.cmd_read_tpl
    self.cmd_read_quiet_tpl = cfg.cmd_read_quiet_tpl

    # Prefix for temp input files (block mode)
    self.in_prefix = cfg.in_prefix

    # Suffix for temp input files (block mode)
    self.in_suffix = cfg.in_suffix

    # Regular expression for prompt
    self.prompt_re = cfg.prompt_re

    # Last prompt caught
    self.prompt = None

    # Output configuration
    self.use_tex = cfg.use_tex
    self.use_breqn = cfg.use_breqn

    # Error string
    self.last_error = None
    self.error = None

    # Input mode ( line_mode = 0, block_mode = 1)
    self.mode = cfg.mode

    # Termcolors
    self.use_termcolors = cfg.use_termcolors

    # Type(s) returned
    self.types = []

    # Logfile
    self.logfile = None


  def errmsg(self, tpl, i):
    """
    Handle error messages.
    """
    return tpl % self.cfg.err_msg[i]


  def start(self):
    """
    Start Axiom.
    """
    if self.p is None:
      self.p = spawn(self.appname)
      i = self.p.expect([self.prompt_re, xp.EOF, xp.TIMEOUT])
      if i == 0:
        self.banner = self.p.before
        self.prompt = self.p.after
        if self.cfg.tmp_log: # log file
          self.tmp_log()
        return True
      else:
        self.error = self.errmsg(self.cfg.err_tpl_start, i)
        return False


  def stop(self):
    """
    Stop Axiom.
    """
    if self.p is not None:
      self.p.close()
      self.p = None


  def isalive(self):
    """
    Check if Axiom is running.
    """
    if self.p is not None:
      return self.p.isalive()
    else:
      return False


  def haserror(self):
    """
    True if there was an error.
    """
    return (self.error != None)


  def hasoutput(self):
    """
    True if there is output.
    """
    return not (self.output in [None, False])


  def input_block(self, src):
    """
    Input in block mode, i.e. as if a input file is read in (what is
    actually done). Output is (unmodified) stored in 'output'.
    """
    input_file = tempfile.NamedTemporaryFile(prefix = self.in_prefix,
      suffix = self.in_suffix, delete = False)
    input_file.write(src)
    input_file.close()

    cmd = self.cmd_read_quiet_tpl % input_file.name

    n = self.p.sendline(cmd)
    i = self.p.expect([self.prompt_re, xp.EOF, xp.TIMEOUT])

    if i == 0:
      self.output = self.p.before
      self.prompt = self.p.after
    else:
      self.output = False
      self.error = self.errmsg(self.cfg.err_tpl_block, i)


  def input_line(self, src):
    """
    Input in line mode, i.e. as if it were entered into the interactive
    console. Output is (unmodified) stored in 'output'.
    """
    n = self.p.sendline(src)
    i = self.p.expect([self.prompt_re, xp.EOF, xp.TIMEOUT])

    if i == 0:
      self.output = self.p.before
      self.prompt = self.p.after
    else:
      self.output = False
      self.error = self.errmsg(self.cfg.err_tpl_line, i)


  def get_current_index(self):
    """
    Return the current index, i.e. the number N in the input prompt (N) ->.
    """
    m = re.match("\(([0-9]+)\)", self.prompt)
    if m is not None  and len(m.groups()) == 1:
      return int(m.group(1))
    else:
      return False


  def get_type_and_value(self, output = None):
    """
    Get index, type and value in the 'output'. Default is the current output.
    """
    if output is None: output = self.output

    r = output.strip(" \n").split("Type:")
    ri = re.match("^\(([0-9]+)\)", r[0]).group(1)
    rv = re.split("^\([0-9]+\)",r[0])[1].strip(" \n")
    rv = re.sub("_\n","", rv)
    rt = r[1].strip()
    return ri, rt, rv


  def extract_types(self, data):
    """
    Extract the type(s) returned
    """
    ty = re.findall('Type:[a-zA-Z0-9_. ]*', data)
    ty = map(lambda x: x.replace('Type:',''), ty)
    return map(lambda x: x.strip(), ty)


  def extract_tex(self, data):
    """
    Extract TeX code from data
    """
    tex = re.findall('\$\$[^\$]*\$\$', data)
    return tex


  def remove_tex(self, data):
    """
    Remove TeX code from data
    """
    if (self.tex == None) or (self.tex == []):
      return data
    else:
      for s in tex:
        data = data.replace(s,'')
      return data


  def split_tex(self, data):
    """
    Split the output by TeX code into text substrings .
    """
    return re.split('\$\$[^\$]*\$\$', data)


  def tex_breqn(self, tex):
    """
    Transform TeX code for using the breqn package.
    """
    # remove leqno's
    tex = re.sub(r"\\leqno\(\d*\)", "%", tex)
    tex = r"\begin{dmath*}" + "\n" + tex + "\n" + r"\end{dmath*}"
    return tex


  def colorize_output(self, output = None, colors = None):
    if output is None: output = self.output
    if colors is None: colors = self.cfg.color_output
    return termcolor.colored(output, colors)

  def process_output(self):
    """
    Process the output.
    """
    # Error: if self.output is False
    if self.haserror():
      self.error = "An error occured. Check syntax."
      self.output = None
      return False

    # There is no output
    if not self.hasoutput():
      self.error = "No output"
      return False


    # Get the type(s) returned
    self.types = self.extract_types(self.output)

    # TeX processing (return if use_tex = False)
    if not self.use_tex: return False

    self.tex = self.extract_tex(self.output)
    self.txt = self.split_tex(self.output)

    # TeX output
    if self.use_breqn:
      self.tex = map(self.tex_breqn, self.tex)
    if self.tex != []:
      self.tex_obj = app_latex.TeX("\n".join(self.tex))


  def reset_output(self):
    """
    Set output and error variables to the initial state (i.e. None).
    """
    self.last_output = self.output
    self.last_error = self.error
    self.output = None
    self.error = None


  def tex_on(self):
    """
    Tell Axiom and myself to produce/handle TeX output.
    """
    self.input_line(")set output tex on")
    self.use_tex = True


  def tex_off(self):
    """
    Tell Axiom and myself not to produce/handle TeX output.
    """
    self.input_line(")set output tex off")
    self.use_tex = False


  def algebra_on(self):
    """
    Tell Axiom to set algebra output on.
    """
    self.input_line(")set output algebra on")


  def algebra_off(self):
    """
    Tell Axiom to set algebra output off.
    """
    self.input_line(")set output algebra off")


  def spool_on(self, filename):
    """
    Tell axiom to log all input/output to filename
    """
    self.input_line(')spool "%s"' % filename)


  def spool_off(self):
    """
    Tell axiom to stop logging/dribbling.
    """
    self.input_line(")spool")


  def tmp_log(self):
    """
    Dribble all input/output to a tempfile in the temp directory.
    """
    log = tempfile.mktemp(suffix=".log", prefix="ax_spool$")
    self.spool_on(log)
    self.logfile = log


  def show_tmp_log(self):
    """
    Print the logfile.
    """
    if self.logfile is not None:
      log = open(self.logfile,'r')
      print log.read()
      log.close()


  def cmdline(self):
    """
    Issue the prompt of the current command line in axiom and process the
    input then return to IPython.
    """
    if not self.isalive(): return False
    prompt = termcolor.colored(self.prompt, self.cfg.color_prompt)
    dist = termcolor.colored(" ", self.cfg.color_input)
    src = raw_input(prompt+dist)
    if src.startswith(")quit"): return  # more commands here. py eval ...
    self.input_line(src)
    self.process_output()
    if self.use_termcolors:
      print self.colorize_output()
    else:
      print self.output


  def cmdloop(self):
    """
    Start a command loop. Runs through process_output, i.e. the output
    may be modified (colorized for example).
    """
    if not self.isalive(): return False

    import readline, pyreadline
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')


    while True:
      prompt = termcolor.colored(self.prompt, self.cfg.color_prompt)
      dist = termcolor.colored(" ", self.cfg.color_input)
      src = raw_input(prompt+dist)
      if src.startswith(")quit"): break # more commands here. py eval ...
      self.input_line(src)
      self.process_output()
      if self.use_termcolors:
        print self.colorize_output()
      else:
        print self.output


  def cmd0(self, src):
    """
    Interactive; runs through process_output, i.e. output may be modified.
    """
    self.png = None
    self.tex_obj = None
    self.txt = None
    self.tex = None
    if self.mode == 0:
      self.input_line(src)
    else:
      self.input_block(src)
    self.process_output()
    if not self.use_tex:
      print self.output
    #print "\n" + self.prompt
    print "\n"
    for t in self.types:
      print t
    self.reset_output()
    if self.use_tex:
      if self.tex == []:
        print self.last_output
      else:
        return self.tex_obj


  def cmd1(self, src):
    """
    Send one command and get type and value of the result. Does not run
    through process_output.
    """
    n = self.get_current_index()
    self.input_line(src)
    self.get_type_and_value(self.output)


#
#
#



def test_cmdloop():
  a = Axiom()
  a.start()
  a.cmdloop()
  a.stop()
  del(a)
  return True




def main():
  pass

if __name__ == '__main__':
  main()
