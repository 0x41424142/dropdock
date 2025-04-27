# DropDock - Automatic Spamhaus Project DROP List to Pihole

This repo contains `DockDrop`, a Docker container that runs on a daily basis to download the Spamhaus DROP domain list and update your Pihole's blocklist.

Stale domains are automatically removed and new ones are added.

Logs are rotated once they reach 10MB in size. 5 rotated logs are kept.

## Environment Variables

Place the following in `./.env` if you need custom values:

```
PIHOLE_URL=<YOUR_PIHOLE_URL> # optional, default is http://pi.hole/api
PIHOLE_PW=<YOURPASSWORD> # optional - you may not have a password set on your Pihole
PIHOLE_GROUPS=<COMMA-SEPARATED-GROUP-NAMES> # optional to only apply domains to specific group names
LOG_LEVEL # optional, default is INFO, can be INFO or DEBUG
```

## Build the Container

```bash
docker build -t dockdrop .
```

## Run the Container

```bash
docker run -d \
  --name dockdrop \
  dockdrop
```

## Run on a Schedule

You can use an OS scheduler to run the container on a schedule. For example, to run it every day at 3 AM:

# On Linux/MacOS

```bash
crontab crontabjob
```

# On Windows

```powershell
$action = New-ScheduledTaskAction -Execute "docker" -Argument "run --rm dockdrop"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
$task = New-ScheduledTask -Action $action -Trigger $trigger -RunLevel Highest
Register-ScheduledTask -TaskName "DockDrop" -InputObject $task
```
