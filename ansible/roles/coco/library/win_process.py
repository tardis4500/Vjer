#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2014, Chris Hoffman <choffman@chathamfinancial.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: win_process
short_description: Manage Windows processes
description:
- Manage and query Windows processes.
options:
  name:
    description:
    - The name of the process to manage.
    type: str
  state:
    description:
    - The desired state of the process.
    type: str
    choices:
    - present
    - absent
    default: present
author:
- Jeff Smith (@jeff.smith@constructconnect.com)
'''

EXAMPLES = r'''
- name: Check that a process exists
  win_process:
    name: notepad
    state: present

- name: Stop the specified process
  win_process:
    name: notepad
    state: absent
'''

RETURN = r'''
processes:
    description: A list of the stopped processes.
    returned: success
    type: complex
'''
