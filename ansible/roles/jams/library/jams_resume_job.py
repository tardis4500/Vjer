#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: jams_resume_job
short_description: Re-enable a JAMS job
description:
    - Re-enables the specified JAMS job.
options:
    jams_resource_name:
        description:
            - The name of the JAMS resource to re-enable.
        type: str
author:
- Felipe Canaviri (felipe.canaviri@constructconnect.com)
'''

EXAMPLES = r'''
- name: Resume the JAMS job
  jams_resume_job:
    jams_resource_name: my-job-name
'''

RETURN = r'''
Nothing
'''
