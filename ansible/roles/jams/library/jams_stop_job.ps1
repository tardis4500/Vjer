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
        jams_job_prefix = @{ type = 'str'; required = $true }
        jams_loop_delay = @{ type = 'int'; required = $false; default = 60 }
    }
    supports_check_mode = $true
}

$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)
$server = 'localhost'
$jams_resource_name = $module.Params.jams_resource_name
$jams_job_prefix = $module.Params.jams_job_prefix
$jams_loop_delay = $module.Params.jams_loop_delay

$resource = Get-Item JAMS::$server\Resources\$jams_resource_name
$resource.QuantityAvailable = 0
$resource.Update()

$filteredJobs = 9999
# Doing extra call since the first time it returns empty which could provide a false positive
Get-JAMSEntry -Server $server | Where-object { $_.jobName -like $jams_job_prefix -and $_.methodId -ne 24 -and $_.methodId -ne 27 -and $_.currentState -eq "Executing" }
while ($filteredJobs -gt 0)
{
    $parentJobs = Get-JAMSEntry -Server $server | Where-object { $_.jobName -like $jams_job_prefix -and $_.methodId -ne 24 -and $_.methodId -ne 27 -and $_.currentState -eq "Executing" }
    $filteredJobs = $parentJobs.Count
    if ($filteredJobs -ne 0)
    {
      Start-Sleep -Seconds $jams_loop_delay
    }
}

$module.Result.changed = $true

$module.ExitJson()
