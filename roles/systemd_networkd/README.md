# systemd_networkd

An Ansible role to configure systemd-networkd for network management on Linux systems.

## Description

This role configures systemd-networkd, which is a system daemon that manages network configurations. It provides a declarative way to configure network interfaces, DHCP settings, static IP addresses, routing, and other network-related configurations.

**Key Feature**: The role uses dynamic templates that automatically generate INI configuration files from YAML data structures. This means **new configuration options are automatically supported without requiring template updates**.

## Requirements

- Ansible 2.1 or higher
- Target system must use systemd as init system
- Target system must have systemd-networkd available
- Root or sudo privileges required

## Role Variables

### Chroot Mode Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `systemd_networkd_chroot_path` | `null` | Path prefix for chroot mode (e.g., `/mnt` for arch-chroot) |

**Note**: When `systemd_networkd_chroot_path` is defined:
- Package installation is handled via `arch-chroot` commands
- Service management is handled via `arch-chroot` commands  
- All file paths should be set to include the chroot prefix (e.g., `/mnt/etc/systemd/network`)
- Host system operations (like package facts) are skipped

### Main Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `systemd_networkd_enabled` | `true` | Enable systemd-networkd service |
| `systemd_networkd_config_dir` | `/etc/systemd/network` | Configuration directory |

### Network Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `systemd_networkd_networks` | `{}` | Dictionary of network configurations |
| `systemd_networkd_netdevs` | `{}` | Dictionary of netdev configurations |
| `systemd_networkd_links` | `{}` | Dictionary of link configurations |

### Systemd-Resolved Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `systemd_networkd_resolved_conf` | `{}` | Main resolved.conf configuration |
| `systemd_networkd_resolved_confd` | `{}` | Dictionary of resolved.conf.d configurations |

### Backup and Cleanup

| Variable | Default | Description |
|----------|---------|-------------|
| `systemd_networkd_backup` | `true` | Backup existing configurations |
| `systemd_networkd_backup_dir` | `/etc/systemd/network/backup` | Backup directory |
| `systemd_networkd_cleanup_orphan_config` | `true` | Remove orphaned Ansible-managed configurations |

## Configuration Structure

The role uses a clean, organized variable structure that maps directly to systemd-networkd configuration files:

### Network Configuration (`systemd_networkd_networks`)

Each key in the dictionary becomes a `.network` file. The structure follows systemd-networkd's INI format:

```yaml
systemd_networkd_networks:
  eth0:                    # Creates eth0.network
    match:
      name: "eth0"
    network:
      DHCP: "yes"
      LinkLocalAddressing: "ipv4"
    address:
      - address: "192.168.1.100/24"
    route:
      - destination: "0.0.0.0/0"
        gateway: "192.168.1.1"

  default:                 # Creates default.network
    match:
      name: "*"
    network:
      DHCP: "yes"
```

### NetDev Configuration (`systemd_networkd_netdevs`)

Each key becomes a `.netdev` file for virtual network devices:

```yaml
systemd_networkd_netdevs:
  bond0:                   # Creates bond0.netdev
    NetDev:
      name: "bond0"
      kind: "bond"
    bond:
      mode: "active-backup"
      up_delay: 200

  br0:                     # Creates br0.netdev
    NetDev:
      name: "br0"
      kind: "bridge"
    bridge:
      STP: true
```

### Link Configuration (`systemd_networkd_links`)

Each key becomes a `.link` file for link-level settings:

```yaml
systemd_networkd_links:
  eth0:                    # Creates eth0.link
    match:
      name: "eth0"
    link:
      MTU: 1500
      Speed: 1000
      Duplex: "full"
```

### Systemd-Resolved Configuration

The role also manages systemd-resolved configuration:

```yaml
systemd_networkd_resolved_conf:      # Main /etc/systemd/resolved.conf
  Resolve:
    DNS: ["1.1.1.1", "1.0.0.1"]
    FallbackDNS: ["8.8.8.8", "8.8.4.4"]

systemd_networkd_resolved_confd:     # /etc/systemd/resolved.conf.d/*.conf files
  enable-multicast-dns:
    Resolve:
      MulticastDNS: true
  fallback-dns:
    Resolve:
      FallbackDNS: "1.1.1.1#cloudflare-dns.com 9.9.9.9#dns.quad9.net"
```

### Key Benefits

1. **Direct mapping**: Variable names become filenames
2. **Flexible structure**: Supports any systemd-networkd configuration option
3. **Automatic file management**: Creates, updates, and removes files as needed
4. **Idempotent**: Safe to run multiple times
5. **Clean separation**: Network, netdev, and link configurations are clearly separated

## Dependencies

None.

## Example Playbook

### Basic Configuration

```yaml
- hosts: servers
  become: true
  roles:
    - systemd_networkd
```

### Advanced Configuration with Current Variable Structure

```yaml
- hosts: servers
  become: true
  vars:
    systemd_networkd_networks:
      eth0:
        match:
          name: "eth0"
        network:
          DHCP: "yes"
          LinkLocalAddressing: "ipv4"
          MulticastDNS: "yes"
        address:
          - address: "192.168.1.100/24"
        route:
          - destination: "0.0.0.0/0"
            gateway: "192.168.1.1"
            metric: 100

      default:
        match:
          name: "*"
        network:
          DHCP: "yes"
          LinkLocalAddressing: "ipv4"
          MulticastDNS: "yes"

    systemd_networkd_netdevs:
      bond0:
        NetDev:
          name: "bond0"
          kind: "bond"
        bond:
          mode: "active-backup"
          mii_monitor_interval: 100
          up_delay: 200
          down_delay: 200

    systemd_networkd_links:
      eth0:
        match:
          name: "eth0"
        link:
          MTU: 1500
          Speed: 1000
          Duplex: "full"
          WakeOnLan: true

    systemd_networkd_resolved_conf:
      Resolve:
        DNS: ["1.1.1.1", "1.0.0.1"]
        FallbackDNS: ["8.8.8.8", "8.8.4.4"]
        MulticastDNS: true

    systemd_networkd_resolved_confd:
      enable-multicast-dns:
        Resolve:
          MulticastDNS: true
  roles:
    - systemd_networkd
```

### Link Configuration Example

```yaml
- hosts: servers
  become: true
  vars:
    systemd_networkd_links:
      eth0:
        match:
          name: "eth0"
        link:
          MTU: 1500
          Speed: 1000
          Duplex: "full"
          WakeOnLan: true
          AutoNegotiation: true
          FlowControl: true
          PauseAutoneg: true
          AsymmetricPause: false
  roles:
    - systemd_networkd
```

## Chroot Mode Usage

The role supports chroot mode for installation scenarios (e.g., during Arch Linux installation):

```yaml
- hosts: install_host
  become: true
  vars:
    systemd_networkd_chroot_path: /mnt
    
    systemd_networkd_networks:
      eth0:
        match:
          name: "eth0"
        network:
          DHCP: "yes"
          LinkLocalAddressing: "ipv4"
        address:
          - address: "192.168.1.100/24"
        route:
          - destination: "0.0.0.0/0"
            gateway: "192.168.1.1"
  roles:
    - systemd_networkd
```

**Important**: In chroot mode, the role automatically:
- Uses `arch-chroot` for package installation and service management
- Prefixes all file paths with the chroot path
- Skips host system operations that aren't applicable

## Cleanup Functionality

The role includes automatic cleanup of orphaned Ansible-managed configurations. This is **enabled by default** and will remove existing Ansible-managed configurations that are no longer defined in your playbook.

To disable cleanup of orphaned configurations:

```yaml
- hosts: servers
  become: true
  vars:
    systemd_networkd_cleanup_orphan_config: false  # Disable cleanup of orphaned configurations
  roles:
    - systemd_networkd
```

**How it works**:
- Only removes files containing "# Managed by Ansible" in the first line
- Automatically backs up existing configurations before removal
- Removes network, netdev, link, and resolved configuration files
- **Excludes files currently defined in variables** for better idempotence
- Restarts services after cleanup
- Preserves manually created configurations

**Use cases**:
- Removing role-managed configurations when switching to manual management
- Cleaning up test environments
- Preparing systems for different network management tools
- Maintaining clean configuration state

**Idempotence behavior**:
- Files currently defined in `systemd_networkd_networks`, `systemd_networkd_netdevs`, `systemd_networkd_links`, and `systemd_networkd_resolved_confd` are **never removed** during cleanup
- This ensures that running the role multiple times with the same configuration won't cause unnecessary file removal and recreation
- Only "orphaned" Ansible-managed files (those no longer defined in variables) are removed

## Benefits of the Current Approach

1. **Clean organization**: Network, netdev, and link configurations are clearly separated
2. **Direct mapping**: Variable names directly correspond to configuration files
3. **Flexible structure**: Supports any systemd-networkd configuration option
4. **Automatic cleanup**: Removes orphaned configurations for clean state management
5. **Idempotent**: Safe to run multiple times without side effects
6. **Comprehensive**: Manages both systemd-networkd and systemd-resolved
7. **Well-tested**: Comprehensive Molecule tests across multiple platforms

## Molecule Testing

This role includes comprehensive Molecule tests for multiple platforms:

- **Debian 12** (systemd-networkd only)
- **Ubuntu 22.04** (systemd-networkd + systemd-resolved)
- **Arch Linux** (systemd-networkd + systemd-resolved)
- **CentOS Stream 9** (systemd-resolved only)

The tests include:
- **Prepare phase**: Creates test configurations to verify cleanup functionality
- **Converge phase**: Applies the role configuration with cleanup enabled
- **Verify phase**: Validates that configurations are correct and orphaned files were cleaned up

To run the tests:

```bash
cd roles/systemd_networkd
molecule test
```

To run individual phases:

```bash
molecule converge    # Apply configuration
molecule verify      # Verify configuration
molecule cleanup     # Clean up test environment
```

## License

MIT-0

## Author Information

Created by wahooli
