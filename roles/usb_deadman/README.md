USB Deadman Switch
==================

This role implements a USB deadman switch system that automatically shuts down the system when specific USB devices (identified by disk labels) are removed. This is particularly useful for security-sensitive systems where physical access control is important.

The role creates a complete deadman switch system using:
- A shutdown script that handles the actual shutdown logic
- Systemd service templates that get triggered by udev events
- Udev rules that monitor for USB device removal
- Sysctl configuration to enable required kernel functionality

Requirements
------------

- Linux system with systemd
- Udev support
- Root privileges (role uses `become: true`)
- USB devices with filesystem labels to monitor

Role Variables
--------------

Available variables are listed below, along with default values (see `defaults/main.yaml`):

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `usb_deadman_systemd_dir` | `/etc/systemd/system` | Directory for systemd service files |
| `usb_deadman_script` | `/usr/local/bin/deadman-shutdown` | Path to the shutdown script |
| `usb_deadman_sysctl_file` | `/etc/sysctl.d/99-usb-deadman.conf` | Path to sysctl configuration file |
| `usb_deadman_monitor_disk_labels` | `[]` | List of disk labels to monitor for removal |

### Example Configuration

```yaml
# Monitor multiple USB devices
usb_deadman_monitor_disk_labels:
- "BACKUP"
- "SECURE"

# Custom script location
usb_deadman_script: "/opt/scripts/deadman-shutdown"
```

Dependencies
------------

None. This role is self-contained and does not depend on other roles.

How It Works
------------

1. **Udev Monitoring**: The role creates udev rules that monitor for removal of block devices with specific filesystem labels
2. **Systemd Integration**: When a monitored device is removed, udev triggers a systemd service
3. **Grace Period**: The shutdown script includes a 3-second grace period to handle accidental disconnections
4. **Safe Shutdown**: The script performs a fast, safe shutdown by:
   - Remounting filesystems read-only (prevents corruption)
   - Dropping caches
   - Initiating systemd poweroff with inhibitors ignored

Example Playbook
----------------

### Basic Usage

```yaml
- hosts: servers
  become: true
  vars:
    usb_deadman_monitor_disk_labels:
    - "CRYPTKEY"
  roles:
    - usb_deadman
```

### Advanced Usage

```yaml
- hosts: security_servers
  become: true
  vars:
    usb_deadman_monitor_disk_labels:
    - "BACKUP_KEY"
    - "ADMIN_KEY"
    usb_deadman_script: "/opt/security/deadman-shutdown"
  roles:
    - usb_deadman
```

### Setting Up USB Devices

To use this role, you need USB devices with specific filesystem labels:

```bash
# Create a filesystem with a specific label
mkfs.ext4 -L CRYPTKEY /dev/sdX1

# Or change an existing filesystem label
e2label /dev/sdX1 CRYPTKEY
```

Testing
-------

The role includes comprehensive molecule tests that verify:
- All required files are created with correct permissions
- Systemd services are properly configured
- Udev rules are correctly generated
- Sysctl parameters are set correctly
- Script content matches expectations

Run tests with:
```bash
cd roles/usb_deadman
molecule test
```

Security Considerations
-----------------------

- The deadman switch provides physical security by ensuring systems shut down when USB keys are removed
- The 3-second grace period helps prevent accidental shutdowns from brief disconnections
- The shutdown process is designed to be fast and safe, minimizing data corruption risk
- Only devices with the specified labels will trigger the shutdown mechanism

Troubleshooting
---------------

### Check if udev rules are loaded:
```bash
udevadm test-builtin path_id /dev/null
```

### Verify systemd service is recognized:
```bash
systemctl list-unit-files | grep deadman
```

### Check sysctl configuration:
```bash
sysctl kernel.sysrq
cat /etc/sysctl.d/99-usb-deadman.conf
```

### Test the shutdown script manually:
```bash
/usr/local/bin/deadman-shutdown CRYPTKEY
```

License
-------

BSD

Author Information
------------------

This role is part of the ansible-collection-common project.
