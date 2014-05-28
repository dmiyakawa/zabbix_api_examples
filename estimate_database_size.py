#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import pyzabbix

import argparse
from functools import reduce
import getpass
from logging import getLogger, StreamHandler
from logging import DEBUG



# See also:
# https://www.zabbix.com/documentation/1.8/manual/installation/requirements
# 
# History: days*(items/refresh rate)*24*3600*bytes (bytes ~= 50)
# Trends: days*(items/3600)*24*3600*bytes (bytes ~= 128)
# Events: days*events*24*3600*bytes (bytes ~= 130)
#
def estimate_database_size(args, logger):
    if not args.url.startswith('http'):
        newurl = '{}{}{}'.format(args.prefix, args.url, args.suffix)
        logger.warning('URL (--url) does not start from "http".')
        logger.warning('Using "{}" for actual URL.'
                       .format(newurl))
        args.url = newurl

    logger.debug('Connecting to "{}" with user "{}"'
                 .format(args.url, args.username))
    zapi = pyzabbix.ZabbixAPI(args.url)
    logger.debug('Zabbix Server version: {}'
                 .format(zapi.api_version()))
    if not args.password:
        args.password = getpass.getpass('Password for {}: '
                                        .format(args.username))
    zapi.login(args.username, args.password)

    #if args.template:
    #    logger.debug('Look for template instead of host')

    if args.hosts:
        hosts = []
        for host in args.hosts:
            result = zapi.host.get(output='extend', filter={'host': host})
            if len(result) == 0:
                logger.error('No hostid for "{}"'.format(result))
                continue
            if len(result) > 1:
                logger.warning('More than one hostid for "{}" ({}).'
                               .format(host, result))
                return
            hosts.extend(result)
    else:
        hosts = zapi.host.get(output='extend')
    logger.debug('hosts: {}'.format(hosts))

    total_items = 0
    total_bytes = 0
    max_host_len = reduce(lambda x, host: max(x, len(host['host'])), hosts, 0)
    for host in hosts:
        items = zapi.item.get(filter={'hostid': host['hostid']},
                              output='extend',
                              templated=False)
        logger.debug('host: {} ({} items)'.format(host['host'], len(items)))
        total_items += len(items)
        subtotal_bytes = 0
        for item in items:
            logger.debug('item: {}'.format(item))
            refresh_rate = int(item['delay'])
            history = int(item['history'])
            trends = int(item['trends'])
            subtotal_bytes += ((history * (24.0 * 3600)) / refresh_rate) * 50
            subtotal_bytes += (24.0 * trends) * 128

        host_tmpl = '{:<' + str(max_host_len) + '}'
        logger.info((host_tmpl + '(id: {:3}): {:.2f} MB ({} items)')
                    .format(host['host'], host['hostid'],
                            subtotal_bytes / 1024 / 1024,
                            len(items)))
        total_bytes += subtotal_bytes

    if total_bytes > 1024 * 1024 * 1024:
        total_str = '{:.3f} GB'.format(total_bytes / (1024*1024*1024))
    elif total_bytes > 1024 * 1024:
        total_str = '{:.3f} MB'.format(total_bytes / (1024*1024))
    elif total_bytes > 1024:
        total_str = '{:.3f} KB'.format(total_bytes / 1024)
    else:
        total_str = '{} B'.format(total_bytes)

    print('Total: {} (Estimated Max. Not includes Event data!)'
          .format(total_str))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hosts',
                        help='Hosts in the Zabbix Server',
                        nargs='*')
    parser.add_argument('--template', action='store_true')
    parser.add_argument('--url',
                        help='Zabbix URL (e.g. http://localhost/zabbix)',
                        default='http://localhost/zabbix')
    parser.add_argument('--username', '-u',
                        help='username for your Zabbix server.',
                        default='Admin')
    parser.add_argument('--password', '-p',
                        help='password for your Zabbix server.')
    parser.add_argument('--prefix', default='http://')
    parser.add_argument('--suffix', default='/zabbix/')
    parser.add_argument('--log', '-l', action='store', default='INFO')
    parser.add_argument('--enable-pyzabbix-log', '-e', action='store_true')
    args = parser.parse_args()
    logger = getLogger(__name__)
    handler = StreamHandler()
    logger.setLevel(args.log.upper())
    handler.setLevel(args.log.upper())
    logger.addHandler(handler)
    if args.enable_pyzabbix_log:
        pyzabbix.logger.addHandler(handler)
        pyzabbix.logger.setLevel(args.log.upper())

    logger.debug('Start running')
    estimate_database_size(args, logger)


if __name__ == '__main__':
    main()
