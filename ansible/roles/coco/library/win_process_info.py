#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: win_process_info
short_description: Return a list of processes
description:
    - Return a list of processes based on specified criteria.
    - Multiple criteria are AND'd together.
    - For non-Windows targets, use the M(community.general.pids) module instead.
options:
    name:
        description:
            - Select processes whose Name parameter match this name.
        type: str
author:
- Jeff Smith (jeff.smith@constructconnect.com)
'''

EXAMPLES = r'''
- name: Find the processes matching the name
  win_process_info:
    name: svchost
'''

RETURN = r'''
processes:
    description: The list of processes
    returned: always
    type: list
    sample:
      - svchost
'''
