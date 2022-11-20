"""Window class where we visualize what we do"""
import time
import os
import webbrowser
from sys import stderr, stdin, stdout
import paramiko
import dearpygui.dearpygui as dpg
import config

class Window():
    """Creates window aKa GUI"""

    def __init__(self) -> None:
        """
        Window initialization
        """
        self.cfg = config.Config()
        self.__version__ = '1.0.1.2'
        print('Window initialization started.')

    def callback(self, sender, data):
        """
        Returns callback info
        """
        print(f'{sender} ==> {data}')
        return sender, data

    def create(self) -> None:
        """
        Creates window context
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

            dpg.add_button(label='Check for updates', pos=(8, 335), callback=lambda: webbrowser.open('https://github.com/OpsecGuy/Awesome-Server-Manager'))

    def update(self) -> None:
        """
        Keeps GUI updated when changes are done.
        """
        while True:
            try:
                dpg.set_value('ip', self.cfg.get_value(dpg.get_value('servers_list'), 'IP'))
                dpg.set_value('username', self.cfg.get_value(dpg.get_value('servers_list'), 'username'))
                dpg.set_value('password', self.cfg.get_value(dpg.get_value('servers_list'), 'password'))

                if os.path.exists(self.cfg.config_path) is False:
                    dpg.set_value('status', f'Servers list could not be found!\nCreating new {self.cfg.config_file}')
                    self.cfg.create_example()

            except Exception as err:
                print(err)
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
            str: full file name with extension
        """
        try:
            command_file_name = dpg.get_value('i_commands')
            file_extension = dpg.get_value('rb_extension')
            if command_file_name != '':
                path = f"{os.getcwd()}\\{command_file_name + file_extension}"
                dpg.set_value('status', f'Reading {command_file_name + file_extension}...')
                return command_file_name + file_extension

            dpg.set_value('status', 'No file has been specified!')
            return None

        except Exception as err:
            dpg.set_value('status', f'Could not find {command_file_name + file_extension} in\n{os.getcwd()}')

    def is_valid(self, stage: int) -> bool:
        """Most of exceptions should be handled here.
        Args:
            stage (int):\n
            1 - Checks if server name is not None and checks if file with commands is valid.\n
            2 - Only checks if server name is not None.

        Returns:
            bool: True/False
        """
        if dpg.get_value('servers_list') == 'None':
            dpg.set_value('status', 'Chose correct server!')
            return False

        if stage == 1:
            dpg.set_value('status', 'Parsing commands...')
            if self.get_input_file() is None:
                return False
            else:
                return True

        if stage == 2:
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

    def connect(self) -> None:
        """
        Check if it's possible to connect to the server.\n
        Error log is printed out in GUI.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        dpg.set_value('status', f'[CONNECT] Connecting to {dpg.get_value("ip")}')
        try:
            if self.is_valid(stage=2):
                try:
                    client.connect(hostname=dpg.get_value('ip'), port=int(self.cfg.get_value(dpg.get_value('servers_list'), 'port')), username=dpg.get_value('username'), password=dpg.get_value('password'), timeout=3.0)
                except Exception:
                    dpg.set_value('status', '[CONNECT] Connection Failed!')
                    return

                client.close()
                dpg.set_value('status', '[CONNECT] Task Finished!')

        except Exception as err:
            dpg.set_value('status', f'[CONNECT] An Error Occurred!\nDETAILS:\n{err}')

    def execute_cmd(self) -> None:
        """
        Executes preapered commands to be executed on the server.\n
        Creates log file with format: *ip*.txt.\n
        If the same server has already log file, old one gonna be flushed.
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            dpg.set_value('status', f'[EXECUTE] Connecting to {dpg.get_value("ip")}')
            if self.is_valid(stage=1):

                try:
                    client.connect(hostname=dpg.get_value('ip'), port=int(self.cfg.get_value(dpg.get_value('servers_list'), 'port')), username=dpg.get_value('username'), password=dpg.get_value('password'), timeout=3.0)
                except Exception:
                    dpg.set_value('status', '[EXECUTE] Connection Failed!')
                    return

                with open(f'log_{dpg.get_value("ip")}.txt', 'w+', encoding='utf-8') as log_file:
                    stdin, stdout, stderr = client.exec_command(self.parse_command())

                    for output in iter(stdout.readline, ''):
                        log_file.writelines(output)

                client.close()
                dpg.set_value('status', '[EXECUTE] Task Finished!')

        except Exception as err:
            dpg.set_value('status', f"[EXECUTE] An Error Occurred!\nDETAILS:\n{err}")
