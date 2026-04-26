from tkzs_config_service_client import ConfigServiceClient
import os
from pathlib import Path
from typing import Optional, Union
from tkzs_config_service_client.crypto import RSACrypto
from dataclasses import dataclass,field

@dataclass
class ConfigCenterFiles:
    env_files: list[str] = field(default_factory=lambda: ['database.env', 'ocean_engine.env'])
    config_file: list[str] = field(default_factory=lambda: ['config.toml'])

    def __post_init__(self):
        for env_file in self.env_files:
            if not Path(env_file).exists():
                raise FileNotFoundError(f'{env_file} not found')
        for config_file in self.config_file:
            if not Path(config_file).exists():
                raise FileNotFoundError(f'{config_file} not found')

_project_name = 'ad_data_aggregator'


def _get_default_private_key_dir(private_key_relative_dir:str = '密钥/.ssl'):
    onedirve_path = os.getenv('OneDrive')
    if onedirve_path is None:
        raise ValueError('OneDrive path is not set')
    return Path(onedirve_path) / private_key_relative_dir
def _get_safe_env(env_name:str):
    env_value = os.getenv(env_name)
    if env_value is None:
        raise ValueError(f'{env_name} is not set')
    return env_value
def _create_default_config_center_client() -> ConfigServiceClient:
    return ConfigServiceClient(
        config_service_url=_get_safe_env('ConfigServiceUrl'),
        private_key_dir=_get_default_private_key_dir(),
        default_logger_print=True
    )

def create_project_config_center_account(username:str|None = None,password:str|None = None,private_key_path:Optional[Union[str, Path]] = None):
    if username is None:
        username = f'{_get_safe_env('ConfigServiceUsername')}_{_project_name}'
    if password is None:
        password = _get_safe_env('ConfigServicePassword')
    if private_key_path is None:
        # 生成一个随机RSA私钥
        private_pem, _ = RSACrypto.generate_keypair()
        private_key_path = _get_default_private_key_dir() / f'{username}_private_key.pem'
        with open(private_key_path, 'wb') as f:
            f.write(private_pem)
    client = _create_default_config_center_client()
    client.register(username=username,password=password,user_private_key_path=private_key_path)
    return username,password,private_key_path,client


def get_login_config_center_client(client:ConfigServiceClient|None = None,username:str|None = None,password:str|None = None,private_key_path:Optional[Union[str, Path]] = None,private_key_dir:Optional[Union[str, Path]] = None):
    if client is None:
        client = _create_default_config_center_client()
    username = username or _get_safe_env('ConfigServiceUsername')
    password = password or _get_safe_env('ConfigServicePassword')
    client.login(username=username,password=password,private_key_path=private_key_path,private_key_dir=private_key_dir)
    return client

def get_project_config_center_client(username:str|None = None,password:str|None = None,private_key_path:Optional[Union[str, Path]] = None):
    if username is None:
        username = f'{_get_safe_env('ConfigServiceUsername')}_{_project_name}'
    if password is None:
        password = _get_safe_env('ConfigServicePassword')
    if private_key_path is None:
        private_key_path = _get_default_private_key_dir() / f'{username}_private_key.pem'
        if not private_key_path.exists():
            private_key_path = None

    try:
        username,password,private_key_path,client = create_project_config_center_account(username=username,password=password,private_key_path=private_key_path)
        return client
    except Exception as e:
        if 'username already exists' in str(e):
            pass
        else:
            raise e
    client = _create_default_config_center_client()
    client.login(username=username,password=password,private_key_path=private_key_path)
    return client

def init_config_center_files(config_center_files:ConfigCenterFiles|None = None):
    if config_center_files is None:
        config_center_files = ConfigCenterFiles()
    for env_file in config_center_files.env_files:
        if not Path(env_file).exists():
            raise FileNotFoundError(f'{env_file} not found')
    for config_file in config_center_files.config_file:
        if not Path(config_file).exists():
            raise FileNotFoundError(f'{config_file} not found')
    client = get_project_config_center_client()
    for env_file in config_center_files.env_files:
        try:
            client.upload_config(env_file)
        except Exception as e:
            if 'Config already exists' in str(e):
                pass
            else:
                raise e
    for config_file in config_center_files.config_file:
        try:
            client.upload_config(config_file)
        except Exception as e:
            if 'Config already exists' in str(e):
                pass
            else:
                raise e

if __name__ == '__main__':
    # get_project_config_center_client()
    init_config_center_files()
    