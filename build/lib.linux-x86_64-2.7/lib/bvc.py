#!/usr/bin/python
# (C)2015 Brocade Communications Systems, Inc.
# 130 Holger Way, San Jose, CA 95134.
# All rights reserved.
# Author: Gary Berger <gberger@brocade.com>
"""
Usage:
        bvc  get-nodes [--address <ip>] [--json]
        bvc  get-hosts [--address <ip>] [--json]
        bvc  get-flows [--address <ip>] [--json]
        bvc  get-flow  [--address <ip>] <node> <table> <flow>
        bvc  add-flow  [--address <ip>] <node> <table> <flow>
        bvc  del-flow  [--address <ip>] <node> <table> <flow>

Options :
            --address           Address of controller (default: localhost)
            --json              Print JSON dump
            --help              This help screen
"""

import requests
import uuid
from lib.docopt import docopt
from requests.auth import HTTPBasicAuth
import lib.bvctmpl as t
# from ncclient import manager
import pprint
from prettytable import PrettyTable


API = {'NODEINVENTORY': 'http://{server}:8181/restconf/operational/opendaylight-inventory:nodes',
       'TOPOLOGY': 'http://{server}:8181/restconf/operational/network-topology:network-topology/',
       'FLOWMOD': 'http://{server}:8181/restconf/config/opendaylight-inventory:nodes/node/{node}/flow-node-inventory:table/{table}/flow/{flow}',
       'FLOW': 'http://{server}:8181/restconf/config/opendaylight-inventory:nodes/node/{node}/flow-node-inventory:table/{table}/flow/{flow}'}


class Controller(object):
    def __init__(self, restconf_server=None, port=8181):
        self.port = port
        self.auth = HTTPBasicAuth('admin', 'admin')
        self.server = restconf_server or 'localhost'
        self.session = requests.Session()
        self.headers = {'content-type': 'application/json'}

    def get_nodes(self, dumpjson=False):
            nodetable = {}
            resource = API['NODEINVENTORY'].format(server=self.server)
            print resource
            try:
                retval = self.session.get(resource, auth=self.auth, params=None, headers=self.headers, timeout=5)
            except Exception, e:
                raise e
            if retval.status_code == 200:
                data = retval.json()
                nodes = data.get('nodes').get('node')
                for node in sorted(nodes):
                    if "cont" not in node['id']:
                        nodeentry = {"Node": node.get('id')}
                        nodetable.setdefault(node.get('id'), []).append(nodeentry)
            if len(nodetable) > 0:
                self.print_table(nodetable)
            else:
                print "No nodes found"
                return None

    def get_flows(self, dumpjson=False):
        flowtable = self._get_flows()
        if len(flowtable) > 0:
            self.print_table(flowtable, 'nodeid')
        else:
            print "No flows found"
            return None

    def _get_flows(self, dumpjson=False):
        '''
        Get all flows known to controller. Traverses the node-inventory document to assemble.
        '''
        #TODO Better management of match and action types
        #TODO Should this be formatted similar to ovs-ofctl dumpflows
        # try:
        resource = API['NODEINVENTORY'].format(server=self.server)
        try:
            retval = self.session.get(resource, auth=self.auth, params=None, headers=self.headers, timeout=5)
        except Exception, error:
            raise error

        if retval.status_code == 200:
            flowdb = {}
            data = retval.json()
            nodes = data.get('nodes').get('node')
            for node in nodes:
                if "cont" not in node.get('id'):
                    _nodeid = node.get('id')
                    table = node['flow-node-inventory:table']
                    for table_entry in table:
                        if 'flow' in table_entry:
                            for flow_entry in table_entry.get('flow'):
                                for ak, av in flow_entry.viewitems():
                                    if 'id' in ak:
                                        _flowid = av
                                    if 'cookie' in ak:
                                        _cookie = av
                                    if 'match' in ak:
                                        if isinstance(av, dict):
                                            for match in av.viewitems():
                                                _matchrule = match
                                    if 'instructions' in ak:
                                        for b in av.get('instruction'):
                                            # _order = b.get('order')
                                            for bk, bv in b.viewitems():
                                                if isinstance(bv, dict):
                                                    for ck, cv in bv.viewitems():
                                                        for c in cv:
                                                            _outputport = c.get('output-action').get('output-node-connector')
                                                            _outputorder = c.get('order')
                                    if 'priority' in ak:
                                        _priority = av
                                    if 'table_id' in ak:
                                        _table_id = av

                                flowmap = {'nodeid': _nodeid,
                                           'flowid': _flowid,
                                           'cookie': _cookie,
                                           'match': _matchrule,
                                           'output': _outputport,
                                           'order': _outputorder,
                                           'table': _table_id,
                                           'priority': _priority}
                                flowdb.setdefault(str(uuid.uuid1()), []).append(flowmap)
            return flowdb

        else:
            print("Error with call {}").format(resource)
            print("Error: {}").format(resource.error)
        return None

    def get_hosts(self, dumpjson=False):
        dbhosts = {}
        hosttable = self._get_hosts()
        #TODO Check empty collection
        if hosttable is not None:
            for hosts in hosttable:
                host = hosttable.get(hosts)
                for h in host:
                    tid = h.get('t_id')
                    htsa = h.get('htsa')
                    for p in htsa:
                        for q in tid:
                            hostmap = {'IP': p.get('ip'), 'MacAddr': p.get('mac'), 'TID': q.get('tp-id')[23:]}
                            dbhosts.setdefault(p.get('id'), []).append(hostmap)
            if len(dbhosts) > 0:
                self.print_table(dbhosts)
            else:
                print "Found no Hosts"
                return
        #TODO ?
        else:
            print "No hosts found"
            return None

        # node_port = v[23:].split(':')
        #                         mapping = {'port': node_port[2],
        #                                    'switch': node_port[0] + ":" + node_port[1]}

    def _get_hosts(self, dumpjson=False):
        '''
        Get all hosts connected to known switches using topology data source
        '''
        resource = API['TOPOLOGY'].format(server=self.server)
        try:
            retval = self.session.get(resource, auth=self.auth, params=None, headers=self.headers, timeout=5)
        except Exception, error:
            raise error

        if retval.status_code == 200:
            hosttable = {}
            data = retval.json()
            nodes = data.get('network-topology').get('topology')
            for node in nodes:
                topology_nodes = node.get('node')
                if topology_nodes is not None:
                    for t_node in topology_nodes:
                        if 'host' in t_node.get('node-id'):
                            host = {'t_id': t_node.get('termination-point'),
                                    'htsa': t_node.get('host-tracker-service:addresses')
                                    }
                            hosttable.setdefault(t_node.get('node-id'), []).append(host)
                else:
                    return None

        return hosttable

        #     for k, v in l.items():
        #         mac = v[5:22]
        #         node_port = v[23:].split(':')
        #         mapping = {'port': node_port[2],
        #                    'switch': node_port[0] + ":" + node_port[1]}

    def delete_flow(self, node, table, flow):
        resource = API['DELETEFLOW'].format(server=self.server, node=node, table=table, flow=flow)
        retval = self.session.delete(resource, auth=self.auth, params=None, headers=self.headers)
        if retval.status_code is not "200":
            print retval.text

    def get_flow(self, node, table, flow):
        resource = API['FLOW'].format(server=self.server, node=node, table=table, flow=flow)
        retval = self.session.get(resource, auth=self.auth, params=None, headers=self.headers)
        if retval.status_code is not "200":
            print retval.status_code
            print retval.text
        else:
            print retval.text

    def add_flow(self, node, table, flow, actions):
        print actions
        headers = {'content-type': 'application/xml'}
        resource = API['FLOW'].format(server=self.server, node=node, table=table, flow=flow)
        retval = self.session.post(resource, auth=self.auth, params=None, headers=headers, data=actions, timeout=5)
        print resource
        print flow
        if retval.status_code is not "200":
            print retval.status_code
            print retval.text
        else:
            print retval.text

    # def netconf_connect(self, host, port, user):
    #     with manager.connect(host=host, port=830, username=user, hostkey_verify=False) as m:
    #         c = m.get_config(source='running').data_xml
    #     with open("%s.xml" % host, 'w') as f:
    #         f.write(c)

    def parse_hosttable(self, hosttable):
        for row in hosttable:
            print row

    def print_table(self, table, sortkey=None):
        p = PrettyTable()
        col_head = table.get(table.keys()[0])[0].keys()
        p.field_names = col_head
        p.sortby = sortkey
        p.padding_width = 1
        p.align = "l"
        for i in table:
            row = table.get(i)[0].values()
            p.add_row(row)
            # rows = [[row[sortindex]]+row for row in rows]
        #TODO Figure out how to put index column first and have secondary sort key.
        p.add_column('Index', range(len(table)))

        print p
        print("Total Records: {}").format(len(table))

if __name__ == "__main__":
    args = docopt(__doc__)
    ctl = Controller(args["<ip>"])
    if args["get-nodes"]:
        ctl.get_nodes(args["--json"])
    if args["get-hosts"]:
        ctl.get_hosts(args["--json"])
    if args["get-flows"]:
        ctl.get_flows(args["--json"])
    if args["del-flow"]:
        ctl.delete_flow(args['<node>'], args['<table>'], args['<flow>'])
    if args["get-flow"]:
        ctl.get_flow(args['<node>'], args['<table>'], args['<flow>'])
    if args["add-flow"]:
        ctl.add_flow(args['<node>'], args['<table>'], args['<flow>'], t.addflow)
