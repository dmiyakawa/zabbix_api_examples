#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import getpass
from logging import getLogger, StreamHandler
from logging import DEBUG

from datetime import datetime
import re
import time
import pyzabbix


r_period = re.compile(r'(\d+)((?:h(?:ours?)?)|(?:m(?:mins?)?))')

def main():
    parser = argparse.ArgumentParser(
        description=('Start maintenance right now'))
    parser.add_argument('hostname', action='store')
    parser.add_argument('-d', '--delete-existing', action='store_true',
                        help=('Remove existing maintenance with same name'
                              ' if exists.'))
    parser.add_argument('--user', action='store', default='zabbixapi')
    parser.add_argument('--password', action='store')
    parser.add_argument('--name', action='store', default='Shot maintenance',
                        help='Name of the maintanance stored in Zabbix')
    parser.add_argument('--period', action='store',
                        default='2h',
                        help=('How long the maintenance should be.'
                              'Seconds or something like "2h" / "30m".'
                              'No complicated values will be accepted :-)'))
    parser.add_argument('--targets', action='store', nargs='*',
                        help='If empty all hosts will be under maintenance')
    parser.add_argument('--log', action='store', default='INFO',
                        help=('Set log level. e.g. DEBUG, INFO, WARN'))
    parser.add_argument('--log-pyzabbix', action='store_true',
                        help=('Show PyZabbix\'s log. Useful if you want'
                              ' to see JSON query that are sent/received.'))

    args = parser.parse_args()
    logger = getLogger(__name__)
    handler = StreamHandler()
    logger.setLevel(args.log.upper())
    handler.setLevel(args.log.upper())
    logger.addHandler(handler)
    if args.log_pyzabbix:
        pyzabbix.logger.addHandler(handler)
        pyzabbix.logger.setLevel(args.log.upper())

    if args.password:
        password = args.password
    else:
        password = getpass.getpass('Password: ')
    
    if args.period.isdigit():
        period = int(args.period)
    else:
        m_period = r_period.match(args.period)
        if m_period:
            mul = {'m': 60, 'h': 60*60}[m_period.group(2)[0]]
            period = int(m_period.group(1)) * mul
        else:
            logger.error('Failed to parse {}'.format(args.period))
            return
            
    logger.debug('Connecting to Zabbix host "{}" with user {}'
                 .format(args.hostname, args.user))
    zapi = pyzabbix.ZabbixAPI(args.hostname)
    zapi.login(args.user, password)

    logger.debug('Zabbix version: {}'.format(zapi.api_version()))

    filtered = zapi.maintenance.get(filter={'name': args.name})
    if filtered:
        assert len(filtered) == 1
        if args.delete_existing:
            logger.debug('Maintenance already exists ({}). Deleting it.'
                         .format(filtered[0]))
            zapi.maintenance.delete(filtered[0][u'maintenanceid'])
        else:
            logger.error('Maintenance already exists ({}).'
                         .format(filtered[0]))
            return

    start_time = int(time.time())
    end_time = start_time + period
    start_readable = (datetime.fromtimestamp(start_time)
                      .strftime('%Y-%m-%d %H:%M:%S'))
    end_readable = (datetime.fromtimestamp(end_time)
                    .strftime('%Y-%m-%d %H:%M:%S'))
    logger.debug('Creating maintenance "{}", from "{}" till "{}"'
                 .format(args.name, start_readable, end_readable))

    hosts = zapi.host.get(output='extend')
    logger.debug('Creating maintenance for {}'
                 .format(map(lambda x: x[u'name'], hosts)))
    hostids = map(lambda x: x[u'hostid'], hosts)
    result = zapi.maintenance.create(name=args.name,
                                     active_since=start_time,
                                     active_till=end_time,
                                     hostids=hostids,
                                     timeperiods=[{'timeperiod_type': 0,
                                                   'start_date': start_time,
                                                   'period': period}])
    logger.debug('Result: {}'.format(result))
    assert len(result[u'maintenanceids']) == 1

    logger.info('Created maintenance id: {}'
                .format(result[u'maintenanceids'][0]))


if __name__ == '__main__':
    main()

