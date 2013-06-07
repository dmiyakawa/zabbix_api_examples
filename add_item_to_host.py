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
from extlib.zabbix_api import Already_Exists

import argparse
from lib import config
import sys

_name = 'Example: Used disk space on /var/log in %' 
_key = 'vfs.fs.size[/var/log,free]'

def add_item_to_host(server, username, password, log_level,
                     host, name, key, remove_duplicate=False):
  zapi = ZabbixAPI(server=server, log_level=log_level)
  zapi.login(username, password)

  version = zapi.apiinfo.version({})

  host_id = zapi.host.get({'filter': {'host': host}})[0]['hostid']
  duplicates = zapi.item.get({'filter': {'key_': key, 'host': host}})
  if len(duplicates) > 0:
    if remove_duplicate:
      print('Key "{}" already exists({}).'.format(key, duplicates))
      print('Try to remove it..')
      request = []
      for dup in duplicates:
        request.append(dup['itemid'])
        pass
      result = zapi.item.delete(request)['itemids']
      
      if type(result) == dict:
        # Seems a bug in 2.0.x, in which [{'itemids': {id: id}}] is returned.
        result = list(result.keys())
        pass

      if request != result:
        print('Requested ids ({}) and resultant ids ({}) don\'t match.'
              .format(request, result))
        sys.exit(1)
        return
      else:
        print('Delete operation seems successful.')
    else:
      print('Key "{}" already exists({}). Aborting..'.format(
          key, duplicates))
      sys.exit(1)
      return
    pass
  pass

  if version.startswith('2.2'):
    print('Not supported, yet.')
  elif version.startswith('2.0'):
    interfaceid = zapi.hostinterface.get({'hostids': host_id})
    try:
      # https://www.zabbix.com/documentation/2.0/manual/appendix/api/item/create
      result = zapi.item.create({ 'name' : name,
                                  'description' : 'description',
                                  'key_' : key,
                                  'type' : 0, # Zabbix agent
                                  'value_type': 0, # numeric float
                                  'hostid' : host_id,
                                  'interfaceid' : interfaceid[0]['interfaceid'],
                                  'delay' : 30,
                                  })
    except Already_Exists as e:
      print('Already exists')
      pass
    pass
  else: # 1.8, which returns '1.3'...
    # https://www.zabbix.com/documentation/1.8/api/item/create
    #
    # Note:
    #  - There's no "interfaceid" in 1.8
    #  - "name" isn't available but 'description is.
    #  - Already_Exists won't be returned even when it already exists.
    #  - Unkind errors will be sent on error, saying 
    #    "[ CItem::create ] Cannot create Item while sending .."
    result = zapi.item.create({ 'description' : name,
                                'key_' : key,
                                'hostid' : host_id,
                                'type' : 0, # Zabbix agent
                                'value_type': 0, # numeric float
                                'delay' : 30,
                                })
    pass
  print('Done.')
  pass


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=('Add an example item to '
                                                'a given host.'))
  config.add_argparse_configs(parser)
  parser.add_argument('host', help='hostname for the example item')
  parser.add_argument('--remove-duplicate', '-r', action='store_true',
                      help=('Remove duplicates when found, '
                            'instead of letting this app exit itself.'))

  args = parser.parse_args()
  server = config.get_server_uri(args.server)

  add_item_to_host(server, args.username, args.password, args.log_level,
                   args.host, _name, _key, args.remove_duplicate)
  pass
