# -*- coding: UTF-8 -*-
#!/usr/bin/env python

#++deprecated

__author__ = "Kurt Pagani <pagani@scios.ch>"
__svn_id__ = "$Id:$"

"""
Module app_latex:
  - Functions for compiling TeX code and creating various output formats.
  - A TeX class for pretty printing objects in various applications,
    especially IPython qtconsole/notebook and WikidPad previewer.

  Configuration:
    Create an instance of the factory settings: cfg = fs()
    - fs.__dict__ shows the properties
    - modify cfg before or after instance creation, depending on
      what result is to be achieved. If auto = True in the TeX class
      then certain porperties are used at instantiation.

  The TeX class:
    Example: hbar = TeX("$\hbar$")

"""


import re
import subprocess
import os, os.path
from shutil import move
from tempfile import NamedTemporaryFile


pipe = subprocess.PIPE

#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
# Default configuration (fs = factory settings) ;;;
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

class fs: pass
fs.__doc__ = """app_latex factory settings"""
fs.latex = 'latex'
fs.pdflatex = 'pdflatex'
fs.dvipng = 'dvipng'
fs.breqn = True
fs.pt = 10
fs.D = 120
fs.T = 'tight'
fs.bg = 'Transparent'
fs.fg = 'Blue'
fs.O = '0cm,0cm'
fs.bd = '0'

fs.preamble_breqn = r'''\documentclass[%ipt]{article}
\usepackage{amssymb,amsmath}
\usepackage{breqn}
\pagestyle{empty}
\begin{document}
%s
\end{document}'''

fs.preamble = r'''\documentclass[%ipt]{article}
\usepackage{amssymb,amsmath}
\pagestyle{empty}
\begin{document}
%s
\end{document}'''

if fs.breqn: fs.preamble = fs.preamble_breqn

fs.opt = None
fs.opt_tpl = "-T %s -D %i -bg %s -fg %s -O %s -bd %s"
fs.suffixes = ['.tex', '.dvi', '.log', '.aux', '.png', '.pdf']
fs.keepfiles = False
fs.outdir = None

fs.latex_cmd_tpl = "%s -halt-on-error -output-directory=%s %s"
fs.dvipng_cmd_tpl = "%s %s -o %s %s"

fs.repr_png = True

#;;;;;;;;;;;;;;
# Functions ;;;
#;;;;;;;;;;;;;;

def latex(src, cfg):
  """
  Write the TeX source to a temporary file then run latex with the file as
  input. All output goes into the system temp directory.
  Return: Popen return code, stdout, stderr, temp file name.
  """
  # Create a named temporary file for the TeX source code
  texfile = NamedTemporaryFile(suffix = ".tex", delete = False)

  # Create the TeX source (template % (font_size, tex_string)
  texinput = cfg.preamble % (cfg.pt, src)

  # Write TeX input to temp file and close it
  texfile.write(texinput)
  texfile.close()

  # LaTeX process
  cmd_tpl = cfg.latex_cmd_tpl
  if cfg.outdir is None:
    outdir = os.path.dirname(texfile.name)
  cmd = cmd_tpl % (cfg.latex, outdir, texfile.name)
  p = subprocess.Popen(cmd, shell = True, stdout = pipe, stderr = pipe)

  # Run (returns stdout/stderr)
  outlog, errlog = p.communicate()

  return p.returncode, outlog, errlog, texfile.name


def pdflatex(src, cfg):
  """
  Write the TeX source to a temporary file then run pdflatex with the file as
  input. All output goes into the system temp directory.
  Return: Popen return code, stdout, stderr, pdf file name.
  """
  # Create a named temporary file for the TeX source code
  texfile = NamedTemporaryFile(suffix = ".tex", delete = False)

  # Create the TeX source (template % (font_size, tex_string)
  texinput = cfg.preamble % (cfg.pt, src)

  # Write TeX input to temp file and close it
  texfile.write(texinput)
  texfile.close()

  # LaTeX process
  cmd_tpl = cfg.latex_cmd_tpl
  if cfg.outdir is None:
    outdir = os.path.dirname(texfile.name)
  cmd = cmd_tpl % (cfg.pdflatex, outdir, texfile.name)
  p = subprocess.Popen(cmd, shell = True, stdout = pipe, stderr = pipe)

  # Run (returns stdout/stderr)
  outlog, errlog = p.communicate()

  root, ext  = os.path.splitext(texfile.name)
  return p.returncode, outlog, errlog, root + '.pdf'


def dvipng(dvifile, cfg):
  """
  Create a PNG image by running dvipng on the dvi file (dvifile).
  Return: Popen returncode, stdout, stderr, png file name.
  """
  root, ext = os.path.splitext(dvifile)
  pngfile = root + ".png"

  if cfg.opt == None:
    cfg.opt = cfg.opt_tpl % (cfg.T, cfg.D, cfg.bg, cfg.fg, cfg.O, cfg.bd)

  cmd = cfg.dvipng_cmd_tpl % (cfg.dvipng, cfg.opt, pngfile, dvifile)
  p = subprocess.Popen(cmd, shell = True, stdout = pipe, stderr = pipe)

  # Run (returns stdout/stderr)
  outlog, errlog = p.communicate()

  return p.returncode, outlog, errlog, pngfile


def cleanup(path, cfg):
  """
  Remove all (by this instance) produced temp files with suffixes defined in
  cfg.suffixes. Return True or False.
  """
  # Cleanup (leave no traces in temp dir)
  if cfg.keepfiles: return True
  suffixes = cfg.suffixes
  try:
    for s in suffixes: os.remove(path + s)
    return True
  except:
    return False


def get_fileparts(f):
  """
  Get the head, tail, root and ext part of a file.
  """
  if isinstance(f, file):
    name = f.name
  elif isinstance(f, str):
    name = f
  else:
    return None

  head, tail = os.path.split(name)
  root, ext = os.path.splitext(tail)
  return head, tail, root, ext


def tex2png(src, cfg):
  """
  Create a TeX rendered PNG image from the TeX source string src.
  Return: the name of the PNG file as string.
  """
  r, out, err, fname = latex(src, cfg)
  if r != 0:
    return False
  root, ext = os.path.splitext(fname)
  dvifile = root + '.dvi'
  r, out, err, pngfile = dvipng(dvifile, cfg)
  if r != 0:
    return False
  else:
    return pngfile


#;;;;;;;;;;;;;;
# Class TeX ;;;
#;;;;;;;;;;;;;;

class TeX():
  """
  Class to handle LaTeX code.
  """
  def __init__(self, src, cfg = fs() , auto = True):
    """
    The src parameter must be a string containing TeX code. The cfg
    parameter is an instance of the factory settings class (maybe
    modified). If auto = True then a PNG image will be created during
    the instantiation of the class.
    """
    self.src = src
    self.cfg = cfg

    self.latex_output = None
    self.latex_errlog = None
    self.tex_filename = None

    self.dvipng_output = None
    self.dvipng_errlog = None
    self.dvifile = None
    self.pngfile = None
    self.png = None

    if auto: self.tex2png(src)


  def do_latex(self, src):
    """
    Run latex on the tex source src.
    Return: Popen return code (integer).
    """
    r, out, err, texfname = latex(src, self.cfg)
    self.latex_output = out
    self.latex_errlog = err
    self.tex_filename = texfname
    return r


  def do_dvipng(self, dvifile):
    """
    Create a png image from the dvi file dvifile.
    Return: Popen return code (integer).
    """
    r, out, err, pngfile = dvipng(dvifile, self.cfg)
    self.dvipng_output = out
    self.dvipng_errlog = err
    self.pngfile = pngfile
    return r


  def tex2png(self, src):
    """
    Create a png image from the tex source src. The png file name is stored
    in self.pngfile.
    Return: True or False
    """
    if bool(self.do_latex(src)): return False
    root, ext = os.path.splitext(self.tex_filename)
    self.dvifile = root + '.dvi'
    if bool(self.do_dvipng(self.dvifile)): return False
    return True


  def cleanup(self):
    """
    Remove all (by this instance) produced temp files.
    """
    root, ext = os.path.splitext(self.tex_filename)
    return cleanup(root, self.cfg)


  def reset(self):
    """
    Reset most parameters save src, so that a new rendering process
    (eventually with modified configuration) may be started.
    """
    self.pngfile = None
    self.png = None
    self.latex_errlog = None
    self.dvipng_errlog = None
    self.latex_output = None
    self.dvipng_output = None
    self.tex_filename = None
    self.cfg.opt = None


  def get_fs(self):
    """
    Get the factory settings as dictionary. The modified settings may
    be obtained by <instance_name>.cfg.__dict__
    """
    return self.cfg.__class__.__dict__


  def _repr_png_(self):
    """
    Representation method for PNG image. Used e.g. in IPython qtconsole
    and/or notebook.
    """
    if not self.cfg.repr_png: return None
    if self.png is not None:
      return self.png
    else:
      if self.pngfile is not None:
        f = open(self.pngfile,"rb")
        self.png = f.read()
        f.close()
        return self.png

#;;;;;;;;;;;;;;;;;
# Main section ;;;
#;;;;;;;;;;;;;;;;;

def main():
  pass

if __name__ == '__main__':
  main()
