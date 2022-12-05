"""Files Management"""
import os
import json
import platform

example_config = {
    'test_server': {
        'IP': '1.1.1.1',
        'port': '22',
        'username': 'root',
        'password': 'password',
    },
    'test_server2': {
        'IP': '1.1.1.2',
        'port': '22',
        'username': 'root',
        'password': 'password',
    },
}

class Config():
    """Helps managing config files"""

    def __init__(self) -> None:
        """
        Config initialization
        """
        print('Config initialization started.')
        self.config_file = 'servers.json'

        if platform.system() == 'Windows':
            self.config_path = f"{os.getcwd()}\\{self.config_file}"
            
        elif platform.system() == 'Linux':
            self.config_path = f"{os.getcwd()}/{self.config_file}"
        else:
            print(f'Your system is not supported!')
            os._exit(0)
            
        if os.path.exists(self.config_path) is False:
            self.create_example()
            print(f'Could not find {self.config_file}! New config has been created.')

    def create_example(self) -> bool:
        """
        Generate example config file if it doesn't exist.
        """
        json_object = json.dumps(example_config, indent=4)
        with open(self.config_file, 'w', encoding='utf-8') as file:
            file.write(json_object)
            return True

    def load_config(self) -> None:
        """
        Saves servers list to file.
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                file.flush()
                json_buffer = json.load(file)
                file.close()
                return json_buffer
        except OSError:
            return False

    def get_servers(self) -> list:
        """
        Retrieves servers name (str) from file
        and creates list of them.
        """

        file = self.load_config()
        servers = []
        servers.clear()
        for i in file:
            servers.append(i)
        return servers

    def get_value(self, server: str, value: str) -> None:
        """
        Returns value of variable specified in config file.
        Args:
            server (str): server name which we choose to manage from dictionary.
            value (str): sets wanted value.
        Returns:
            any: value
        """
        file = self.load_config()
        for i in file:
            if i == server:
                return file[i][value]
        return None
