# -*- coding: UTF-8 -*-
#!/usr/bin/env python

__author__ = "Kurt Pagani <pagani@scios.ch>"
__svn_id__ = "$Id: wax.py 3 2008-01-22 19:51:27Z scios$"



import web

from string import Template
from interfaces.axiom import Axiom0

out = Template("<code>$txt</code>")

urls = ('/', 'index')
render = web.template.render('templates/')

ax = Axiom0()
ax.start()

class index:

  def GET(self):
    return render.index()

#   def POST(self):
#     data = web.data()
#     return "<code>ECHO:" + data + "</code>"

  def POST(self):
    data = web.data() # get input
    if data.startswith(")quit"):
      ax.stop()
      return out.substitute(txt="Axiom stopped.")
    ax.write(data) # send input to Axiom
    if ax.hasoutput():
      return out.substitute(txt=ax.output) # return Axiom output
    else:
      return out.substitute(txt="NIL")

def main():
  print "WebAxiom Test V 0.1"
  print "Press Ctrl-C or close this window to terminate the server\n"
  app = web.application(urls, globals())
  app.run()


if __name__ == '__main__':
  main()
