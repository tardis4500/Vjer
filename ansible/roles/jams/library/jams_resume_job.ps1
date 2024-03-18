#!powershell

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#AnsibleRequires -CSharpUtil Ansible.Basic

Import-Module JAMS

<#
  .SYNOPSIS
  Finds the proper status to pause all jobs so deployment can proceed without impacting on Jams jobs.

  .DESCRIPTION
  Based on the given Server, it will perform a call to recover Job-Entries from JAMS.
  The result will be filtered by using a criteria based on the 'jobName', 'methodId' and 'currentState' fields.
  All this process will be enclosed in a loop until to find the proper status, then the Jams resource will be paused.
#>

$spec = @{
    options             = @{
        jams_resource_name = @{ type = 'str'; required = $true }
    }
    supports_check_mode = $true
}

$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)
$server = 'localhost'
$jams_job_quantity_available = 999999
$jams_resource_name = $module.Params.jams_resource_name

## Verify ResourceName has the prefix Pipeline_, reject otherwise

$resource = Get-Item JAMS::$server\Resources\$jams_resource_name
$resource.QuantityAvailable = $jams_job_quantity_available
$resource.Update()

$module.Result.changed = $true

$module.ExitJson()
