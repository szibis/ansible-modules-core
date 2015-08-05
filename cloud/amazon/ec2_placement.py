#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_placement
short_description: create, remove or list placement group(s) in EC2.
description:
    - Creates, removes and lists placement groups in EC2.
      This module has a dependency on python-boto.
version_added: "2.0"
options:
  name:
    description:
      - The EC2 placement group name.
    required: False
    default: null
  strategy:
    description:
      - The placement strategy of the new placement group.
        Currently, the only acceptable value is cluster
    required: False
    default: cluster
    choices: ['cluster']
  state:
    description:
      - Whether the placement group should be present or absent.
        Use list to show all or search specific placement group.
    required: False
    default: present
    choices: ['present', 'absent', 'list']
  region:
    description:
      - region in which the resource exists.
    required: False
    default: null
    aliases: ['aws_region', 'ec2_region']

author: "Slawomir Skowron (@szibis)"
extends_documentation_fragment: aws
'''

EXAMPLES = '''
# Basic example of adding placement group
tasks:
- name: add placement group
  ec2_placement:
      name: "example_group"
      state: "present"
      region: "us-east-1"

# Basic example for delete placement group
tasks:
- name: remove placement group
  ec2_placement:
      name: "example_group"
      state: "absent"
      region: "us-east-1"

# Basic example for listing all placement groups
tasks:
- name: list all placement group
  ec2_placement:
      state: "list"
      region: "us-east-1"

# Basic example for listing specific placement groups
tasks:
- name: list placement group
  ec2_placement:
      name: "example_group"
      state: "list"
      region: "us-east-1"
'''

RETURN = '''
name:
    description: Name given to the placement group or list of groups.
    returned: success
    type: string
strategy:
    description: The placement strategy of the new placement group.
    returned: success
    type: string
'''

import sys

try:
    import boto.ec2
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
                name=dict(required=False, type='str'),
                strategy=dict(default='cluster', choices=['cluster']),
                state=dict(default='present', choices=['present', 'absent', 'list'])
                )
            )
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    name = module.params.get('name')
    strategy = module.params.get('strategy')
    state = module.params.get('state')

    if not isinstance(name, basestring) and name:
        module.fail_json(msg="name argument must be string")

    ec2 = ec2_connect(module)

    if name:
        getplacements = ec2.get_all_placement_groups(filters={'group-name': name})
    else:
        getplacements = ec2.get_all_placement_groups()

    placelist = []

    placelist = [placement.name for placement in getplacements]

    if state == 'present':
        if not name:
            module.fail_json(msg="name argument is required when state is present")
        if name in placelist:
            module.exit_json(msg="Placement group already exists with name %s." % name, name=name, strategy=strategy, changed=False)
        else:
            placer = ec2.create_placement_group(name)
        module.exit_json(msg="Placement group %s created." % name, name=name, strategy=strategy, changed=True)

    if state == 'absent':
        if not name:
            module.fail_json(msg="name argument is required when state is absent")
        if name not in placelist:
            module.exit_json(msg="Placement group with name %s not exist. \
                             Nothing to remove." % name, name=name, strategy=strategy, changed=False)
        else:
            placer = ec2.delete_placement_group(name)
        module.exit_json(msg="Placement group %s removed." % name, name=name, strategy=strategy, changed=True)

    if state == 'list':
        module.exit_json(msg="List of all placement groups.", name=placelist, strategy=strategy, changed=False)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

main()
