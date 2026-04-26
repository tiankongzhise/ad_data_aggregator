from ad_data_aggregator_backend.config.ad_platforms_secret_manager import SecretManager, AdPlatformSecretManager

def test_get_secret_value():
    manager = SecretManager()
    manager.load_from_config_center()
    print(manager.get_secret_value("ocean_engine", "app_id"))
    print(manager.get_secret_value("ocean_engine", "secret"))
    print(manager.get_secret_value("ocean_engine", "access_token"))
    print(manager.get_secret_value("ocean_engine", "refresh_token"))
    print(manager.get_secret_value("ocean_engine", "expires_at"))
    print(manager.get_secret_value("ocean_engine", "refresh_token_expires_at"))
    print(manager.get_secret_value("ocean_engine", "advertiser_id_map"))
    print(manager.get_secret_value("ocean_engine", "cc_account_id_map"))
    print(manager)

def test_get_secret():
    manager = SecretManager()
    manager.load_from_config_center()
    print(manager.get_secret("ocean_engine", "app_id"))
    print(manager.get_secret("ocean_engine", "secret"))
    print(manager.get_secret("ocean_engine", "access_token"))
    print(manager.get_secret("ocean_engine", "refresh_token"))
    print(manager.get_secret("ocean_engine", "expires_at"))
    print(manager.get_secret("ocean_engine", "refresh_token_expires_at"))

def test_list_platforms():
    manager = SecretManager()
    manager.load_from_config_center()
    print(manager.list_platforms())

def test_list_secrets():
    manager = SecretManager()
    manager.load_from_config_center()
    print(manager.list_secrets("ocean_engine"))

def main():
    print("test_get_secret_value")
    test_get_secret_value()
    print("test_get_secret")
    test_get_secret()
    print("test_list_platforms")
    test_list_platforms()
    print("test_list_secrets")
    test_list_secrets()

if __name__ == "__main__":
    main()