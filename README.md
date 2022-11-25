## Awesome Server Manager v1
Python version used: 3.11.0 64-bit  
Supported versions: 3.5 and newer  
Supported systems: Windows

## Description
Awesome Server Manager is a tool which will make your life way easier by loggining automatically to each server and run tasks directly from your PC which will save your valuable time.  
  
'servers.json' is created automatically with example config if it doesn't exist. File stores all necessary data about your server(s). For each server you can customize ip, port, username, password.

By default 'commands.txt' is a file where you must put commands that will be executed on the server. You can create any text file, just remember to set name of it in correct form and be sure to place it in folder where application is stored.  
Worth to note is that each command should be in separated line like below:
```
whoami
apt update
apt upgrade -y
```
### REMINDER!
Keep 'servers.json' and file which stores your commands (?.txt) in the same folder where application is located.
When executing commands log file (SERVER_IP.txt) is being created for look up into server output. File overrides itself each time you execute that function.

## Setup
### Using from source (Windows only)
1. Download and install python 3.9.x - [DOWNLOAD](https://www.python.org/downloads/release/python-3912/)
2. Make sure to add Python to the PATH. You can do it by marking checkbox in installator
3. Download all files from [here](https://github.com/OpsecGuy/Awesome-Server-Manager/archive/refs/heads/main.zip)
4. Unpack zip to any folder. Then open a Command Prompt (CMD) and navigate to where downloaded files are stored and type 'pip install -r setup.txt'
5. After you finish installing necesssary packages use '(py|python) app.py' to run program.
### Using executable from Release page (Windows only) (Common)
This is the easiest way if you just want to start using application :)
1. Download newest app.py version from [here](https://github.com/OpsecGuy/Awesome-Server-Manager/releases) and save to any folder
2. Start program
3. Add your servers in servers.json and press refresh in application GUI

## Screenshot:
![This is an image](https://i.imgur.com/AHwkaFP.png)
