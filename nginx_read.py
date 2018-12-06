#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.0.1',
    'status': ['beta'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: nginx_read

short_description: This is module read only configuration nginx.conf 

version_added: "2.4"

description:
    - "This module is required to read variables from the nginx.conf 
    file or to get the bundle server name and its protocol path"

options:
    path:
        description:
            - This is file nginx.conf path
        required: true
    variable:
        description:
            - The name of the variable we are looking for in the file <path>
        required: false
    get_log_info:
        description:
            - The bool variable that indicates that you need to find a match for 
            the server name and its protocol in web-server configuration file <path>
        required: false

author:
    - Sergey Gamov (@SGamoff)
'''

EXAMPLES = '''
# get variable value
- name: Test get value
  nginx_read:
    path: "/etc/nginx/nginx.conf"
    variable: "include"

# get all server_name and access_log from config
- name: Test get logs path
  nginx_read:
    path: "/etc/nginx/nginx.conf"
    get_log_info: "True"

# fail the module
- name: Test failure of the module
  nginx_read:
    path: "/etc/nginx/nginx.conf"
'''

RETURN = '''
variable:
    description: When find variable return dict of list value
    returned: success
    type: dict
    sample: variable:[value1, value2]
log_info:
    description: When find bundle server_name and his access_log
    returned: success
    type: dict
    sample: {"log_info":{"server1":"log1_path","server2":"log2_path"}}
'''

import fnmatch
import nginx
import os

from ansible.module_utils.basic import AnsibleModule


def _read_var(dictionary, variable):
    list = []
    for value in _rec_value_get(dictionary, variable):
        list.append(value)
    return list


def _rec_value_get(dictionary, key_item):
    if type(dictionary) is dict:
        for key, value in dictionary.items():
            if type(value) is dict or type(value) is list:
                for value in _rec_value_get(value, key_item):
                    yield value
            elif key==key_item:
                    yield value
    elif type(dictionary) is list:
        for value in dictionary:
            if type(value) is dict or type(value) is list:
                for value in _rec_value_get(value, key_item):
                    yield value


def search_srv_and_log(conf_obj, output):
    if len(conf_obj.servers) > 0:
        for server_instance in conf_obj.servers:
            server_name = None
            access_log = None
            for value in _rec_value_get(server_instance.as_dict, 'server_name'):
                server_name = value
            for value in _rec_value_get(server_instance.as_dict, 'access_log'):
                if (os.path.exists(value)): access_log = value
            if not server_name is None and not access_log is None:
                for domain_name in server_name.split():
                    output[domain_name] = access_log
    return output


def get_all_includes(path, all_acces_log=False, param=None, result=None):
    res = nginx.loadf(os.path.realpath(path))
    if result is None:
        result = {}
    for file_path in _read_var(res.as_dict, 'include'):
        dir_name = file_path[:file_path.rfind('/')+1]
        pattern = file_path[file_path.rfind('/')+1:]
        if os.path.exists(dir_name):
            for included_files in fnmatch.filter(os.listdir(dir_name), pattern):
                if (os.path.exists(dir_name + included_files)): get_all_includes(dir_name + included_files, all_acces_log=all_acces_log, param=param, result=result)
    if all_acces_log:
        result = search_srv_and_log(res, result)
    else:
        if not param in result.keys():
            result[param] = []
        result[param] = result[param] + _read_var(res.as_dict, param)
    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path = dict(type='path', required=True),
            variable = dict(default=None, required=False),
            get_log_info = dict(default=False, type='bool')
        ),
        supports_check_mode=True
    )
    path = module.params["path"]
    variable = module.params["variable"]
    get_log_info = module.params["get_log_info"]
    result = dict()
    if not variable is None:
        result = get_all_includes(path,param=variable)
    if variable is None and get_log_info == True:
        result["log_info"] = get_all_includes(path,all_acces_log=get_log_info)
    if variable is None and get_log_info == False:
        module.fail_json(msg='You request is failed need set variable or get_log_info.')
    module.exit_json(**result)


if __name__ == '__main__':
    main()