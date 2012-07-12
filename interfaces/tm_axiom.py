# -*- coding: UTF-8 -*-
#!/usr/bin/env python

__author__ = "Kurt Pagani <pagani@scios.ch>"
__svn_id__ = "$Id:$"



import os
import re
import string

from scios.axiom.axiom import Axiom0

DATA_BEGIN = chr(2)
DATA_END = chr(5)
DATA_ESCAPE = chr(27)
DATA_COMMAND = chr(16)

DATA_TPL = string.Template('$format:$message')
CHANNEL_TPL = string.Template('$channel#$message')

# Data constants
VERBATIM = 'verbatim'
LATEX = 'latex'
HTML = 'html'
PS = 'ps'
SCHEME = 'scheme'
COMMAND = 'command'

# Channel constants
OUTPUT = 'output'
PROMPT = 'prompt'
INPUT = 'input'
ERROR = 'error'
STATUS = 'status'

DATA_CONST = [VERBATIM, LATEX, HTML, PS, SCHEME, COMMAND]
CHANNEL_CONST = [OUTPUT, PROMPT, INPUT]

PRETEX = r""


class TmData():
  def __init__(self, fmt, msg):
    if fmt in DATA_CONST:
      self.data = DATA_TPL.substitute(format=fmt, message=msg)
    elif fmt in CHANNEL_CONST:
      self.data = CHANNEL_TPL.substitute(channel=fmt, message=msg)
    else:
      raise TypeError

  def send(self):
    os.sys.stdout.write(DATA_BEGIN+self.data+DATA_END)
    os.sys.stdout.flush()


#
#
#

def get_index(prompt):
  """
  Return the number N in the input prompt (N) ->.
  """
  m = re.match("\(([0-9]+)\)", prompt)
  if m is not None  and len(m.groups()) == 1:
    return int(m.group(1))
  else:
    return False


def get_type_and_value(output):
  """
  Get index, type and value in the 'output'.
  """
  r = output.strip(" \n").split("Type:")
  ri = re.match("^\(([0-9]+)\)", r[0]).group(1)
  rv = re.split("^\([0-9]+\)",r[0])[1].strip(" \n")
  rv = re.sub("_\n","", rv)
  rt = r[1].strip()
  return ri, rt, rv


def extract_types(data):
  """
  Extract the type(s) returned (if any).
  """
  ty = re.findall('Type:[a-zA-Z0-9_. ]*', data)
  ty = map(lambda x: x.replace('Type:',''), ty)
  return map(lambda x: x.strip(), ty)


def extract_tex(data):
  """
  Extract TeX code from data.
  """
  tex = re.findall('\$\$[^\$]*\$\$', data)
  return tex


def remove_tex(data, tex = []):
  """
  Remove TeX code from data.
  """
  for s in tex:
    data = data.replace(s,'')
  return data


def split_tex(data):
  """
  Split the output by TeX code into text substrings .
  """
  return re.split('\$\$[^\$]*\$\$', data)


def tex_breqn(tex):
  """
  Transform TeX code for using the breqn package.
  """
  # remove leqno's
  tex = re.sub(r"\\leqno\(\d*\)", "%", tex)
  tex = r"\begin{dmath*}" + "\n" + tex + "\n" + r"\end{dmath*}"
  return tex


def modPrompt(prompt):
  """
  Modify the prompt.
  """
  p = re.sub(r"-", ">", prompt)
  p += " "
  return p


def processOutput(data):
  """
  Process the raw output.
  """
  tex = extract_tex(data)
  txt = remove_tex(data,tex)
  tex = map(lambda t: re.sub(r"\\leqno\(\d*\)", "", t), tex)
  tex = map(lambda t: re.sub(r"\\sp\s*([^ \t\r\n\f\v\\]*)", r"^{\1}", t), tex)
  tex = map(lambda t: re.sub(r"\\sb\s*([^ \t\r\n\f\v\\]*)", r"_{\1}", t), tex)
  tex = map(lambda t: re.sub(r"\\root\s*(\{\d*\})\s*\\of", r"\\sqrt[\1]", t), tex)
  tex = map(lambda t: PRETEX+t, tex)
  return txt, tex


err_start = TmData(VERBATIM, "Could not start Axiom.")
log=open("C:/users/scios/Desktop/ax.log",'w')#+debug

def main():

  ax = Axiom0()
  if not ax.start(): err_start.send()

  ax.writeln(")set output tex on")
  ax.writeln(")set output algebra off")

  TmData(VERBATIM, ax.banner).send()
  TmData(PROMPT, modPrompt(ax.prompt)).send()

  while True:
    s = raw_input()
    if s.startswith(')quit'):
      ax.stop()
      TmData(VERBATIM, "Axiom terminated.").send()
      break
    log.write(s+'\n')#+debug
    if len(s.splitlines()) > 1:
      ax.write(s)
    else:
      ax.writeln(s)

    if ax.hasoutput:
      txt, tex = processOutput(ax.output)
      for t in tex:
        TmData(LATEX, t).send()
      TmData(VERBATIM, txt).send()
    TmData(PROMPT, modPrompt(ax.prompt)).send()

if __name__ == '__main__':
  main()
