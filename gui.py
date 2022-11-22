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
import logger

class Window():
    """Manage visual interface"""

    def __init__(self) -> None:
        """
        Window initialization
        """
        print('Window initialization started.')
        self.cfg = config.Config()
        self.logger = logger.Logger()
        self.__version__ = '1.0.1.8'

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
            label='Window',
            width=400,
            height=500,
            no_title_bar=True,
            no_resize=False,
            no_move=True,
            tag='w_main'):

            with dpg.group(horizontal=True):
                dpg.add_button(label='Refresh',
                               tag='b_refresh',
                               callback=lambda: dpg.configure_item(item='servers_list',
                                                                   items=self.cfg.get_servers()))
                dpg.add_button(label='Connect',
                               tag='b_connect',
                               callback=self.connect)

                dpg.add_button(label='Execute',
                               tag='b_execute',
                               callback=self.execute_cmd)

            dpg.add_listbox(items=self.cfg.get_servers(),
                            num_items=8,
                            width=200,
                            tag='servers_list')

            with dpg.group(horizontal=True):
                dpg.add_button(label='Show Info',
                               tag='b_unsafe',
                               callback=self.show_context)
                dpg.add_button(label='Hide Info',
                               tag='b_safe',
                               callback=self.hide_context)

            with dpg.group(horizontal=True):
                dpg.add_text(label='IP',
                             show=False,
                             color=(0, 255, 0),
                             tag='ip',)
                dpg.add_text(label='Username',
                             show=False,
                             color=(220, 0, 40),
                             tag='username')
                dpg.add_text(label='Password',
                             show=False,
                             color=(220, 0, 40),
                             tag='password')
            dpg.add_separator()
            dpg.add_input_text(label='Commands File',
                               default_value='commands',
                               width=200,
                               tag='i_commands')

            with dpg.group(horizontal=True):
                dpg.add_button(label='Clear',
                               tag='b_clear',
                               callback=lambda: dpg.set_value('i_commands', ''))
                dpg.add_radio_button(label='File extension',
                                     items=['.txt', '.json'],
                                     default_value='.txt',
                                     horizontal=True,
                                     tag='rb_extension')
            dpg.add_separator()
            dpg.add_input_text(label='',
                               readonly=True,
                               multiline=True,
                               enabled=False,
                               width=350,
                               height=150,
                               tag='i_logs_area')

            with dpg.group(horizontal=True):
                dpg.add_button(label='Clear Logs',
                            callback=self.logger.reset)

                dpg.add_button(label='Update',
                            show=False,
                            tag='b_update',
                            callback=lambda: webbrowser.open(
                                'https://github.com/OpsecGuy/Awesome-Server-Manager'
                                ))

    def update(self) -> None:
        """
        Keeps GUI updated when changes are done.
        """
        while True:
            if os.path.exists(self.cfg.config_path) is False:
                self.logger.log(f'Could not find {self.cfg.config_file}.\n\
                              New config has been created.')
                self.cfg.create_example()

            dpg.set_value('ip', self.cfg.get_value(dpg.get_value('servers_list'), 'IP'))
            dpg.set_value('username', self.cfg.get_value(dpg.get_value('servers_list'), 'username'))
            dpg.set_value('password', self.cfg.get_value(dpg.get_value('servers_list'), 'password'))
            dpg.set_value('i_logs_area', '\n'.join(self.logger.log_buffer))

            vp_width = dpg.get_viewport_width()
            vp_height = dpg.get_viewport_height()
            dpg.configure_item(item='w_main', width=vp_width - 1)
            dpg.configure_item(item='w_main', height=vp_height - 1)

            if self.get_current_version() != self.__version__:
                dpg.configure_item('b_update', show=True)

            time.sleep(0.01)

    def run(self) -> None:
        """
        Execute/Start window thread.
        """
        dpg.create_viewport(
            title=f'Awesome Server Manager {self.__version__}',
            height=500,
            width=400,
            resizable=True,
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
        abs_path = f"{os.getcwd()}\\{command_file_name + file_extension}"
        if command_file_name != '' and os.path.exists(abs_path) is True:
            return command_file_name + file_extension

        self.logger.log(f'Could not find {command_file_name + file_extension} in\n{os.getcwd()}!')
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
            self.logger.log('[OTHER] Chose correct server!')
            return False

        if protection == 'full':
            if self.get_input_file() == 'None':
                return False
            self.logger.log('[OTHER] Grabbing data from commands file.')
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
        self.logger.log('[OTHER] Parsing commands...')
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
        return requests.get(url='https://raw.githubusercontent.com/OpsecGuy/Awesome-Server-Manager/main/version',
                            headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'},
                            timeout=5.0).text.replace('\n', '')

    def connect(self) -> bool:
        """
        Check if it's possible to connect to the server.\n
        Error log is printed out in GUI.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.is_valid(protection='light'):
            self.logger.log(f'[CONNECT] Connecting to {dpg.get_value("ip")}')
            try:
                client.connect(hostname=dpg.get_value('ip'),
                               port=int(self.cfg.get_value(dpg.get_value('servers_list'), 'port')),
                               username=dpg.get_value('username'),
                               password=dpg.get_value('password'),
                               timeout=3.0)
                client.close()
                self.logger.log('[CONNECT] Task Completed!')
            except socket.timeout:
                self.logger.log('[CONNECT] Fail: Server Timed out!')

        return False

    def execute_cmd(self) -> bool:
        """
        Executes preapered commands to be executed on the server.\n
        Creates log file with format: *ip*.txt.\n
        If the same server has already log file, old one gonna be flushed.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.is_valid(protection='full'):
            self.logger.log(f'[EXECUTE] Connecting to {dpg.get_value("ip")}')
            try:
                client.connect(hostname=dpg.get_value('ip'),
                               port=int(self.cfg.get_value(dpg.get_value('servers_list'), 'port')),
                               username=dpg.get_value('username'),
                               password=dpg.get_value('password'),
                               timeout=3.0)
            except socket.timeout:
                self.logger.log('[EXECUTE] Fail: Server Timed out!')
                return

            try:
                with open(f'log_{dpg.get_value("ip")}.txt', 'w+', encoding='utf-8') as log_file:
                    self.logger.log(f'[EXECUTE] Writing server logs to log_{dpg.get_value("ip")}.txt')
                    try:
                        stdin, stdout, stderr = client.exec_command(self.parse_command())
                        self.logger.log('[EXECUTE] Commands executed correctly!')
                    except paramiko.SSHException:
                        self.logger.log('[EXECUTE] Failed to execute commands!')
                        return

                    for output in iter(stdout.readline, ''):
                        log_file.writelines(output)
            except OSError:
                self.logger.log('[EXECUTE] Failed open/write to the log file!')

            client.close()
            self.logger.log('[EXECUTE] Task Completed!')
