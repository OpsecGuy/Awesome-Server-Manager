from sys import stderr, stdin, stdout
import threading, paramiko, os, time, hashlib


class wtype:
    header = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    normal = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

server_files = [r'/root/test.txt',
r'/root/test1.txt',]

local_files = [r'C:\Users\User\example\test.txt',
r'C:\Users\User\example\test1.txt']

servers = {
    'server1' : {
        'ip':'1.1.1.1',
        'user':'root',
        'password':'example'
    },
    'server2' : {
        'ip':'1.1.1.2',
        'user':'root',
        'password':'example'
    },
    'server3' : {
        'ip':'1.1.1.3',
        'user':'root',
        'password':'example'
    },
}
def setup_console():
    os.system('cls')
    print(f'{wtype.normal}Choose mode:\n[1] Health Check\n[2] Mass Execute\n[3] Verify files')
    mode = int(input('Select mode > '))
    return mode

def get_server(server):
    ip_addr = servers[server]['ip']
    username = servers[server]['user']
    password = servers[server]['password']
    return ip_addr, username, password

def get_local_file(index):
    return local_files[index], server_files[index]

def get_commands_from_file(filename):
    commands = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                commands.append(line)
        
        return ''.join(commands).replace('\n', ' && ')
    except Exception as err:
        print(err)


### FEATURES ###
def is_up(ip, login, pwd):
    try:
        client.connect(ip, 22, login, pwd, timeout=300, auth_timeout=300, banner_timeout=300)
        print(f'{wtype.green}[{ip}] Connected')
    except Exception as err:
        pass
        print(f'{wtype.fail}[{ip}] Reason: {err}')

def mass_execute(ip, login, pwd, filename):
    try:
        client.connect(ip, 22, login, pwd, timeout=300, auth_timeout=300, banner_timeout=300)
        print(f'{wtype.green}[{ip}] Connected')

        # with open(f'log_{ip}.txt', 'w+', encoding='utf-8') as log_file:
        command = get_commands_from_file(filename)
        print(f'{wtype.blue}[{ip}] Executing {command}')

        stdin, stdout, stderr = client.exec_command(command)
        print(f'{wtype.blue}[{ip}]{stdout.readline()}\n{stderr.readline()}')

            # for output in iter(stdout.readline, ''):
            #     log_file.writelines(output)
        print(f'{wtype.green}[{ip}] Finished!')

    except (Exception, paramiko.SSHException) as err:
        print(f'{wtype.fail}[{ip}] Reason: {err}')

def verify_file_hash(ip, login, pwd):
    try:
        client.connect(ip, 22, login, pwd, timeout=300, auth_timeout=300, banner_timeout=300)
        print(f'{wtype.green}[{ip}] Connected')

        for file in range(len(local_files)):
            src_file, dst_file = get_local_file(file)
            src_file_hash = hashlib.sha256()
            dst_file_hash = dst_file
            print(f'{wtype.green}[{ip}] Compare {src_file} to {dst_file_hash}')

            with open(src_file, 'rb') as local_file:
                for byte_block in iter(lambda: local_file.read(4096), b''):
                    src_file_hash.update(byte_block)

            stdin, stdout, stderr = client.exec_command(f'sha256sum {dst_file}')
            for output in iter(stdout.readlines, ''):
                if output == '' or output == None or output == []:
                    print(f'{wtype.fail}[{ip}] Reason: Couldn\'t {dst_file} find file!')
                    return
                dst_file_hash = output
            
            dst_file_hash = dst_file_hash.split(f' ', 1)[0]
            if dst_file_hash == src_file_hash.hexdigest():
                print(f'{wtype.green}[{ip}] Hashes match')
            else:
                print(f'{wtype.fail}[{ip}] Reason: Hashes doesn\'t match')
                print(f'{dst_file_hash}\n{src_file_hash.hexdigest()}')

    except Exception as err:
        print(f'{wtype.fail}[{ip}] Reason: {err}')

### THREADS ###
def start_threads():
    global client
    mode = setup_console()
    print(f'{wtype.green}Loaded servers: {len(servers.keys())}')
    for srv in servers:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        i, l, p = get_server(srv)
        
        if mode == 1:
            threading.Thread(target=is_up, name=i, args=[i, l, p]).start()
            time.sleep(0.5)
        elif mode == 2:
            threading.Thread(target=mass_execute, name=i, args=[i, l, p, 'commands.txt']).start()
            time.sleep(0.5)
        elif mode == 3:
            threading.Thread(target=verify_file_hash, name=i, args=[i, l, p]).start()
            time.sleep(3)
        else:
            print(f'{wtype.fail}Invalid mode!')
            os._exit(0)

if __name__ == "__main__":
    start_threads()
