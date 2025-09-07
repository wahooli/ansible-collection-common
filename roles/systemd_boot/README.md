# systemd_boot

An Ansible role to configure systemd-boot bootloader for Arch Linux systems.

## Description

This role configures systemd-boot as the bootloader for Arch Linux systems. It handles the installation, configuration, and management of systemd-boot, including creating boot entries for the main system and fallback options with enhanced security features.

**Key Features**:
- Automatic systemd-boot installation to EFI partition
- Configurable bootloader settings (timeout, editor, auto-entries, console-mode)
- Flexible boot entry configuration with fallback support
- Enhanced security with restrictive file permissions (0700 for directories, 0600 for files)
- Backup of existing bootloader configuration
- Comprehensive verification and testing
- Support for multiple boot entries with custom configurations
- Chroot compatibility for installation scenarios

## Requirements

- Ansible 2.1 or higher
- Target system must be Arch Linux or Arch-based (Manjaro, etc.)
- Target system must have UEFI firmware
- Target system must have an EFI partition mounted at `/boot` (or custom path)
- Root or sudo privileges required
- systemd and efibootmgr packages must be available

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `systemd_boot_chroot_path` | `undefined` | Chroot path for installation scenarios (e.g., `/mnt` for arch-chroot) |
| `systemd_boot_path` | `/boot` | Base path for systemd-boot installation |
| `systemd_boot_loader_path` | `/boot/loader` | Path for loader configuration |
| `systemd_boot_entries_path` | `/boot/loader/entries` | Path for boot entries |
| `systemd_boot_timeout` | `10` | Boot timeout in seconds |
| `systemd_boot_editor` | `false` | Enable boot menu editor |
| `systemd_boot_auto_entries` | `true` | Auto-generate entries for other bootloaders |
| `systemd_boot_auto_firmware` | `true` | Auto-generate entries for firmware |
| `systemd_boot_default_entry` | `@saved` | Default boot entry (can be entry name or @saved) |
| `systemd_boot_console_mode` | `max` | Console mode (0, 1, 2, auto, keep, max) |
| `systemd_boot_entries` | `{}` | Dictionary of boot entries to create |

### Boot Entry Configuration

The `systemd_boot_entries` variable allows you to define multiple boot entries with full customization:

```yaml
systemd_boot_entries:
  arch:
    title: "Arch Linux"
    options: "root=UUID=auto rw"
    linux: /vmlinuz-linux
    initrd:
      - /amd-ucode.img
      - /initramfs-linux.img
    create_fallback: true
  example:
    title: "Example Entry"
    options: "root=UUID=auto rw quiet"
    machine_id: "6a9857a393724b7a981ebb5b8495b9ea"
    version: "3.8.0-2.fc19.x86_64"
    linux: /6a9857a393724b7a981ebb5b8495b9ea/3.8.0-2.fc19.x86_64/linux
    devicetree: /6a9857a393724b7a981ebb5b8495b9ea/3.8.0-2.fc19.x86_64/devicetree
    devicetree_overlay: /6a9857a393724b7a981ebb5b8495b9ea/3.8.0-2.fc19.x86_64/devicetree-overlay
    architecture: x64
    initrd:
      - /amd-ucode.img
      - /initramfs-linux.img
    create_fallback: false
  firmware_updater:
    title: "Firmware updater"
    efi: "/EFI/tools/fwupdx64.efi"
```

## What Gets Installed

### Directories

The role creates the following directory structure with secure permissions:
- `/boot/` - Base boot directory (mode 0700)
- `/boot/loader/` - Loader configuration directory (mode 0700)
- `/boot/loader/entries/` - Boot entries directory (mode 0700)

### Configuration Files

- **`/boot/loader/loader.conf`** - Main bootloader configuration (mode 0600)
- **`/boot/loader/entries/{entry}.conf`** - Boot entry files (mode 0600)
- **`/boot/loader/entries/{entry}-fallback.conf`** - Fallback boot entries (mode 0600)

### Boot Entries

The role creates boot entries based on the `systemd_boot_entries` configuration:

1. **Main Entries**: Each entry defined in `systemd_boot_entries` gets a corresponding `.conf` file
2. **Fallback Entries**: When `create_fallback: true` is set, fallback entries are automatically created with `-fallback` suffix
3. **Automatic Fallback**: Fallback entries automatically replace `initramfs-*.img` with `initramfs-*-fallback.img`

## How It Works

1. **Package Installation**: Ensures systemd and efibootmgr packages are installed
2. **Directory Creation**: Creates necessary directories with secure permissions (0700)
3. **Configuration**: Deploys loader.conf and boot entry files with secure permissions (0600)
4. **Installation**: Installs systemd-boot to the EFI partition using `bootctl install`
5. **Fallback Creation**: Automatically creates fallback entries for specified boot entries
6. **Configuration Update**: Updates bootloader configuration using `bootctl update`
7. **Verification**: Displays bootloader status for confirmation

## Dependencies

- `systemd` package (provides systemd-boot and bootctl)
- `efibootmgr` package (for EFI boot management)
- UEFI firmware support
- EFI partition mounted and accessible

## Example Playbook

### Basic Configuration

```yaml
- hosts: arch_servers
  become: true
  roles:
    - systemd_boot
```

### Custom Configuration

```yaml
- hosts: arch_servers
  become: true
  vars:
    systemd_boot_path: "/boot/efi"
    systemd_boot_timeout: 5
    systemd_boot_editor: false
    systemd_boot_console_mode: "keep"
  roles:
    - systemd_boot
```

### Chroot Installation

For installation scenarios where you need to configure systemd-boot in a chroot environment (e.g., during system installation):

```yaml
- hosts: arch_servers
  become: true
  vars:
    systemd_boot_chroot_path: "/mnt"
    systemd_boot_path: "/boot"
    systemd_boot_entries:
      arch:
        title: "Arch Linux"
        options: "root=UUID=auto rw"
        linux: /vmlinuz-linux
        initrd: /initramfs-linux.img
        create_fallback: true
  roles:
    - systemd_boot
```

**Note**: When `systemd_boot_chroot_path` is set, all operations (package installation, file operations, and bootctl commands) will target the chroot environment using `arch-chroot`.

### Advanced Configuration with Custom Entries

```yaml
- hosts: arch_servers
  become: true
  vars:
    systemd_boot_path: "/boot/efi"
    systemd_boot_entries:
      arch:
        title: "Arch Linux"
        options: "root=UUID=12345678-1234-1234-1234-123456789012 rw quiet"
        linux: /vmlinuz-linux
        initrd:
          - /amd-ucode.img
          - /initramfs-linux.img
        create_fallback: true
      arch_lts:
        title: "Arch Linux LTS"
        options: "root=UUID=12345678-1234-1234-1234-123456789012 rw quiet"
        linux: /vmlinuz-linux-lts
        initrd:
          - /amd-ucode.img
          - /initramfs-linux-lts.img
        create_fallback: true
  roles:
    - systemd_boot
```

### Minimal Configuration

```yaml
- hosts: arch_servers
  become: true
  vars:
    systemd_boot_entries:
      arch:
        title: "Arch Linux"
        options: "root=UUID=auto rw"
        linux: /vmlinuz-linux
        initrd: /initramfs-linux.img
        create_fallback: true
  roles:
    - systemd_boot
```

## Manual Bootloader Management

After the role is deployed, you can manually manage the bootloader:

### Check Bootloader Status

```bash
bootctl status
```

### Update Bootloader Configuration

```bash
bootctl update
```

### Set Default Boot Entry

```bash
bootctl set-default arch
```

### List Boot Entries

```bash
bootctl list
```

### Install/Reinstall systemd-boot

```bash
bootctl install --path=/boot
```

## Boot Entry Customization

The role supports all standard systemd-boot entry options:

### Standard Options

- `title` - Display name for the boot entry
- `options` - Kernel command line options
- `linux` - Path to the Linux kernel
- `initrd` - Path(s) to initramfs files (supports arrays)
- `efi` - Path to EFI application (for non-Linux entries)

### Advanced Options

- `machine_id` - Machine identifier for versioned entries
- `version` - Kernel version for versioned entries
- `devicetree` - Path to device tree blob
- `devicetree_overlay` - Path to device tree overlay
- `architecture` - Target architecture (x64, arm64, etc.)

### Kernel Parameters

Common kernel parameters you might want to add:
- `quiet` - Reduce boot messages
- `nomodeset` - Disable KMS for troubleshooting
- `acpi_osi=Linux` - Fix ACPI issues
- `i915.modeset=0` - Disable Intel graphics modesetting
- `root=UUID=...` - Specify root filesystem by UUID
- `rw` - Mount root filesystem read-write

## Security Features

This role implements several security enhancements:

- **Restrictive Permissions**: All directories use mode 0700, files use mode 0600
- **Secure Paths**: Boot directories are not world-readable
- **Template Security**: All configuration files are templated with proper ownership
- **Fallback Support**: Automatic creation of secure fallback entries

## Troubleshooting

### Boot Issues

- **EFI Partition Not Mounted**: Ensure the EFI partition is properly mounted at `/boot` (or custom path)
- **Permission Issues**: Check that all directories and files have correct ownership and permissions
- **Missing Entries**: Verify `systemd_boot_entries` configuration is correct

### Installation Failures

- **bootctl install fails**: Check EFI partition has sufficient space and is accessible
- **Package installation fails**: Ensure pacman database is up to date
- **Permission denied**: Verify running with root privileges

### Boot Entry Problems

- **Entry not showing**: Check file permissions and syntax in entry files
- **Wrong kernel path**: Verify kernel and initramfs paths exist
- **Boot options not working**: Test kernel command line options manually
- **Fallback not working**: Ensure `create_fallback: true` is set for the entry

### Verification

Use these commands to verify the installation:

```bash
# Check bootloader status
bootctl status

# Verify EFI partition mount
mount | grep boot

# Check boot entries
ls -la /boot/loader/entries/

# Verify configuration files
cat /boot/loader/loader.conf
cat /boot/loader/entries/arch.conf

# Check file permissions
ls -la /boot/loader/
ls -la /boot/loader/entries/
```

## Molecule Testing

This role includes comprehensive Molecule tests for validation:

```bash
cd roles/systemd_boot
molecule test
```

The tests verify:
- Package installation
- Directory creation with correct permissions
- Configuration file deployment
- File permissions and ownership
- Configuration content validation
- Bootloader command functionality
- Fallback entry creation

## Important Notes

- **UEFI Required**: This role only works on UEFI systems, not legacy BIOS
- **EFI Partition**: The EFI partition must be accessible and mountable
- **Security**: All boot directories and files use restrictive permissions
- **Fallback Entries**: Automatically created when `create_fallback: true` is set
- **Container Support**: Automatically detects container environments and adjusts installation parameters
- **Secure Boot**: systemd-boot works with Secure Boot when properly configured

## Security Considerations

- **Secure Permissions**: All configuration files have restrictive permissions (0600)
- **Directory Security**: Boot directories use restrictive permissions (0700)
- **Backup**: Existing configurations are backed up before modification
- **Validation**: Configuration files are validated before deployment
- **Template Security**: All files are templated with proper ownership and permissions

## License

MIT-0

## Author Information

Created by wahooli

## Contributing

When contributing to this role:

1. Follow the existing code style and structure
2. Add appropriate tests for new functionality
3. Update documentation for any new features
4. Ensure all templates are properly configured and secure
5. Test changes with Molecule before submitting
6. Maintain security best practices for file permissions

## Related Roles

- `lvm_autosnapshot` - LVM snapshot management with systemd-boot support
- `archlinux_configure` - General Arch Linux system configuration
- `archlinux_install` - Arch Linux installation automation
