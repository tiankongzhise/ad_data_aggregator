from tkzs_config_service_client import ConfigServiceClient
import os
from pathlib import Path

def _get_default_private_key_dir(private_key_relative_dir:str = '密钥/.ssl'):
    onedirve_path = os.getenv('OneDrive')
    if onedirve_path is None:
        raise ValueError('OneDrive path is not set')
    return Path(onedirve_path) / private_key_relative_dir
def _get_safe_env(env_name:str):
    env_value = os.getenv(env_name)
    print(f'{env_name}: {env_value}')
    if env_value is None:
        raise ValueError(f'{env_name} is not set')
    return env_value

config_center_client = ConfigServiceClient(
    config_service_url=_get_safe_env('ConfigServiceUrl'),
    private_key_dir=_get_default_private_key_dir()
)
config_center_client.login(username=_get_safe_env('ConfigServiceUsername'),password=_get_safe_env('ConfigServicePassword'))