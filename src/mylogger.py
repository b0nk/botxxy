import sys
import time

# sys.stdout.encoding is None when piping to a file.
encoding = sys.stdout.encoding
if encoding is None:
  encoding = sys.getfilesystemencoding()


class Logger(object):
  def __init__(self):
    self.terminal = sys.stdout
    self.log = open("botlog.log", "a", 0)

  def write(self, message):
    t = time.strftime('%H:%M:%S', time.localtime())
    try:
      self.terminal.write(message.encode(encoding, 'replace'))
      self.log.write("[%s] %s" % (t, message.encode(encoding, 'replace')))
    except UnicodeDecodeError:
      self.terminal.write(message)
      self.log.write("[%s] %s" % (t, message))
