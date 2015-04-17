#!/usr/bin/python
# (C)2015 Brocade Communications Systems, Inc.
# 130 Holger Way, San Jose, CA 95134.
# All rights reserved.
# Author: Gary Berger <gberger@brocade.com>
"""
Usage:
        bvc  show-nodes     [--address <ip>] [--json]
        bvc  show-hosts     [--address <ip>] [--json]
        bvc  show-flows     [--address <ip>] [--json]
        bvc  show-modules   [--address <ip>] [--json]
        bvc  show-mounts    [--address <ip>] [--json]
        bvc  http-get       <uri> [--address <ip>]
        bvc  show-api       [--address <ip>]
        bvc  get-capabilities  <resource> [--json] [--address <ip>]
        bvc  get-config        <resource> (--ops | --config) [--address <ip>]
        bvc  get-schema        <node> <module> [--address <ip>]
        bvc  get-allschemas    <node> [--address <ip>]
        bvc  post-netconf      <resource> (--ops | --config)  [--node <node>] [--payload <json>] [--address <ip>]
        bvc  mount-device      <name> <address> <user> <password> [--port <port>] [--vdx] [--address <ip>]
        bvc  unmount-device    <name> [--address <ip>]

Options :
            --address           Address of controller (default: localhost)
            --json              Print JSON dump
            --help              This help screen
"""

from lib.docopt.docopt import docopt
from lib.bvclib import Controller
from lib.bvclib import API
import uuid
import pprint


def show_api():
    apitable = {}
    for k, v in API.viewitems():
        s = {'API': k, 'Link': v}
        apitable.setdefault(uuid.uuid4(), []).append(s)
    ctl.print_table("API", apitable)


def show_nodes(args):
    dumpjson = (args["--json"])
    nodemap = {}
    nodetable = {}

    # (retval, status) = ctl.get_bvc_nodes_oper(dumpjson)
    (retval, status) = ctl.get_bvc_nodes('OPER', dumpjson)
    node_ops = retval
    if status:
        (retval, status) = ctl.get_bvc_nodes('CONFIG', dumpjson)
        node_config = retval
        # (node_config, status) = ctl.get_bvc_nodes_config(dumpjson)
        if status:
            nodemap = node_ops.copy()
            nodemap.update(node_config)
        else:
            nodemap = node_ops

        for n in nodemap:
            s = {'node': n, 'status': nodemap[n]}
            nodetable.setdefault(uuid.uuid4(), []).append(s)
        ctl.print_table("get_nodes", nodetable)
    else:
        print("Error: {}").format(retval)


def show_hosts(args):
    dumpjson = (args["--json"])
    dbhosts = {}
    (retval, status) = ctl.get_bvc_hosts(dumpjson)
    hosttable = retval
    if status:
        #TODO Check empty collection
        if hosttable is not None:
            for hosts in hosttable:
                host = hosttable.get(hosts)
                for h in host:
                    tid = h.get('t_id')
                    htsa = h.get('htsa')
                    for p in htsa:
                        for q in tid:
                            hostmap = {'IP': p.get('ip'), 'MacAddr': p.get('mac'), 'TID': q.get('tp-id')}
                            dbhosts.setdefault(p.get('id'), []).append(hostmap)
            if len(dbhosts) > 0:
                ctl.print_table("get_hosts", dbhosts)
            else:
                print "Found no Hosts"
                return
        #TODO ?
        else:
            print "No hosts found"
            return None
    else:
        print("Error: {}").format(retval)

    # node_port = v[23:].split(':')
    #                         mapping = {'port': node_port[2],
    #                                    'switch': node_port[0] + ":" + node_port[1]}


# def show_flows(args):
#     dumpjson = args["--json"]
#     (configtable, status) = ctl.get_bvc_flow_entries("NODECONFIG", dumpjson)
#     if status:
#         if configtable is not None and len(configtable) > 0:
#                 self.print_table("get_flows", configtable, 'nodeid')
#         else:
#             print "No flows found in configuration table"
#             return None
#         opstable = self.get_bvc_flow_entries("NODECONFIG", dumpjson)
#         if configtable is not None and len(configtable) > 0:
#                 self.print_table("get_flows", configtable, 'nodeid')
#         else:
#             print "No flows found in configuration table"
#             return False

def show_modules(args):
    dumpjson = (args["--json"])
    (retval, status) = ctl.get_modules(dumpjson)
    if status:
        ctl.print_table("show-modules", retval, 'name')
    else:
        print("Houston we have a problem, {}").format(retval)


def get_capabilities(args):
    dumpjson = (args["--json"])
    (retval, status) = ctl.get_capabilities(args["<resource>"], dumpjson)
    if status:
        ctl.print_table("Node Capabilities", retval, 'namespace')
    else:
        print("Houston we have a problem, {}").format(retval)


def get_schema(args):
    module = args['<module>']
    node = args['<node>']
    data = {'input': {'identifier': module}}
    (retval, status) = ctl.netconf_get_schema(node, data)
    if status:
        print retval.json()['get-schema']['output']['data']


def get_all_schemas(args):
    node = args['<node>']
    (retval, status) = ctl.get_capabilities(node)
    if status:
        for i in retval.iteritems():
            data = {'input': {'identifier': i[1][0]['namespace'].rsplit(':', 1)[1]}}
            (retval, status) = ctl.netconf_get_schema(node, data)
            if status:
                print retval.json()['get-schema']['output']['data']


def show_mounts(args):
    dumpjson = (args["--json"])
    (retval, status) = ctl.get_mounts(dumpjson)
    if status:
        ctl.print_table("show-mounts", retval, 'name')
    else:
        print("Houston we have a problem, {}").format(retval)


def http_get(args):
    uri = args['<uri>']
    (retval, status) = ctl.http_get(uri)
    if status:
        print retval
    else:
        print("Houston we have a problem, {}").format(retval)


def get_config(args):
    if(args['--ops']):
        ds = 'operational'
    else:
        ds = 'config'
    (retval, status) = ctl.netconf_get(args["<resource>"], ds, 'NETCONF')
    if status:
        pprint.pprint(retval)
    else:
        print("Houston we have a problem, {}").format(retval)


def post_netconf(args):
    if(args['--ops']):
        ds = 'operational'
    else:
        ds = 'config'
    (retval, status) = ctl.netconf_post(args["<resource>"], ds, args['<json>'], args["<node>"])
    if status:
        pprint.pprint(retval)
    else:
        print("Houston we have a problem, {}").format(retval)


def mount_device(args):
    (retval, status) = ctl.mount_netconf_device(args['<name>'], args['<address>'], args['<user>'], args['<password>'], args['<port>'], args['--vdx'])
    if status:
        print(retval)
    else:
        print("Houston we have a problem, {}").format(retval)


def unmount_device(args):
    (retval, status) = ctl.unmount_netconf_device(args['<name>'])
    if status:
        print(retval)
    else:
        print("Houston we have a problem, {}").format(retval)


def parse_hosttable(hosttable):
    for row in hosttable:
        print row


def main():
    args = docopt(__doc__)
    ctl = Controller(args["<ip>"])
    if args["show-nodes"]:
        show_nodes(args)
    if args["show-hosts"]:
        show_hosts(args)
    if args["show-flows"]:
        print "Not Implemented"
    if args["show-modules"]:
        show_modules(args)
    if args["show-mounts"]:
        show_mounts(args)
    if args["show-api"]:
        show_api()
    if args['http-get']:
        http_get(args)
    if args['get-config']:
        get_config(args)
    if args['get-schema']:
        get_schema(args)
    if args['get-capabilities']:
        get_capabilities(args)
    if args['post-netconf']:
        post_netconf(args)
    if args['get-allschemas']:
        get_all_schemas(args)
    # if args["del-flow"]:
    #     ctl.delete_flow(args['<node>'], args['<table>'], args['<flow>'])
    # if args["get-flow"]:
    #     ctl.get_flow(args['<node>'], args['<table>'], args['<flow>'])
    # if args["add-flow"]:
    #     ctl.add_flow(args['<node>'], args['<table>'], args['<flow>'])
    if args["mount-device"]:
        mount_device(args)
    if args["unmount-device"]:
        unmount_device(args)
