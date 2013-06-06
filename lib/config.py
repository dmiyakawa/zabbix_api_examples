'''
Secret config file.
'''

from lib import defaults

_servers = defaults._servers
server = defaults._default_server
username = defaults._username
password = defaults._password
log_level = defaults._log_level

def add_argparse_configs(parser, require_server=True):
  server_help = ('Specify full server URI '
                 '(e.g. "http://www.example.com/zabbix"), or '
                 'a shortcut name specified in your config file.')
  if require_server:
    parser.add_argument('server', help=server_help, default=server)
  else:
    parser.add_argument('--server', '-s', help=server_help, default=server)
    pass

  parser.add_argument('--username', '-u',
                      help='username for your Zabbix server.',
                      default=username)
  parser.add_argument('--password', '-p',
                      help='password for your Zabbix server.',
                      default=password)
  parser.add_argument('--log-level', '-l', type=int,
                      help='Set the log level for Zabbix API.',
                      default=log_level)
  return parser


def get_server_uri(name):
  if name in _servers:
    return _servers[name]
  else:
    return name

