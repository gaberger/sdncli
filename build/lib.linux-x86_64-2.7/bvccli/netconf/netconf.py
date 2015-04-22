import requests
from pprint import pprint
from uuid import uuid4
from ..common import api
from ..common import utils
import json


def _netconf_get(ctl, node, ds, apicall, debug, resource=None):
    resource = api.API[apicall].format(server=ctl.server, node=node, ds=ds, resource=resource)
    try:
        retval = ctl.session.get(resource, auth=ctl.auth, params=None, headers=ctl.headers,  timeout=120)
    except requests.exceptions.ConnectionError:
        return (("Error connecting to BVC {}").format(ctl.server), False)
    if str(retval.status_code)[:1] == "2":
        try:
            data = retval.json()
            if debug:
                pprint(data)
        except ValueError, e:
            return(("Bad JSON found: {} {}").format(e, retval.text), False)
        return(data, True)
    else:
        return (("Unexpected Status Code {}").format(retval.status_code), False)


def _netconf_post(ctl, node, ds, apicall, debug, data=None):
    resource = api.API[apicall].format(server=ctl.server, node=node, ds=ds)
    payload = json.dumps(data)
    try:
        retval = ctl.session.post(resource, auth=ctl.auth, params=None, headers=ctl.headers, data=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        return (("Error connecting to BVC {}").format(ctl.server), False)
    if str(retval.status_code)[:1] == "2":
        try:
            data = retval.json()
            if debug:
                print("Payload: {}").format(payload)
                pprint(data)
        except ValueError, e:
            return(("Bad JSON found: {} {}").format(e, retval.text), False)
        return(data, True)
    else:
        return (("Unexpected Status Code {}").format(retval.text), False)


def _get_capabilities(ctl, args, debug=False):
    moduledb = {}
    ds = "operational"
    node = args["<node>"]
    resource = api.API['CAPABILITIES'].format(server=ctl.server, ds=ds, node=args['<node>'])
    headers = {'content-type': 'application/xml'}
    try:
        retval = ctl.session.get(resource, auth=ctl.auth, params=None, headers=headers)
    except requests.exceptions.ConnectionError:
        return(("Error connecting to BVC {}").format(ctl.server), False)
    if str(retval.status_code)[:1] == "2":
        data = retval.json()
        if debug:
            pprint(data)
        try:
            root = data['netconf-state']['schemas']['schema']
            for line in root:
                modulemap = {'namespace': line['namespace'],
                             'revision':  line['version']}
                moduledb.setdefault(str(uuid4()), []).append(modulemap)
            if len(moduledb) > 0:
                return(moduledb, True)
            else:
                return(("No Modules found for Node: {}").format(node), False)
        except KeyError:
            return(("Error in schema for Node: {}").format(node), False)
    else:
        return (("Unexpected Status Code {}").format(retval.status_code), False)


def get_schemas(ctl, args):
    #TODO: Test for ietf-monitoring first
    debug = args['--debug']
    ds = 'operations'
    node = args['<node>']
    (retval, status) = _get_capabilities(ctl, args)
    if status:
        for i in retval.iteritems():
            module = i[1][0]['namespace'].rsplit(':', 1)[1]
            revision = i[1][0]['revision'] or None
            data = {'input': {'identifier': module}}
            (retval, status) = _netconf_post(ctl, node, ds, 'GETSCHEMA', debug, data)
            if status:
                data = retval['get-schema']['output']['data']
                if revision:
                    utils.print_file((module + '@' + revision), utils.get_schemadir(), json.dumps(data))
                else:
                    utils.print_file((module), utils.get_schemadir(), json.dumps(data))


def show_capabilities(ctl, args):
    (retval, status) = _get_capabilities(ctl, args)
    if status:
        utils.print_table("Node Capabilities", retval, 'namespace')
    else:
        print("Houston we have a problem, {}").format(retval)


def show_config(ctl, args):
    debug = args['--debug']
    node = args['<node>']
    if(args['--config']):
        ds = 'config'
    else:
        ds = 'operational'
    (retval, status) = _netconf_get(ctl, node, ds, 'NETCONF', debug)
    if status:
        pprint(retval)
        utils.write_file(node, utils.get_configdir(), json.dumps(retval))
    else:
        print("Houston we have a problem, {}").format(retval)


def show_schema(ctl, args):
    debug = args['--debug']
    ds = 'operations'
    module = args['<resource>']
    data = {'input': {'identifier': module}}
    (retval, status) = _netconf_post(ctl, args['<node>'], ds, 'GETSCHEMA', debug, data)
    if status:
        print retval['get-schema']['output']['data']
    else:
        print("Houston we have a problem, {}").format(retval)
