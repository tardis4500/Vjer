#!powershell

# Copyright: (c) 2014, Chris Hoffman <choffman@chathamfinancial.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#AnsibleRequires -CSharpUtil Ansible.Basic

$spec = @{
    options             = @{
        name  = @{ type = 'str'; required = $true }
        state = @{ type = 'str'; choices = 'present', 'absent'; default = 'present' }
    }
    supports_check_mode = $true
}

$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

$name = $module.Params.name
$state = $module.Params.state

try {
    if ($state -eq 'present') {
        $module.Result.processes = Get-Process -Name $name -ErrorAction Stop
    }
    else {
        $module.Result.processes = Stop-Process -Name $name -Force -PassThru -ErrorAction Stop
        $module.Result.changed = $true
    }
}
catch [Microsoft.PowerShell.Commands.ProcessCommandException] {
    if ($state -eq 'present') { $module.FailJson("No process found", $_) }
    $module.Result.processes = @()
}

$module.ExitJson()
