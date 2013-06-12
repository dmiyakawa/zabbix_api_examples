#!/usr/bin/python3
#
#   Copyright 2013 Daisuke Miyakawa (d.miyakawa@gmail.com)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

'''
Make sure your account have an access to Template group
(read/write or read-only)
'''

from extlib.zabbix_api import ZabbixAPI
from lib import config

import argparse
import pprint
import sys

# See also:
# https://www.zabbix.com/documentation/1.8/manual/installation/requirements
# 
# History: days*(items/refresh rate)*24*3600*bytes (bytes ~= 50)
# Trends: days*(items/3600)*24*3600*bytes (bytes ~= 128)
# Events: days*events*24*3600*bytes (bytes ~= 130)
#
def estimate_database_size(server, username, password, log_level,
                           template_name):
  zapi = ZabbixAPI(server=server, log_level=log_level)
  zapi.login(username, password)

  print ('Zabbix Server version: {}'.format(zapi.apiinfo.version({})))
  templates = zapi.template.get({'output': 'extend',
                                'filter': {'host': template_name}})
  if len(templates) == 0:
    print ('Unknown template "{}"'.format(template_name))
    sys.exit(1)
    return

  template = templates[0]
  templateid = template['templateid']

  items = zapi.item.get({'templateids': templateid, 'output': 'extend'})
  usage = 0
  for item in items:
    key_ = item['key_']
    refresh_rate = int(item['delay'])
    history = int(item['history'])
    trends = int(item['trends'])
    # print (key_, refresh_rate, history, trends)
    usage += ((history * (24.0 * 3600)) / refresh_rate) * 50
    usage += (24.0 * trends) * 128
    pass
    # print(key_, delay, history, trends)
  print ('{} MB'.format(usage / 1024 / 1024))


if __name__ == '__main__':
  parser = config.add_argparse_configs(argparse.ArgumentParser())
  parser.add_argument('template_name', help='template name')
  args = parser.parse_args()
  server = config.get_server_uri(args.server)

  estimate_database_size(server, args.username,
                         args.password, args.log_level,
                         args.template_name)
