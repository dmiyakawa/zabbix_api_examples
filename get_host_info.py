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

from extlib.zabbix_api import ZabbixAPI
from lib import config

import argparse
import pprint

def get_host_info(server, username, password, log_level):
  zapi = ZabbixAPI(server=server, log_level=log_level)
  zapi.login(username, password)

  responses = zapi.host.get({'output': 'extend'})
  
  hostid = responses[0]['hostid']
  items = zapi.item.get({'hostids': hostid, 'output': 'extend'})
  for item in items:
    print('"{}"(id: {}):'.format(item['name'], item['itemid']))
    pprint.pprint(item)
    pass
  pass

if __name__ == '__main__':
  parser = config.add_argparse_configs(argparse.ArgumentParser())
  args = parser.parse_args()
  server = config.get_server_uri(args.server)

  get_host_info(server, args.username,
                args.password, args.log_level)
