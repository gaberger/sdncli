from api import API
import requests
from uuid import uuid4
from pprint import pprint
from utils import print_table


def _get_modules(ctl, debug=False):
        moduledb = {}
        resource = API['MODULES'].format(server=ctl.server)
        headers = {'content-type': 'application/xml'}
        try:
            retval = ctl.session.get(resource, auth=ctl.auth, params=None, headers=headers)
        except requests.exceptions.ConnectionError:
            return(("Error connecting to BVC {}").format(ctl.server), False)
        if str(retval.status_code)[:1] == "2":
            data = retval.json()
            if debug:
                pprint.pprint(data)
            root = data['modules']['module']
            for line in root:
                modulemap = {'name':     line['name'],
                             'namespace': line['namespace'],
                             'revision':  line['revision']}
                moduledb.setdefault(str(uuid4()), []).append(modulemap)
            if len(moduledb) > 0:
                return(moduledb, True)
            else:
                return("No Modules found", False)
        else:
            return (("Unexpected Status Code {}").format(retval.status_code), False)


def show_modules(ctl, debug=False):
        (retval, status) = _get_modules(ctl, debug)
        if status:
            print_table("show-modules", retval, 'name')
        else:
            print("Houston we have a problem, {}").format(retval)
