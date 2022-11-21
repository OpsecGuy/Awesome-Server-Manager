## Awesome Server Manager v1
Currently supported systems: Windows

## Description
Awesome Server Manager is a tool which saves your time and without loggining manually to each server you can check if server is up or down or even execute commands directly from your PC.

## Usage
'servers.json' is created automatically with example config. File stores all necessary data about your servers. For each server you can customize name under which, server data is stored. IP, port, username, password can be set in file.

Default 'commands.txt' file is where you put commands that will be executed on the server. Keep in mind that you can set any name of the file. Remember to insert each command in separated lines.

Most important thing is that 'servers.json' and file which stores commands must be in the same folder where script is located.

When executing commands log file (IP.txt) is being created for each server. File overrides itself each time you execute that function.

## Setup
1. Download & install python 3.9.x (Make sure to add Python to the PATH. You can do it with installator)
2. Open Command Prompt (CMD) and type 'pip install -r setup.txt'
3. Go to the directory where you store script and type '(py|python) app.py'

## Screenshot:
![This is an image](https://i.imgur.com/TkdcmGD.png)
