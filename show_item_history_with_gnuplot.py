#!/usr/bin/python2.7
# -*- encoding: utf-8 -*-
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
Gets a history of one item and show it as a graph, using gnuplot library.
You need to install gnuplot and its python interface.

(In debian, python-gnuplot deb package is what you may want)

E.g.
> ./get_item_stat.py (zabbix) (target host) system.cpu.util[,system,avg1]

By default data in last 6 hours will be shown. There's no option to
enlarge (shorten) it.

'''

from extlib.zabbix_api import ZabbixAPI
from lib import config

import argparse
import pprint
import os
import sys
import tempfile
import time

import Gnuplot

def get_item_stat(server, username, password, log_level, host, key):
  zapi = ZabbixAPI(server=server, log_level=log_level)
  zapi.login(username, password)

  item = zapi.item.get({ 'filter': {'host': host, 'key_': key},
                           'output': 'extend' })
  itemid = item[0]['itemid']

  print('item:')
  pprint.pprint(item)
  print('itemid: {}'.format(itemid))

  # If this is set too long, your Zabbix server may not respond well.
  now = time.time()
  time_from = int(now - 6*60*60)
  time_till = int(now)

  # See: https://www.zabbix.com/documentation/1.8/api/history/get
  #
  # All parameters are optional except "history".
  # If parameter is set in query, this option is considered
  # as being ON, except if parameter is equal to NULL.
  results = zapi.history.get({'history': 0, # Numeric (float)
                              'itemids': [itemid], 
                              'output': 'extend',
                              'time_from': time_from,
                              'time_till': time_till,
                              # 'limit': 300,
                              })

  if len(results) == 0:
    print('Empty result. Exitting')
    sys.exit(1)
    return

  (fd, filename) = tempfile.mkstemp(text=1)
  f = os.fdopen(fd, 'w')
  try:
    min_clock = -1
    max_clock = -1
    for result in results:
      clock = int(result['clock'])
      value = result['value']
      if min_clock < 0:
        min_clock = clock
      else:
        min_clock = min(clock, min_clock)
        pass
      if max_clock < 0:
        max_clock = clock
      else:
        max_clock = max(clock, max_clock)
        pass
      f.write('{} {}\n'.format(clock, value))
      pass
    min_t = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(min_clock))
    max_t = time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(max_clock))
    print ('{} ({})-{} ({}) '.format(min_clock, min_t, max_clock, max_t))
    f.close()
    g = Gnuplot.Gnuplot()
    # g.set_range('yrange', (0,1))
    g.plot(Gnuplot.File(filename, using=(1,2), with_='lines'))
    raw_input('Press return to finish\n')
  finally:
    os.unlink(filename)
    pass
  pass


if __name__ == '__main__':
  parser = config.add_argparse_configs(argparse.ArgumentParser())
  parser.add_argument('host', help='hostname')
  parser.add_argument('key', help='item key')
  
  args = parser.parse_args()
  server = config.get_server_uri(args.server)

  get_item_stat(server, args.username, args.password, args.log_level,
                args.host, args.key)
  pass
