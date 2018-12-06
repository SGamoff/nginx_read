##### Ansible module read nginx.conf files

This module is required to read variables from the nginx.conf file or to get the bundle server name and its protocol path

```
options:
    path:
        description:
            - This is file nginx.conf path
        required: true
    variable:
        description:
            - The name of the variable we are looking for in the file <path>
        required: false if get_log_info set else true
    get_log_info:
        description:
            - The bool variable that indicates that you need to find a match for 
            the server name and its protocol in web-server configuration file <path>
        required: false if variable set else true
```

###### Requirements

The below requirements are needed on the host that executes this module.

 * Py python-nginx (`pip install python-nginx`)

###### Installation

Copy nginx_read.py in in the correct “magic” directory. [Ansible documentation](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-modules-and-plugins-locally)