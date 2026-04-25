import json5

def test_jsonc():
    with open('ad_data_aggregator_config.jsonc', 'r', encoding='utf-8') as f:
        data = json5.load(f)
    print(data)


if __name__ == '__main__':
    test_jsonc()