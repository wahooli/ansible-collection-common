# automation_user

Creates a highly secure system user account for Ansible automation with comprehensive SSH restrictions and command filtering.

## Description

This role creates a dedicated system user account for remote Ansible automation with enterprise-grade security features. The user:

- **Cannot execute interactive shells** (bash, sh, zsh, etc.) via SSH
- **Cannot authenticate with passwords** (password-locked account)
- **Uses SSH key-based authentication only**
- **Has comprehensive command filtering** that blocks dangerous commands
- **Cannot access sensitive system files** directly
- **Has restricted SSH capabilities** (no TTY, no port forwarding, no X11)
- **Can optionally have sudo access** with additional security restrictions
- **Is designed for remote management** from your workstation to servers
- **Prevents privilege escalation** through command restrictions

## Requirements

- Ansible 2.1 or higher
- Target system must have SSH server running
- SSH public keys must be provided
- Bash 4.0+ on target system (for command filtering)

## Role Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `automation_user_name` | Yes | `"ansible"` | Name of the automation user to create |
| `automation_user_ssh_keys` | Yes | `[]` | List of SSH public keys to add to authorized_keys |
| `automation_user_sudo_access` | No | `true` | Whether to grant sudo access without password |
| `automation_user_disable_password_auth` | No | `true` | Whether to enable SSH restrictions and command filtering |
| `automation_user_shell` | No | `"/bin/bash"` | Shell for the automation user (note: interactive access is blocked via SSH) |
| `automation_user_home` | No | `/var/lib/{username}` | Home directory for the automation user |

## Example Playbook

### Basic Usage

```yaml
- hosts: servers
  roles:
    - automation_user
  vars:
    automation_user_name: "deploy"
    automation_user_ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
      - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
```

### With Sudo Access

```yaml
- hosts: servers
  roles:
    - automation_user
  vars:
    automation_user_name: "admin"
    automation_user_ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
    automation_user_sudo_access: true
```

### Disable SSH Restrictions (Not Recommended)

```yaml
- hosts: servers
  roles:
    - automation_user
  vars:
    automation_user_name: "ansible"
    automation_user_ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
    automation_user_disable_password_auth: false
```

### Custom Home Directory

```yaml
- hosts: servers
  roles:
    - automation_user
  vars:
    automation_user_name: "deploy"
    automation_user_ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
    automation_user_home: "/home/deploy"
```

## Security Features

### SSH Restrictions
- **ForceCommand**: All SSH connections execute through a command filter script
- **No TTY Allocation**: Prevents interactive terminal sessions
- **No Port Forwarding**: Disables SSH tunneling and port forwarding
- **No X11 Forwarding**: Prevents X11 display forwarding
- **No Agent Forwarding**: Prevents SSH agent forwarding
- **Password Authentication Disabled**: Only SSH key authentication allowed

### Command Filtering
- **Interactive Shells Blocked**: bash, sh, zsh, tcsh, csh, ksh, dash, fish, screen, tmux
- **Editor Commands Blocked**: vi, vim, nano, pico, emacs, less, more
- **Privilege Escalation Blocked**: su, visudo, passwd, chpasswd
- **Destructive Commands Blocked**: rm, mkfs, fdisk, dd, parted, lvm commands
- **Data Destruction Blocked**: shred, wipe, secure-delete
- **Network Tools Blocked**: nmap, masscan, tcpdump, wireshark
- **Process Manipulation Blocked**: kill, killall, pkill
- **System Recovery Bypass Blocked**: single, emergency, rescue modes

### System Security
- **Password Locked**: Account cannot be accessed via `su` or password
- **System User**: Created as a system user (UID < 1000 on most systems)
- **Restricted Home Directory**: `/var/lib/{username}` with 700 permissions
- **Secure SSH Directory**: `.ssh` directory with 700 permissions
- **Authorized Keys**: Restricted to 600 permissions
- **Sudo Restrictions**: LOGIN_DISABLED prevents interactive sudo access
- **PAM Integration**: `/etc/security/su_disabled_users` prevents `su` access

### Sudo Security
- **NOPASSWD Access**: Sudo access without password when enabled
- **LOGIN_DISABLED**: Prevents interactive sudo sessions
- **Command Restrictions**: Blocks dangerous commands even with sudo
- **Group Restrictions**: Applies to wheel, sudo, and admin groups

## How It Works

1. **User Creation**: Creates a system user with password-locked account
2. **SSH Setup**: Configures SSH keys and restrictive SSH configuration
3. **Command Filtering**: Installs a command filter script that blocks dangerous commands
4. **Sudo Configuration**: Sets up sudo access with security restrictions
5. **PAM Integration**: Configures PAM to prevent `su` access to the automation user
6. **SSH Restart**: Restarts SSH service to apply new configuration

## Security Considerations

- **Command Filtering**: The role blocks many dangerous commands, but this is not a complete security solution
- **Sudo Access**: When enabled, the user can execute any command with sudo (subject to command filtering)
- **SSH Keys**: Ensure SSH private keys are properly secured on your workstation
- **Network Security**: Consider additional network-level security measures
- **Audit Logging**: Monitor SSH and sudo access logs for security events

## Dependencies

None.

## License

MIT
