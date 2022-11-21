"""Window class where we visualize what we do"""
import time
import os
import socket
import webbrowser
from sys import stderr, stdin, stdout
import dearpygui.dearpygui as dpg
import paramiko
import requests
import config

class Window():
    """Manage visual interface"""

    def __init__(self) -> None:
        """
        Window initialization
        """
        print('Window initialization started.')
        self.cfg = config.Config()
        self.__version__ = '1.0.1.5'

    def callback(self, sender, data):
        """
        Returns callback info.
        """
        print(f'{sender} ==> {data}')
        return sender, data

    def create(self) -> None:
        """
        Creates window context.
        """
        dpg.create_context()

        with dpg.window(
            label='Window',                  \
            height=400,                      \
            width=400,                       \
            no_title_bar=True,               \
            no_bring_to_front_on_focus=True, \
            no_resize=True,                  \
            no_move=True):

            with dpg.group(horizontal=True):
                dpg.add_button(label='Refresh', tag='b_refresh', callback=lambda: dpg.configure_item('servers_list', items=self.cfg.get_servers()))
                dpg.add_button(label='Connect', tag='b_connect', callback=self.connect)
                dpg.add_button(label='Execute', tag='b_execute', callback=self.execute_cmd)
            dpg.add_listbox(items=self.cfg.get_servers(), tag='servers_list', num_items=8, width=200)

            with dpg.group(horizontal=True):
                dpg.add_button(label='Show Info', tag='b_unsafe', callback=self.show_context)
                dpg.add_button(label='Hide Info', tag='b_safe', callback=self.hide_context)

            with dpg.group(horizontal=True):
                dpg.add_text(label='IP', tag='ip', show=False, color=(0, 255, 0))
                dpg.add_text(label='Username', tag='username', show=False, color=(220, 0, 40))
                dpg.add_text(label='Password', tag='password', show=False, color=(220, 0, 40))

            dpg.add_separator()
            dpg.add_input_text(label='Commands File', default_value='commands', width=200 ,tag='i_commands')

            with dpg.group(horizontal=True):
                dpg.add_button(label='Clear', tag='b_purge', callback=lambda: dpg.set_value('i_commands', ''))
                dpg.add_radio_button(['.txt', '.json'], label='extension', tag='rb_extension', default_value='.txt', horizontal=True)
            dpg.add_separator()
            dpg.add_text('Status: Waiting...', tag='status', color=(0, 255, 0))
            dpg.add_button(label='Update', tag='b_update', show=False, pos=(8, 335), callback=lambda: webbrowser.open('https://github.com/OpsecGuy/Awesome-Server-Manager'))

    def update(self) -> None:
        """
        Keeps GUI updated when changes are done.
        """
        while True:
            if os.path.exists(self.cfg.config_path) is False:
                dpg.set_value('status', f'Could not find {self.cfg.config_file}.\nNew config has been created.')
                self.cfg.create_example()

            dpg.set_value('ip', self.cfg.get_value(dpg.get_value('servers_list'), 'IP'))
            dpg.set_value('username', self.cfg.get_value(dpg.get_value('servers_list'), 'username'))
            dpg.set_value('password', self.cfg.get_value(dpg.get_value('servers_list'), 'password'))

            if self.get_current_version() != self.__version__:
                dpg.configure_item('b_update', show=True)

            time.sleep(0.01)

    def run(self) -> None:
        """
        Execute/Start window thread.
        """
        dpg.create_viewport(
            title=f'Awesome Server Manager {self.__version__}', \
            height=400,                         \
            width=400,                          \
            max_width=400,                      \
            max_height=400,                     \
            resizable=False,                    \
            vsync=True)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()

    def destroy(self) -> None:
        """
        Destroys window context.
        """
        dpg.destroy_context()

    def hide_context(self) -> None:
        """
        Hides given context.
        """
        dpg.hide_item('ip')
        dpg.hide_item('username')
        dpg.hide_item('password')

    def show_context(self) -> None:
        """
        Force visibility of wanted context.
        """
        dpg.show_item('ip')
        dpg.show_item('username')
        dpg.show_item('password')

    def get_input_file(self) -> str:
        """
        Retrieves file which stores commands.

        Returns:
            str: full file name with extension.
        """
        command_file_name = dpg.get_value('i_commands')
        file_extension = dpg.get_value('rb_extension')
        if command_file_name != '':
            dpg.set_value('status', f'Reading {command_file_name + file_extension}.')
            return command_file_name + file_extension

        dpg.set_value('status', f'Could not find {command_file_name + file_extension} in\n{os.getcwd()}!')
        return 'None'

    def is_valid(self, protection: str) -> None:
        """Most of exceptions should be handled here.
        Args:
            protection (int):\n
            light - Only checks if server name is not None.\n
            full - Checks if server name is not None and checks if file with commands is valid.

        Returns:
            bool: True/False/None
        """
        if dpg.get_value('servers_list') == 'None':
            dpg.set_value('status', 'Chose correct server!')
            return False

        if protection == 'full':
            dpg.set_value('status', 'Parsing commands...')
            if self.get_input_file() == 'None':
                return False
        elif protection == 'light':
            pass
        return True

    def parse_command(self) -> str:
        """
        Command builder which is used later to execute on server.
        Returns:
            str: command
        """
        buffer = ''
        with open(self.get_input_file(), 'r', encoding='utf-8') as file:
            for line in file.readlines():
                if line != '\n':
                    escaped = ''.join(line.replace('\n', ' && '))
                    buffer = buffer + escaped
        return buffer

    def get_current_version(self):
        """Grabs version data from GitHub page.\n
        Visit Github for the newest versions.

        Returns:
            str: current version
        """
        return requests.get('https://raw.githubusercontent.com/OpsecGuy/Awesome-Server-Manager/main/version', headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}, timeout=5.0).text.replace('\n', '')

    def connect(self) -> bool:
        """
        Check if it's possible to connect to the server.\n
        Error log is printed out in GUI.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        dpg.set_value('status', f'[CONNECT] Connecting to {dpg.get_value("ip")}.')
        if self.is_valid(protection='light'):
            try:
                client.connect(hostname=dpg.get_value('ip'), port=int(self.cfg.get_value(dpg.get_value('servers_list'), 'port')), username=dpg.get_value('username'), password=dpg.get_value('password'), timeout=3.0)
                client.close()
                dpg.set_value('status', '[CONNECT] Task Finished!')
            except socket.timeout:
                dpg.set_value('status', '[CONNECT] Fail: Server Timed out!')

        return False

    def execute_cmd(self) -> bool:
        """
        Executes preapered commands to be executed on the server.\n
        Creates log file with format: *ip*.txt.\n
        If the same server has already log file, old one gonna be flushed.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        dpg.set_value('status', f'[EXECUTE] Connecting to {dpg.get_value("ip")}')
        if self.is_valid(protection='full'):
            try:
                client.connect(hostname=dpg.get_value('ip'), port=int(self.cfg.get_value(dpg.get_value('servers_list'), 'port')), username=dpg.get_value('username'), password=dpg.get_value('password'), timeout=3.0)
            except socket.timeout:
                dpg.set_value('status', '[EXECUTE] Fail: Server Timed out!')
                return

            try:
                with open(f'log_{dpg.get_value("ip")}.txt', 'w+', encoding='utf-8') as log_file:
                    try:
                        stdin, stdout, stderr = client.exec_command(self.parse_command())
                    except paramiko.SSHException:
                        dpg.set_value('status', '[EXECUTE] Failed to execute commands!')
                        return

                    for output in iter(stdout.readline, ''):
                        log_file.writelines(output)
            except OSError:
                dpg.set_value('status', '[EXECUTE] Failed open/write to file!')

            client.close()
            dpg.set_value('status', '[EXECUTE] Task Finished!')
