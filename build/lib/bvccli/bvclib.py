
import requests
import pprint
import uuid
import json
import netconflib
from requests.auth import HTTPBasicAuth
from api import API




class Controller(object):
    def __init__(self, auth, address):
        self.port = auth.get('port', 8181)
        self.auth = HTTPBasicAuth(auth.get('username', 'admin'), auth.get('password', 'admin'))
        self.server = address or auth.get('server')
        self.session = requests.Session()
        self.headers = {'content-type': 'application/json'}


    def http_get(self, uri):
        headers = {'content-type': 'application/xml'}
        try:
            retval = self.session.get(uri, auth=self.auth, params=None, headers=headers, timeout=120)
        except requests.exceptions.ConnectionError:
            return(("Error connecting to BVC {}").format(self.server), False)
        if str(retval.status_code)[:1] == "2":
            try:
                data = retval.json()
            except ValueError, e:
                return(("Bad JSON found: {} {}").format(e, retval.text), False)
            return(data, True)
        else:
            return (("Unknown Status Code").format(retval.status_code), False)


    # def get_bvc_flow_entries(self, api, debug):
    #     new_flow_entry = {}
    #     flowdb = {}
    #     resource = API[api].format(server=self.server)
    #     try:
    #         retval = self.session.get(resource, auth=self.auth, params=None, headers=self.headers, timeout=5)
    #     except requests.exceptions.ConnectionError:
    #         return(("Error connecting to BVC {}").format(self.server), False)
    #     if str(retval.status_code)[:1] == "2":
    #         data = retval.json()
    #         if debug:
    #             pprint.pprint(data)
    #         nodes = data['nodes']['node']
    #         for node in nodes:
    #             if "cont" not in node.get('id'):
    #                 _nodeid = node.get('id')
    #                 if _nodeid is not None:
    #                     print "Nodeid: %s" % _nodeid
    #                     if "flow-node-inventory:table" in node:
    #                         table = node['flow-node-inventory:table']
    #                         for table_entry in table:
    #                             if 'flow' in table_entry:
    #                                 for flow_entry in table_entry.get('flow'):
    #                                     s = self.extract(flow_entry, new_flow_entry)
    #                                     flowmap = {'nodeid': _nodeid,
    #                                                # 'flowname': s['flow-name'],
    #                                                'hardtimeout': s['hard-timeout'],
    #                                                'idletimeout': s['idle-timeout'],
    #                                                'flowid': s['id'],
    #                                                'in_port': s['in-port'],
    #                                                'ipv4destination': s['ipv4-destination'],
    #                                                'order': s['order'],
    #                                                #TODO get index of nodes to dereference
    #                                                'outputnode': s['output-node-connector'],
    #                                                'priority': s['priority'],
    #                                                'table_id': s['table_id'],
    #                                                'ethertype': s['type']}
    #                                                 #'vlanid': s['vlan-id']}
    #                                                 #TODO  u'vlan-id-present': True}
    #                                     flowdb.setdefault(str(uuid.uuid4()), []).append(flowmap)
    #         return (flowdb, True)
    #     else:
    #         return (("Unexpected Status Code {}").format(retval.status_code), False)

    # def _get_flows1(self, debug=False):
    #     #TODO Better management of match and action types
    #     #TODO Should this be formatted similar to ovs-ofctl dumpflows
    #     # try:
    #     resource = API['NODEINVENTORY'].format(server=self.server)
    #     try:
    #         retval = self.session.get(resource, auth=self.auth, params=None, headers=self.headers, timeout=5)
    #     except requests.exceptions.ConnectionError:
    #         print("Error connecting to BVC {}").format(self.server)
    #         return None

    #     if retval.status_code == 200:
    #         flowdb = {}
    #         data = retval.json()
    #         if debug:
    #             pprint.pprint(data)
    #         nodes = data['nodes']['node']
    #         _flowid = None
    #         _priority = None
    #         _table_id = None
    #         _matchrule = None
    #         _cookie = None
    #         _outputorder = None
    #         _outputport = None
    #         _gototable = None
    #         for node in nodes:
    #             if "cont" not in node.get('id'):
    #                 _nodeid = node.get('id')
    #                 table = node['flow-node-inventory:table']
    #                 for table_entry in table:
    #                     if 'flow' in table_entry:
    #                         for flow_entry in table_entry.get('flow'):
    #                             pprint.pprint(flow_entry)
    #                             for ak, av in flow_entry.viewitems():
    #                                 # for k, v in (filter(lambda x: m in x, flow_entry.viewitems())):
    #                                 if 'table_id' in ak:
    #                                     _table_id = av
    #                                 if 'id' in ak:
    #                                     _flowid = av
    #                                 if 'cookie' in ak:
    #                                     _cookie = av
    #                                 if 'match' in ak:
    #                                     if isinstance(av, dict):
    #                                         for match in av.viewitems():
    #                                             _matchrule = match
    #                                     else:
    #                                         print "%s:%s" % (ak, av)
    #                                         _matchrule = "Unknown"
    #                                 if 'instructions' in ak:
    #                                     for b in av.get('instruction'):
    #                                         # _order = b.get('order')
    #                                         if 'go-to-table' in b:
    #                                             print("Found I")
    #                                             _gototable = b['go-to-table']
    #                                         else:
    #                                             for bk, bv in b.viewitems():
    #                                                 if isinstance(bv, dict):
    #                                                     for ck, cv in bv.viewitems():
    #                                                         if isinstance(cv, list):
    #                                                             for i in cv:
    #                                                                 _outputport = i['output-action']['output-node-connector']
    #                                                                 _outputorder = i['order']
    #                                                         elif isinstance(cv, dict):
    #                                                             for k,v in cv.viewitems():
    #                                                                 print("Key: {}, Value {}").format(ak, av)
    #                                                             print("Found Dict")
    #                                 if 'priority' in ak:
    #                                     _priority = av
    #                             flowmap = {'nodeid': _nodeid,
    #                                        'flowid': _flowid,
    #                                        'cookie': _cookie,
    #                                        'match': _matchrule,
    #                                        'output': _outputport,
    #                                        'goto': _gototable,
    #                                        'order': _outputorder,
    #                                        'table': _table_id,
    #                                        'priority': _priority}
    #                             flowdb.setdefault(str(uuid.uuid1()), []).append(flowmap)
    #                             _flowid = None
    #                             _priority = None
    #                             _table_id = None
    #                             _matchrule = None
    #                             _cookie = None
    #                             _outputorder = None
    #                             _outputport = None
    #                             _gototable = None
    #                             # else:
    #                             #     print("Unknown Key Found {}:{}").format(k, v)

    #                 return flowdb

    #     else:
    #         print("Error with call {}").format(resource)
    #         print("Error: {}").format(resource.error)
    #     return None

        #     for k, v in l.items():
        #         mac = v[5:22]
        #         node_port = v[23:].split(':')
        #         mapping = {'port': node_port[2],
        #                    'switch': node_port[0] + ":" + node_port[1]}
