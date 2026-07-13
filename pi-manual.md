# Manual for operating the Raspberry Pi.

---
### First step: SSH into the pi.

You will need the Pi's **username, hostname, and password**; this info can be found in some login info doc on the club's Google Drive.

In a terminal, run the command with corresponding info:
\
`ssh username@hostname.local`
\
Then enter the password. On success, you should be in the Pi.

---
### Pi Structure

The Pi has various directories, but the one we're interested in is the one called **projects**. It contains the **uoft-vac-discord-bots** directory, which is connected to the GitHub repo.

Any future, non-discord bot related projects with GitHub repos that the club decides to embark one will probably go here as well.

---
### Environments

Every bot must have an **environment file (`.env`)** and a **virtual environment directory (`venv`)**.
- `.env`: stores sensitive data, such as bot tokens.
- `venv`: allows bots to separate their dependencies. Whenever modifying a bot's dependencies, **make sure** you are in its venv.

---
### Systemd Services

Every bot will also have their own **systemd service**, which allows bots to automatically start whenever the Pi boots.
\
A service must be **enabled** to have the bot automatically start.

---
# Instructions

Here are instructions for common scenarios when working with the Pi.
\
Instructions for using particular commands is farther below.

### Setting up a new bot

Make sure the new completed bot directory is on GitHub.
\
Particularly, it must have a driver file and `requirements.txt`.

1. `git pull` and `cd` into the new bot's `bot` directory.

#### 2. Create `.env` in `bot` using the `nano` (see below for details).

Example `.env`:
```
BOT_TOKEN = _

TARGET_CHANNEL_ID = _

```

#### 3. Create `venv` in `bot` and activate it.

Run:
\
`python3 -m venv venv`
\
`source venv/bin/activate`

This will put in you that bot's virtual environment.

#### 4. In the bot's venv, install its dependencies.

Run: `pip install -r requirements.txt`

#### 5. Create a ** systemd service**.

Run `sudo nano /etc/systemd/system/bot-name.service` and paste:
```
[Unit]
Description=Bot Name
After=network.target

[Service]
User=vac
WorkingDirectory=/home/vac/projects/uoft-vac-discord-bots/bot-directory/bot
ExecStart=/home/vac/projects/uoft-vac-discord-bots/bot-directory/bot/venv/bin/python -u driver_file.py
Restart=always

[Install]
WantedBy=multi-user.target
```
- Replace info: Bot Name, bot-directory, driver_file.

#### 6. Enable and start the service.

Run:
\
`sudo systemctl daemon-reload`
\
`sudo systemctl enable bot-name`
\
`sudo systemctl start bot-name`
- Use the same bot-name you used when creating the service.

### Updating an existing bot

Assumes the steps above have been completed for said bot
\
Make sure the bot's directory on GitHub has the desired changes.

1. `git pull`
2. `sudo systemctl restart bot-name`

---
# Prominent Commands

- `sudo reboot`: restarts the entire Pi.
- `source venv/bin/activate`: enter a bot's venv.
    - You'll know you're in a venv if you see `(venv)` at the start of the command line.
- `pip list`: check an environment's libraries.

### `nano`

Used to write contents in a file (and create it, if the file didn't exist beforehand).
\
Run: `nano filepath`
- Arrow keys to navigate.
- Hold shift while navigating to select.
- `ctrl + o` and `enter` to save changes.
- `ctrl + x` to exit.

There are many more operations that you can search online. The ones above are the essentials.

### Service: `systemctl`

- `sudo systemctl daemon-reload`: rereads all service files. Run after editing a service file.
- `sudo systemctl start bot-name`
- `sudo systemctl restart bot-name`
- `sudo systemctl stop bot-name`
- `sudo systemctl enable bot-name`
- `sudo systemctl disable bot-name`
- `systemctl is-enabled bot-name`
- `sudo systemctl status bot-name`: can check whether the bot's service is running, or if startup has failed.
    - Run after `start/restart` to see if the service has started successfully, or after `stop` to check if the service has indeed stopped.

### Logs: `journalctl`

Logs contain prints and errors. Great for debugging.
- `journalctl -u bot-name -f`: display live logs.
- `journalctl -u bot-name -n`: display the most recent 10 logs.
- `journalctl -u bot-name -n <n>`: display the most recent `n` logs.
- `journalctl -u bot-name -b`: display all logs since current boot.
- `journalctl -u bot-name`: display all logs.
    - Too much info. Probably unnecessary.
