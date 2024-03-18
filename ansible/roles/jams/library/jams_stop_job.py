#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: jams_stop_job
short_description: Disable a JAMS job
description:
    - Disable the specified JAMS job and wait for running jobs to complete.
options:
    jams_resource_name:
        description:
            - The name of the JAMS resource to disable.
        type: str
    jams_job_prefix:
        description:
            - The glob string to use to find running jobs for which to wait.
        type: str
    jams_loop_delay:
        description:
            - The number of seconds to wait between checks. (default=60)
        type: str
author:
- Felipe Canaviri (felipe.canaviri@constructconnect.com)
'''

EXAMPLES = r'''
- name: Stop the JAMS job
  jams_stop_job:
    jams_resource_name: my-job-name
    jams_job_prefix: my_jobs_*
    jams_loop_delay: 5
'''

RETURN = r'''
Nothing
'''
