#!powershell

# Copyright: (c) 2016, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#AnsibleRequires -CSharpUtil Ansible.Basic
#Requires -Module Ansible.ModuleUtils.LinkUtil

$spec = @{
    options             = @{
        name = @{ type = "str"; required = $true }
    }
    supports_check_mode = $true
}

$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

$module.Result.processes = try {
    Get-Process -Name $module.Params.name -ErrorAction Stop
}
catch [Microsoft.PowerShell.Commands.ProcessCommandException] {
    @()
}

$module.ExitJson()
