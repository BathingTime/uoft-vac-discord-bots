# The Frodopi Manual.

---
### First step: SSH into the pi.

You will need the Pi's **username, hostname, and password**; this info can be found in some login info doc on the club's Google Drive.

First, make sure your machine is on the same network that the Pi is on. If the Pi is in the office, this'll likely be done with your or someone's **hotspot**. More details on networks below.

In a terminal, run the command with corresponding info:
\
`ssh <username>@<hostname>.local`
\
Then enter the password. On success, you should be in the Pi.

Run `exit` to exit the Pi.

---
### Networks

The Pi will be hosted in the **club office** where it connects to **eduroam**. It can host the bots on eduroam fine, but if you want to SSH into the Pi to make changes, your machine must be on **the same network** that the Pi is on. However, this does not seem to work with eduroam due to some whatever business.

Thus, the most straightforward solution is to add your **hotspot** as a network to the Pi and modify its **autoconnect priority** to be higher than eduroam's.
- You'll likely need to use the hotspot of someone whose hotspot is already saved on the Pi to SSH and add your hotspot. From there, you can just use your hotspot.

>Instructions on how to add networks are below.

When the Pi looks for networks to join, it'll choose the saved one with highest priority.

Then, whenever you want to SSH, turn on your hotspot, turn the Pi's power supply off and on, and it should connect to your hotspot over eduroam and you'll be able to SSH with your machine (that is on the same hotspot).
\
After making the desired changes, run `sudo nmcli connection up eduroam` and the Pi will connect back to eduroam and automatically disconnect from your machine.

Note: when making the Pi connect to a different network, your machine's will **automatically disconnect** from the Pi, since the two devices will be on different networks

---
### Pi Structure

The Pi has various directories, but the one we're interested in is the one called **projects**. It contains the **uoft-vac-discord-bots** directory, which is connected to the GitHub repo.

Any future, non-discord bot related projects with GitHub repos that the club decides to embark one will probably go here as well.

---
### Environments

Every bot must have an **environment file (`.env`)** and a **virtual environment directory (`venv`)**.
- `.env`: stores sensitive data, such as bot tokens.
- `venv`: allows bots to separate their dependencies. Whenever modifying a bot's dependencies, **make sure you are in its venv**.

---
### Systemd Services

Every bot will also have their own **systemd service**, which allows bots to automatically start whenever the Pi boots.
\
A service must be **enabled** to have the bot automatically start.

Instructions on how to operate systemd services are below.

---
# Instructions

Here are instructions for common scenarios when working with the Pi.
\
All actions here are to be done **inside the Pi**.
\
Descriptions for particular commands are farther below.

## Adding a new bot

Make sure the new completed bot directory is on GitHub.
\
Particularly, it must have a <u>driver file and `requirements.txt`</u>, and all necessary files for hosting are in **one subdirectory**.

1. `git pull` and `cd` into the new bot's `bot` directory.

3. Create `.env` in `bot` using `nano` (see below for details).

Example `.env`:
```
BOT_TOKEN = _

TARGET_CHANNEL_ID = _

```

3. Create `venv` in `bot` and enter it.

Run:
\
`python3 -m venv venv`
\
`source venv/bin/activate`

4. In the bot's venv, install its dependencies.

Run `pip install -r requirements.txt`

5. Create a ** systemd service**.

Run `sudo nano /etc/systemd/system/<bot name>.service` and paste:
```
[Unit]
Description=<bot name>
After=network.target

[Service]
User=vac
WorkingDirectory=/home/vac/projects/uoft-vac-discord-bots/<bot directory>/bot
ExecStart=/home/vac/projects/uoft-vac-discord-bots/<bot directory>/bot/venv/bin/python -u <driver file>.py
Restart=always

[Install]
WantedBy=multi-user.target
```
- Replace info: Bot Name, bot directory, driver file.

6. Enable and start the service.

Run:
\
`sudo systemctl daemon-reload`
\
`sudo systemctl enable <bot name>`
\
`sudo systemctl start <bot name>`

- Use the same bot name you used when creating the service.

## Updating an existing bot

Assumes the steps above have been completed for said bot
\
Make sure the bot's directory on GitHub has the desired changes.

1. `git pull`

2. (IF `requirements.txt` was modified) reinstall dependencies in its venv.

In the bot's `bot` directory, run
\
`source venv/bin/activate`
\
`pip install -r requirements.txt`
\
`deactivate`

3. `sudo systemctl restart <bot name>`

## Adding a new network

Could be an internet or hotspot.
\
Make sure the network is visible (for hotspot, I suggest enabling **maximise compatibility**).

1. Find the network.

Run
\
`sudo nmcli device wifi rescan`
\
`nmcli device wifi`

You should be able to see the network displayed. If not, try to figure out why because you cannot proceed otherwise.

2. Connect the Pi.

Run `sudo nmcli device wifi connect <wifi name> password <password>`

This will disconnect your machine from the Pi.

3. Connect to the same new network on your computer and SSH again.

4. Set the network's **autoconnect priority**.

Run `sudo nmcli connection modify <wifi name> connection.autoconnect-priority <n>`

Recommended values:
- **eduroam**: 10
- **Hotspots**: 100
- **Home networks**: 200

## Modifying eduroam's login

eduroam uses someone's student info to connect.
\
When they graduate, the login info must be updated to another student.
\
This will likely be one of the new webmasters.

1. Change the **identity and password**.

Run
\
`sudo nmcli connection modify eduroam 802-1x.identity "<utorid>@utoronto.ca"`
\
`sudo nmcli connection modify eduroam 802-1x.password "<password>"`
- Note: `@utoronto.ca` MUST be after your UtorID. That's just how it works.

2. Reload networks.

Run
\
`sudo nmcli connection reload`
\
`nmcli -f 802-1x.identity connection show eduroam`

You should see the new UtorID. The password is hidden, but trust that is has been updated as well.

---
# Prominent Commands

- `sudo reboot`: restart the entire Pi.
- `sudo shutdown now`: stop all processes, unmount all file systems, and power off the Pi.
- `source venv/bin/activate`: enter a bot's venv.
    - You'll know you're in a venv if you see `(venv)` at the start of the command line.
    - Run `deactivate` to exit a venv.

### Writing files: `nano`

Used to write contents in a file (and create it, if the file didn't exist beforehand).
\
Run `nano <filepath>`
- Arrow keys to navigate.
- Hold shift while navigating to select.
- `ctrl + o` and `enter` to save changes.
- `ctrl + x` to exit.

There are many more operations that you can search online. The ones above are the essentials.

### Libraries: `pip`

Make sure you are in a bot's venv when modifying its libraries.

- `pip install -r requirements.txt`: installs all libraries listed in `requirements.txt`.
- `pip install <library>`
- `pip uninstall <library>`
- `pip list`: display an environment's libraries.

### Service: `systemctl`

- `sudo systemctl daemon-reload`: rereads all service files. Run after editing a service file.
- `sudo systemctl start <bot name>`
- `sudo systemctl restart <bot name>`
- `sudo systemctl stop <bot name>`
- `sudo systemctl enable <bot name>`
- `sudo systemctl disable <bot name>`
- `systemctl is-enabled <bot name>`
- `systemctl status <bot name>`: can check whether the bot's service is running, or if startup has failed.
    - Run after `start/restart` to see if the service has started successfully, or after `stop` to check if the service has indeed stopped.

### Logs: `journalctl`

Logs contain prints and errors. Great for debugging.
- `journalctl -u <bot name> -f`: display live logs.
- `journalctl -u <bot name> -n`: display the most recent 10 logs.
- `journalctl -u <bot name> -n <n>`: display the most recent `n` logs.
- `journalctl -u <bot name> -b`: display all logs since current boot.
- `journalctl -u <bot name>`: display all logs.
    - Too much info. Probably unnecessary.

### Network: `nmcli`

- `nmcli connection show`: display all **saved** networks.
- `nmcli connection show <connection id>`: display all attributes for a saved network.
    - Use these full attribute names when running `modify`.
- `nmcli connection show --active`: display attributes for the active network.
- `nmcli -f <attributes,> connection show`: display the specified attributes for all saved networks.
    - e.g. Compare each network's autoconnect priorities:
\
`nmcli -f name,autoconnect-priority connection show`
- `nmcli device wifi`: display all **visible** networks.
- `sudo nmcli device wifi rescan`: let the Pi rescan for visible networks.
    - Most networks will often not display the first time, so rescanning once is recommended.
- `nmcli device status`: display what each saved network is doing.
- `sudo nmcli connection up <network name>`: connect to a **saved** network.
- `sudo nmcli connection down <active network name>`: disconnect from the active network.
    - Will automatically connect to the highest priority network.
- `sudo nmcli device wifi connect <network name> password <password>`: save a new connection and connect.
    - New network must be visible from `nmcli device wifi`.
- `sudo nmcli connection modify <network name> <attribute> <value>`: modify an attribute for a network to the specified value.
    - e.g. Modify autoconnect priority to `n`:
\
`sudo nmcli connection modify <network name> connection.autoconnect-priority <n>`
- `sudo nmcli connection reload`: reread connection files.
    - Run after `modify` and check if the changes have saved.
- `nmcli radio wifi`: whether the Pi is able to connect to a network.
- `nmcli radio wifi on`
- `nmcli radio wifi off`

Prominent attributes:
- id (`str`): the "name" of the network (as opposed to the **ssid**, which is a unique identifier).
- autoconnect (`bool`): if the network is able to be autoconnected to.
- autoconnect-priority (`int`): if multiple networks are available, the Pi will connect to the one with **highest priority**.
