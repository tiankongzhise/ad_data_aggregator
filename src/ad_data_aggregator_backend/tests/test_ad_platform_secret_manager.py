from ad_data_aggregator_backend.config.ad_platforms_secret_manager import  AdPlatformSecretManager

def test_get_secret_value():
    manager = AdPlatformSecretManager("ocean_engine")
    manager.pf_load_from_config_center()
    print(manager.pf_get_secret_value("app_id"))
    print(manager.pf_get_secret_value("secret"))
    print(manager.pf_get_secret_value("access_token"))
    print(manager.pf_get_secret_value("refresh_token"))
    print(manager.pf_get_secret_value("expires_at"))
    print(manager.pf_get_secret_value("refresh_token_expires_at"))
    print(manager)

def test_get_secret():
    manager = AdPlatformSecretManager("ocean_engine")
    manager.pf_load_from_config_center()
    print(manager.pf_get_secret("app_id"))
    print(manager.pf_get_secret("secret"))
    print(manager.pf_get_secret("access_token"))
    print(manager.pf_get_secret("refresh_token"))
    print(manager.pf_get_secret("expires_at"))
    print(manager.pf_get_secret("refresh_token_expires_at"))

def test_get_platform_name():
    manager = AdPlatformSecretManager("ocean_engine")
    manager.pf_load_from_config_center()
    print(manager.get_platform_name())

def test_list_secrets():
    manager = AdPlatformSecretManager("ocean_engine")
    manager.pf_load_from_config_center()
    print(manager.pf_list_secrets())

def main():
    print("test_get_secret_value")
    test_get_secret_value()
    print("test_get_secret")
    test_get_secret()
    print("test_get_platform_name")
    test_get_platform_name()
    print("test_list_secrets")
    test_list_secrets()

if __name__ == "__main__":
    main()