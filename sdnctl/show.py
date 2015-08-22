"""
Usage:
        sdncli show hosts
        sdncli show mounts
        sdncli show nodes
        sdncli show config <node>
        sdncli show flows <node> <table>
        sdncli show flow <id>
        sdncli show interfaces
        sdncli show modules
        sdncli show rpc <node>
        sdncli show streams
        sdncli show providers
        sdncli show inventory

Options :
            -h --help              This help screen
            -o --operations        Read from operations datastore
            -c --config            Read from configuration datastore

"""
from util import print_table_dict
from pybvc.common.status import STATUS
from pybvc.openflowdev.ofswitch import OFSwitch
from pybvc.openflowdev.ofswitch import Match
from pybvc.common.utils import dict_unicode_to_string
from pybvc.common.utils import find_dict_in_list
from pybvc.netconfdev.vrouter.vrouter5600 import VRouter5600
from pybvc.netconfdev.vdx.nos import NOS

from singledispatch import singledispatch
from pprint import pprint

# @singledispatch
# def get_interfaces_list():
#     raise NotImplementedError("Not Implemented Yet!")


# @get_interfaces_list.register(VRouter5600)
# def _(obj):
#     result = VRouter5600.get_interfaces_list()
#     return result

# @get_interfaces_list.register(NOS)
# def _(obj):
#     raise NotImplementedError("Not Implemented")
#     return result

def show(ctl, args):
    # NODES
    if args.get('nodes'):
        table = []
        result = ctl.get_all_nodes_conn_status()
        for node in result.data:
            result = ctl.get_node_info(node.get('node'))
            if(result.status.eq(STATUS.OK)):
                d = result.data
                record = {'Node': node.get('node'),
                          'IPAddres': d.get('flow-node-inventory:ip-address'),
                          'SerialNo': d.get('flow-node-inventory:serial-number'),
                          'Software': d.get('flow-node-inventory:software'),
                          'Hardware': d.get('flow-node-inventory:hardware'),
                          'Connected': node.get('connected'),
                          'Decription': d.get('flow-node-inventory:description'),
                          'Manufacturer': d.get('flow-node-inventory:manufacturer')}
                table.append(record)
        fields = ['Node', 'Connected', 'Decription', 'Hardware', 'IPAddres', 'Manufacturer', 'SerialNo', 'Software']
        print_table_dict(fields, table)
        # print [[r['node'], r['connected'], node.clazz] for r in result.data for node in nodes if node.get_id() == r['node']]
    # HOSTS
    elif args.get('hosts'):
        if ctl.topology.get_hosts_cnt() > 0:
            table = []
            fields = ['IP', 'Mac', 'Id']
            hosts = ctl.topology.get_hosts()
            if hosts is not None:
                for host in hosts:
                    hostmap = {'Id': host.get_id(),
                               'Mac': host.get_mac_address(),
                               'IP': host.get_ip_address_for_mac(host.get_mac_address())}
                    table.append(dict(hostmap))
                print_table_dict(fields, table)
        else:
            print "No Hosts Found"
    # MOUNTS
    elif args.get('mounts'):
        result = ctl.build_netconf_config_objects()
        fields = ['name', 'port', 'address', 'username', 'password', 'connection_timeout_millis', 'connected']
        table = []
        for i in result.data:
            result = ctl.check_node_conn_status(i.name)
            if(result.status.eq(STATUS.NODE_CONNECTED)):
                i.connected = "True"
            else:
                i.connected = "False"
            table.append(i.__dict__)
        print_table_dict(fields, table)
    # CONFIG
    elif args.get('config'):
        node = args.get('<node>')
        result = ctl.check_node_conn_status(node)
        if(result.status.eq(STATUS.NODE_CONNECTED)):
            result = ctl.get_node_config(node)
            if(result.status.eq(STATUS.OK)):
                print (result.data).json()
            else:
                print "Houston we have a problem"
        else:
                print "Node {} is not mounted".format(node)

    # TOPOLOGY
    elif args.get('topology'):
        print "show topology"
    # MODULES
    elif args.get('modules'):
        pass
        # result = ctl.get_config_modules()
    #STREAMS
    elif args.get('streams'):
        streams = ctl.get_streams_info().data
        # TODO This returns empty DICT
        if len(streams) > 0:
            print streams
        else:
            print "No streams found"
    #PROVIDERS
    elif args.get('providers'):
        pass
        # providers =  ctl.get_service_providers_info().data
        # if len(providers) > 0:
        #     for i in providers:
        #         print i
        # else:
        #     print "No providers found"
    #FLOWS
    elif args.get('flows'):
        table = []
        node = args['<node>']
        flowtable = args.get('<table>', 0)
        ofswitch = OFSwitch(ctl, node)
        result = ofswitch.get_flows(flowtable, operational=True)
        if(result.status.eq(STATUS.OK)):
            # fields = ['cookie', 'priority', 'id', 'match', 'action', 'second', 'nanosecond', 'packet-count', 'byte-count']
            fields = ['cookie', 'priority', 'id', 'match', 'action', 'packet-count', 'byte-count']
            for i in result.data:
                # i['second'] = dict_unicode_to_string(i.get('opendaylight-flow-statistics:flow-statistics').get('duration').get('second'))
                # i['nanosecond'] = dict_unicode_to_string(i.get('opendaylight-flow-statistics:flow-statistics').get('duration').get('nanosecond'))
                i['packet-count'] = dict_unicode_to_string(i.get('opendaylight-flow-statistics:flow-statistics').get('packet-count'))
                i['byte-count'] = dict_unicode_to_string(i.get('opendaylight-flow-statistics:flow-statistics').get('byte-count'))
                match = dict_unicode_to_string(i.get('match'))
                match = str(match).translate(None, '{\'\`\ }')
                i['match'] = str(match).replace(",", "\n")
                action = dict_unicode_to_string(i['instructions']['instruction'][0])
                action = str(action).translate(None, '\'\`\ []]')
                i['action'] = str(action).replace(",", "\n")
                table.append(i)
            print_table_dict(fields, table, 'id')
        else:
            print "No Flows Found"
    #INTERFACES
    elif args.get('interfaces'):
        node = [[netconf_nodes, mounts] for netconf_nodes in ctl.inventory.netconf_nodes
                for mounts in (ctl.get_mounts()).data
                if netconf_nodes.get_id() == mounts['name']
                and 'controller-config' not in netconf_nodes.get_id()]
        for n in node:
            name = n[1]['name']
            port = n[1]['odl-sal-netconf-connector-cfg:port']
            address = n[1]['odl-sal-netconf-connector-cfg:address']
            user = n[1]['odl-sal-netconf-connector-cfg:username']
            password = n[1]['odl-sal-netconf-connector-cfg:password']
            m = globals()[n[0].clazz](ctl, name, address, port, user, password)
            result = m.get_interfaces_cfg()
            if(result.status.eq(STATUS.OK)):
                fields = ['cookie', 'priority', 'id', 'match', 'action']
                print (result.data)
            # for i in result:
            #     print i







