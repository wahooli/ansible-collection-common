# Borg Backup Role

This role configures Borg Backup using systemd service instances with the `@` syntax, allowing multiple backup configurations to run independently.

## Features

- Uses systemd service instances (`borg-backup@instance.service`) for flexible backup configuration
- Configuration files stored in `/etc/conf.d/borg-backup/`
- Each backup instance can have its own schedule, source directories, and settings
- Automatic timer creation and management (daily and weekly schedules)
- Support for multiple source directories per backup instance
- Built-in pruning and repository checking

## Configuration

### Default Variables

```yaml
# Base backup configuration
borg_backup_default_schedule: daily
borg_backup_cache_dir: /var/cache/borg-backup
borg_backup_base_config_dir: /var/lib/borg-backup/security
borg_backup_config_dir: /etc/conf.d/borg-backup

# Default borg arguments
borg_backup_default_create_args: "--verbose --stats --show-rc --compression zstd,3 --one-file-system"
borg_backup_default_prune_args: "--keep-daily 7 --keep-weekly 4 --keep-monthly 3"
borg_backup_default_check_args: "--verbose"
borg_backup_default_archive_name: "{now}"

# List of backup instances to configure
borg_backup_instances:
  - name: home
    source_dirs:
      - /home
      - /etc
    schedule:
      - daily
      - weekly
    repository: /var/backup/borg/home-backup
    compression: lz4
    stats: true
  
  - name: opt
    source_dirs:
      - /opt
    schedule:
      - weekly
    repository: ssh://borg@borg-server.example.com/opt-backup
    passphrase: "your-secret-passphrase"
    compression: lz4
    stats: true
```

### Instance Configuration Options

Each backup instance supports the following options:

- `name`: Unique identifier for the backup instance (used in systemd service names)
- `source_dirs`: List of directories to backup (supports multiple directories)
- `schedule`: List of schedules (daily, weekly, or both)
- `repository`: Borg repository path (local or remote SSH)
- `passphrase`: Encryption passphrase (optional, enables encrypted repos)
- `compression`: Compression algorithm (default: zstd,3)
- `stats`: Whether to show statistics (default: true)
- `create_args`: Custom arguments for borg create command
- `prune_args`: Custom arguments for borg prune command
- `check_args`: Custom arguments for borg check command
- `archive_name`: Custom archive naming pattern (default: {now})

## Usage

### Manual Backup Execution

To run a backup manually for a specific instance:

```bash
# Run home backup
sudo systemctl start borg-backup@home.service

# Run opt backup
sudo systemctl start borg-backup@opt.service
```

### Check Service Status

```bash
# Check status of all instances
sudo systemctl status borg-backup@*.service

# Check specific instance
sudo systemctl status borg-backup@home.service
```

### View Logs

```bash
# View logs for specific instance
sudo journalctl -u borg-backup@home.service

# Follow logs in real-time
sudo journalctl -u borg-backup@home.service -f
```

### Timer Management

```bash
# Check timer status
sudo systemctl status borg-backup-daily@*.timer
sudo systemctl status borg-backup-weekly@*.timer

# Enable/disable specific timers
sudo systemctl enable borg-backup-daily@home.timer
sudo systemctl disable borg-backup-weekly@opt.timer
```

## File Structure

After deployment, the following files will be created:

- `/etc/systemd/system/borg-backup@.service` - Service template
- `/etc/systemd/system/borg-backup-daily@.timer` - Daily timer template
- `/etc/systemd/system/borg-backup-weekly@.timer` - Weekly timer template
- `/etc/conf.d/borg-backup/` - Configuration directory
  - `/etc/conf.d/borg-backup/home` - Home backup configuration
  - `/etc/conf.d/borg-backup/opt` - Opt backup configuration

## Configuration Files

Each backup instance gets a configuration file in `/etc/conf.d/borg-backup/` containing:

```bash
# Borg Backup Configuration for home
BORG_REPO='/var/backup/borg/home-backup'
BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK=yes
BORG_ARCHIVE_NAME='{now}'
BORG_BACKUP_SOURCE_DIRS='/home /etc'
BORG_CREATE_ARGS='--verbose --stats --show-rc --compression zstd,3 --one-file-system'
BORG_PRUNE_ARGS='--keep-daily 7 --keep-weekly 4 --keep-monthly 3'
BORG_CHECK_ARGS='--verbose'
```

## Adding New Backup Instances

To add a new backup instance, simply add it to the `borg_backup_instances` list in your playbook variables:

```yaml
borg_backup_instances:
  - name: var
    source_dirs:
      - /var
      - /tmp
    schedule:
      - daily
    repository: /var/backup/borg/var-backup
    compression: lz4
    stats: false
```

The role will automatically create the necessary configuration files and systemd units.

## OS Support

This role supports multiple operating system families:

- **Debian/Ubuntu**: Uses `apt` package manager
- **RedHat/CentOS/Fedora**: Uses `yum`/`dnf` package managers with EPEL
- **Arch Linux**: Uses `pacman` package manager

## Security Features

- Runs as root user with restricted permissions
- Protects system directories and kernel modules
- Private temporary directories and devices
- No new privileges execution
- Configurable encryption support via passphrases
