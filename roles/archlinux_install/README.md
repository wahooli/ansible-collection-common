Role Name
=========

ArchLinux installation role with comprehensive support for advanced storage configurations including LUKS encryption, LVM, ZFS, mdraid arrays, and various filesystem types.

Description
-----------

This role automates the complete installation of ArchLinux from the archiso environment. It provides a flexible and powerful approach to disk partitioning, storage management, and system configuration with support for:

- **Advanced Storage**: LUKS encryption, LVM volume management, ZFS pools, mdraid arrays
- **Multiple Filesystems**: Btrfs, ext4, XFS, ZFS with subvolume support
- **Flexible Partitioning**: Dynamic disk-based configuration with custom partition layouts
- **Boot Options**: UEFI with GRUB or systemd-boot support
- **Network Configuration**: systemd-networkd integration
- **Repository Management**: CachyOS repository support with mirror ranking
- **User Management**: Automated user creation and password management

Requirements
------------

- ArchLinux installation media (archiso)
- UEFI-capable system (when using UEFI)
- Target system with appropriate storage devices
- Internet connection for package installation

Role Variables
--------------

### Core Configuration

- `archlinux_install_disks`: **Required** - List of disk configurations for partitioning
- `archlinux_install_uefi`: Enable UEFI installation (default: `true`)
- `archlinux_install_timezone`: System timezone (default: `UTC`)
- `archlinux_install_wipe_drive`: Wipe drives before partitioning (default: `false`)

### Disk Configuration Structure

```yaml
archlinux_install_disks:
  - device: /dev/sda
    wipe: false
    partitions:
      - name: ESP
        start: 0%
        end: 512MiB
        flags: [boot, esp]
        type: primary
      - name: RootFS
        start: 512MiB
        end: 100%
        type: primary
```

### Storage Management

#### LUKS Encryption
- `archlinux_install_dm_crypt`: List of LUKS device configurations
```yaml
archlinux_install_dm_crypt:
  - device: /dev/sda2
    name: cryptroot
    password: "{{ vault_root_password }}"
    force: false
```

#### LVM Configuration
- `archlinux_install_lvm`: List of LVM volume group configurations
```yaml
archlinux_install_lvm:
  - vg: vg0
    devices: [/dev/mapper/cryptroot]
    lvs:
      - name: root
        size: 50G
      - name: home
        size: 100%FREE
```

#### mdraid Arrays
- `archlinux_install_mdadm`: List of mdraid array configurations
```yaml
archlinux_install_mdadm:
  - device: /dev/md0
    level: 1
    name: md0
    members:
      - device: /dev/sda2
      - device: /dev/sdb2
```

#### ZFS Support
- `archlinux_install_zfs_root`: Enable ZFS root filesystem (default: `false`)
- `zfs_zpools`: ZFS pool configurations (when using ZFS)

### Filesystem Configuration

- `archlinux_install_filesystems`: List of filesystem configurations
```yaml
archlinux_install_filesystems:
  - device: /dev/mapper/vg0-root
    fstype: btrfs
    mountpoint: /
    options: defaults,noatime
```

#### Btrfs Subvolumes
- `archlinux_install_btrfs_subvolumes`: List of Btrfs subvolume configurations
```yaml
archlinux_install_btrfs_subvolumes:
  - name: @home
    mountpoint: /home
    options: defaults,noatime
```

### Mount Configuration

- `archlinux_install_mounts`: List of mount point configurations
```yaml
archlinux_install_mounts:
  - device: /dev/mapper/vg0-home
    path: /home
    fstype: btrfs
    options: defaults,noatime
```

### Swap Configuration

- `archlinux_install_swap`: List of swap configurations (files or partitions)
```yaml
archlinux_install_swap:
  - file: /swap/swapfile
    size: 8G
  - partition: /dev/sda3
```

### Package Management

- `archlinux_install_packages`: Override default package list (optional)
- `archlinux_install_additional_packages`: Additional packages to install
- `archlinux_install_kernel`: Kernel package name (default: `linux`)
- `archlinux_install_ucode`: Install microcode updates (default: `true`)
- `archlinux_install_dependencies`: Additional dependencies for archiso environment

### CachyOS Repository Support

- `archlinux_install_enable_cachyos_repositories`: Enable CachyOS repos (default: `false`)
- `archlinux_install_rankmirrors`: Enable mirror ranking (default: `false`)
- `archlinux_install_rankmirrors_count`: Number of mirrors to rank (default: `5`)

### Network Configuration

- `archlinux_install_systemd_networkd`: Enable systemd-networkd (default: `false`)
- `archlinux_install_systemd_networks`: Network interface configurations
- `archlinux_install_ntp_servers`: NTP server list
- `archlinux_install_ntp_fallback_servers`: Fallback NTP servers

### User Management

- `archlinux_install_users`: List of users to create
```yaml
archlinux_install_users:
  - name: admin
    password: "{{ vault_admin_password }}"
    groups: [wheel, network]
    shell: /bin/bash
```
- `archlinux_install_root_password`: Root password hash

### Boot Configuration

- `archlinux_install_systemd_boot_entries`: systemd-boot entry configurations
- `archlinux_install_grub_cmdline`: GRUB command line options
- `archlinux_install_hostname`: System hostname

### Localization

- `archlinux_install_gen_locales`: List of locales to generate
- `archlinux_install_locale_conf`: Locale configuration
- `archlinux_install_vconsole_keymap`: Virtual console keymap

Dependencies
------------

- `community.general` collection for mdadm, parted, lvg, lvol modules
- `ansible.posix` collection for mount module
- `systemd_boot` role (when using systemd-boot)

Example Playbook
----------------

### Basic Installation with LVM and LUKS

```yaml
- hosts: archiso
  roles:
    - role: archlinux_install
      vars:
        archlinux_install_disks:
          - device: /dev/sda
            wipe: false
            partitions:
              - name: ESP
                end: 512MiB
                flags: [boot, esp]
                type: primary
              - name: LUKS
                start: 512MiB
                end: 100%
                type: primary
        
        archlinux_install_dm_crypt:
          - device: /dev/sda2
            name: cryptroot
            password: "{{ vault_root_password }}"
        
        archlinux_install_lvm:
          - vg: vg0
            devices: [/dev/mapper/cryptroot]
            lvs:
              - name: root
                size: 50G
              - name: home
                size: 100%FREE
        
        archlinux_install_filesystems:
          - device: /dev/mapper/vg0-root
            fstype: btrfs
            mountpoint: /
          - device: /dev/mapper/vg0-home
            fstype: btrfs
            mountpoint: /home
        
        archlinux_install_mounts:
          - device: /dev/mapper/vg0-root
            path: /
            fstype: btrfs
          - device: /dev/mapper/vg0-home
            path: /home
            fstype: btrfs
        
        archlinux_install_swap:
          - file: /swap/swapfile
            size: 8G
        
        archlinux_install_users:
          - name: admin
            password: "{{ vault_admin_password }}"
            groups: [wheel, network]
            shell: /bin/bash
```

### ZFS Installation

```yaml
- hosts: archiso
  roles:
    - role: archlinux_install
      vars:
        archlinux_install_zfs_root: true
        archlinux_install_enable_cachyos_repositories: true
        
        zfs_zpools:
          - name: zroot
            devices: [/dev/sda2, /dev/sdb2]
            raid_level: mirror
            properties:
              ashift: 12
        
        archlinux_install_filesystems:
          - device: zroot/ROOT/default
            fstype: zfs
            mountpoint: /
        
        archlinux_install_mounts:
          - device: zroot/ROOT/default
            path: /
            fstype: zfs
```

### mdraid Installation

```yaml
- hosts: archiso
  roles:
    - role: archlinux_install
      vars:
        archlinux_install_disks:
          - device: /dev/sda
            partitions:
              - name: ESP
                end: 512MiB
                flags: [boot, esp]
              - name: RAID
                start: 512MiB
                end: 100%
                flags: [raid]
          - device: /dev/sdb
            partitions:
              - name: ESP
                end: 512MiB
                flags: [boot, esp]
              - name: RAID
                start: 512MiB
                end: 100%
                flags: [raid]
        
        archlinux_install_mdadm:
          - device: /dev/md0
            level: 1
            name: md0
            members:
              - device: /dev/sda2
              - device: /dev/sdb2
        
        archlinux_install_filesystems:
          - device: /dev/md0
            fstype: btrfs
            mountpoint: /
        
        archlinux_install_mounts:
          - device: /dev/md0
            path: /
            fstype: btrfs
```

### Network Configuration with systemd-networkd

```yaml
- hosts: archiso
  roles:
    - role: archlinux_install
      vars:
        # ... disk configuration ...
        
        archlinux_install_systemd_networkd: true
        archlinux_install_systemd_networks:
          "00-default-dhcp":
            match:
              name: "*"
            network:
              DHCP: "yes"
              dhcp4: true
              dhcp6: false
              LinkLocalAddressing: "ipv4"
              MulticastDNS: true
              IPv6AcceptRA: true
          "10-static-eth0":
            match:
              name: "eth0"
            network:
              address:
                - address: "192.168.1.100/24"
              route:
                - destination: "0.0.0.0/0"
                  gateway: "192.168.1.1"
              dns:
                - "8.8.8.8"
                - "8.8.4.4"
```

Testing
--------

The role includes comprehensive testing with Molecule:

- **Default scenario**: Basic installation testing
- **mdadm scenario**: RAID array testing

To run tests:

```bash
cd roles/archlinux_install
molecule test
```

License
-------

MIT

Author Information
------------------

Created by wahooli - A comprehensive ArchLinux installation automation role supporting advanced storage configurations and modern system management practices.
