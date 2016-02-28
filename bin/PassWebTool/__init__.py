# $Id: //gbl/SF/PassWebTool/PassWebToolClass.py#1 $
from keepass import kpdb
from string import ascii_uppercase, ascii_lowercase,digits, punctuation
from random import choice
import logging, optparse, cgi, time, getpass
from os import environ
from ConfigParser import ConfigParser

from PassWebToolClass import PassWebToolException

#import logging.handlers
#f = logging.Formatter(fmt='%(levelname)s:%(name)s: %(message)s '
#    '(%(asctime)s; %(filename)s:%(lineno)d)',
#    datefmt="%Y-%m-%d %H:%M:%S")
#handlers = [
#    logging.handlers.RotatingFileHandler('rotated.log', encoding='utf8',
#        maxBytes=100000, backupCount=1),
#    logging.StreamHandler()
#]
#root_logger = logging.getLogger()
#root_logger.setLevel(logging.DEBUG)
#for h in handlers:
#    h.setFormatter(f)
#    h.setLevel(logging.DEBUG)
#    root_logger.addHandler(h)

def generate_pwid(size=6, chars=ascii_uppercase + digits):
    return ''.join(choice(chars) for _ in range(size))


def parseParams():
    '''
    parse arguments from cmdline(optparse) or web(form).
    :return: opmode(String), configuration(dict), entry(dict)
    '''
    parser = optparse.OptionParser(description="PassWebTool - a stupid idea")
    parser.add_option('-m','--mode', action="store", dest="mode", help="opmode: [list|get|edit|save]")
    parser.add_option('-c', action="store", dest="cfgfile", help="PassWebTool keepass config  [default:%default]",
                      default="../etc/pwt.ini" )
   # parser.add_option('-p', action="store", dest="kppass", help="KeePass: Password  [default:********]", default="PassWebTool")
    parser.add_option('-v', action="store_true", dest="verbose", help="enable logging")

    parser.add_option('-I', '--pwid', action="store", dest="pwid", help="Criteria: pwid (PassWordIDentification)")

    parser.add_option('-H', '--host', action="store", dest="host", help="Criteria: host-name")
    parser.add_option('-S', '--service', action="store", dest="service", help="Criteria: service-name")
    parser.add_option('-U', '--user', action="store", dest="username", help="Criteria: username")
    parser.add_option('-P', '--pass', action="store", dest="password", help="Criteria: password")
    parser.add_option('-N', '--notes', action="store", dest="notes", help="Criteria: notes")

    parser.add_option('-D', '--delete', action="store_true", dest="delete", help="remove entry (req. --pwid only)")

    form = cgi.FieldStorage()
    options, args = parser.parse_args()

    configfile = options.cfgfile
    if environ.has_key('cfgfile'):
        configfile = environ['cfgfile']

    try:
        cfgfile = ConfigParser()
        cfgfile.read( configfile )

        logfile = cfgfile.get("PassWebTool", "logfile")
        logverb = logging.INFO - 10 * cfgfile.getboolean("PassWebTool", "verbose")

        c = { 'kpfile': cfgfile.get("KeePass", "file"),
              'kppass': cfgfile.get("KeePass", "pass"),
              'kpgroup': cfgfile.get("KeePass", "new_folder") }

    except Exception, e:
        raise PassWebToolException("Error while parsing cfgfile: " + str(e))

    try:
        logging.basicConfig(format='%(levelname)s:%(message)s', filename=logfile, level=logverb)
    except IOError, e:
        raise PassWebToolException("Could not initiate logging: " + str(e))

    d = {'pwid': form.getvalue('pwid') or options.pwid or None,
        'host': form.getvalue('host') or options.host or None,
        'service': form.getvalue('service') or options.service or None   ,
        'username': form.getvalue('username') or options.username or None,
        'password': form.getvalue('password') or options.password or None,
        'notes': form.getvalue('notes') or options.notes or None}

    if d['pwid'] == '' or d['pwid'] == 'None':
        d['pwid'] = None

    opmode = form.getvalue('mode') or options.mode or None
    return opmode, c, d
