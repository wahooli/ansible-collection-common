# lvm_autosnapshot

An Ansible role to set up automatic LVM snapshotting as a pacman hook for Arch Linux systems.

## Description

This role configures automatic LVM snapshot creation before package operations (install, upgrade, remove) on Arch Linux systems. It creates snapshots of the root logical volume and backs up boot files to enable system rollback in case of issues after package updates.

**Key Features**:
- Automatic LVM snapshot creation before pacman operations
- Boot file backup and bootloader entry creation for snapshots
- System rollback capability using LVM snapshots
- MOTD status display showing snapshot information
- Cleanup and management scripts for snapshot lifecycle

## Requirements

- Ansible 2.1 or higher
- Target system must be Arch Linux or Arch-based (Manjaro, etc.)
- Target system must use LVM with a volume group and root logical volume
- Root or sudo privileges required
- LVM2 package must be available

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `lvm_autosnapshot_name` | `auto_snapshot` | Name for the LVM snapshot logical volume |
| `lvm_autosnapshot_suffix` | `-snapshot` | Suffix added to boot files and bootloader entries |
| `lvm_autosnapshot_script_install_path` | `/usr/local/sbin/` | Directory where snapshot management scripts are installed |
| `lvm_autosnapshot_target_vg` | `vg0` | Target volume group name |
| `lvm_autosnapshot_target_lv` | `lv_root` | Target logical volume name (usually root) |
| `lvm_autosnapshot_bootloader` | `systemd-boot` | Bootloader type (currently only systemd-boot supported) |
| `lvm_autosnapshot_systemd_boot_path` | `/boot/loader/entries` | Path to systemd-boot entries directory |
| `lvm_autosnapshot_status_file` | `/run/motd_snapshot_status` | Status file for MOTD display |

## What Gets Installed

### Scripts

The role installs several management scripts to `/usr/local/sbin/`:

- **`create-root-snapshot`**: Creates LVM snapshot and backs up boot files
- **`remove-root-snapshot`**: Removes existing snapshot and cleans up boot files
- **`rollback-root-snapshot`**: Rolls back system to snapshot state
- **`check-root-snapshot`**: Checks snapshot status (used by MOTD)

### Pacman Hook

A pacman hook (`/etc/pacman.d/hooks/99-lvm-snapshot.hook`) is installed that:
- Triggers on package install, upgrade, and remove operations
- Runs before the transaction begins
- Creates a snapshot of the root logical volume
- Backs up boot files and creates bootloader entries
- Aborts the pacman operation if snapshot creation fails

### MOTD Integration

A script (`/etc/profile.d/motd-snapshot-status.sh`) is installed that:
- Displays snapshot status in the message of the day
- Shows when the last snapshot was created
- Indicates if a snapshot is available for rollback

### Sudo Configuration

Sudo access is configured for the `check-root-snapshot` script to allow non-root users to check snapshot status.

## How It Works

1. **Before Package Operations**: When you run `pacman -Syu` or similar commands, the pacman hook triggers
2. **Snapshot Creation**: The hook creates an LVM snapshot of your root logical volume
3. **Boot File Backup**: Boot files (vmlinuz, initramfs) are copied with snapshot suffixes
4. **Bootloader Entries**: New bootloader entries are created pointing to the snapshot
5. **Package Operation**: Pacman proceeds with the package installation/upgrade
6. **Rollback Option**: If something goes wrong, you can boot into the snapshot to rollback

## Dependencies

- `lvm2` package (automatically installed if missing)
- LVM volume group and logical volume setup
- systemd-boot (currently supported bootloader)

## Example Playbook

### Basic Configuration

```yaml
- hosts: arch_servers
  become: true
  roles:
    - lvm_autosnapshot
```

### Custom Configuration

```yaml
- hosts: arch_servers
  become: true
  vars:
    lvm_autosnapshot_target_vg: "system"
    lvm_autosnapshot_target_lv: "root"
    lvm_autosnapshot_name: "pre_update_snapshot"
    lvm_autosnapshot_suffix: "-backup"
    lvm_autosnapshot_script_install_path: "/usr/local/bin/"
  roles:
    - lvm_autosnapshot
```

## Manual Snapshot Management

After the role is deployed, you can manually manage snapshots:

### Create a Snapshot

```bash
sudo /usr/local/sbin/create-root-snapshot
```

### Remove a Snapshot

```bash
sudo /usr/local/sbin/remove-root-snapshot
```

### Rollback to Snapshot

```bash
sudo /usr/local/sbin/rollback-root-snapshot
```

### Check Snapshot Status

```bash
sudo /usr/local/sbin/check-root-snapshot
```

## Rollback Process

To rollback your system:

1. **Boot into Snapshot**: Select the snapshot entry from your bootloader menu
2. **Verify System State**: Check that the system is working correctly
3. **Run Rollback Script**: Execute the rollback script from the snapshot environment
4. **Reboot**: Reboot to return to the main system

## Important Notes

- **Space Requirements**: LVM snapshots require sufficient free space in the volume group
- **Performance Impact**: Snapshots may slightly impact I/O performance
- **Cleanup**: Old snapshots should be removed periodically to free up space
- **Bootloader Support**: Currently only systemd-boot is fully supported
- **Hook Behavior**: The pacman hook will abort operations if snapshot creation fails

## Troubleshooting

### Snapshot Creation Fails

- Check available space in the volume group: `vgs`
- Verify LVM setup: `lvs` and `vgs`
- Check script permissions and paths
- Review pacman hook configuration

### Boot Issues

- Verify bootloader entries were created correctly
- Check that boot files were copied with proper suffixes
- Ensure snapshot logical volume is active: `lvchange -ay`

### MOTD Not Showing

- Check script permissions in `/etc/profile.d/`
- Verify sudo configuration for status checking
- Check that the status file is being updated

## Molecule Testing

This role includes Molecule tests for validation:

```bash
cd roles/lvm_autosnapshot
molecule test
```

## License

MIT-0

## Author Information

Created by wahooli

## Contributing

When contributing to this role:

1. Follow the existing code style and structure
2. Add appropriate tests for new functionality
3. Update documentation for any new features
4. Ensure all scripts are properly templated and configurable
