# About this repository

This (probably) contains a bunch of examples working with Zabbix API
(specifically Zabbix API wrapper) available at:
https://github.com/gescheit/scripts/tree/master/zabbix

Tested on 2013-06-06. If the upstream API has changed, this code
may not work well.

Tested with Zabbix Server 1.8.11 (Ubuntu package 1.8.11-1) and 
2.0.6 (CentOS package 2.0.6).

Licensed under Apache 2.0.

# How to use this.

Of course you need to know Zabbix and its API. Before that you may
need to learn what API (Application Programming Interface) is.
Oh well, you definitely want to know what the "programming" is. Etc. 

Seriously, you need two additional py files to let this work well.

1. Put zabbix_api.py onto extlib/
2. Put defaults.py onto lib/, having a few configurations for yourself

Here's example content of defaults.py. Note that before trying it,
make sure your account has sufficient priviledge toward each operation.

    _servers = {'example': 'http://example.com/zabbix'}
    _default_server = 'example'
    _username = 'Admin'
    _password = 'zabbix'
    _log_level = 0

