from ad_data_aggregator_backend.plugins.ocean_engine import OceanEnginePlugin
import json
import asyncio
from typing import Literal
class TestOceanEnginePlugin:
    def __init__(self,app_id:str,secret:str):
        self.app_id = app_id
        self.secret = secret


    async def test_get_access_token(self,auth_code:str):
        plugin = OceanEnginePlugin()
        access_token = await plugin._get_access_token(self.app_id, self.secret, auth_code)
        print(f"access_token: {access_token}")
        with open('access_token.json', 'w',encoding='utf-8') as f:
            json.dump(access_token, f)
    async def test_refresh_access_token(self,refresh_token:str):
        plugin = OceanEnginePlugin()
        access_token = await plugin._refresh_access_token(self.app_id, self.secret, refresh_token)
        print(f"refresh_access_token: {access_token}")
        with open('refresh_access_token.json', 'w',encoding='utf-8') as f:
            json.dump(access_token, f)
    async def test_get_available_dimensions_and_metrics_by_data_topic(self,advertiser_id:int,data_topics:list[str],access_token:str):
        plugin = OceanEnginePlugin()
        dimensions_and_metrics = await plugin._get_available_dimensions_and_metrics_by_data_topic(advertiser_id, data_topics, access_token)
        print(f"dimensions_and_metrics: {dimensions_and_metrics}")
        with open('dimensions_and_metrics.json', 'w',encoding='utf-8') as f:
            json.dump(dimensions_and_metrics, f,ensure_ascii=False)
    async def test_get_advertiser_list(self,access_token:str):
        plugin = OceanEnginePlugin()
        advertiser_list = await plugin._get_authorized_accounts(access_token)
        print(f"advertiser_list: {advertiser_list}")
        with open('advertiser_list.json', 'w',encoding='utf-8') as f:
            json.dump(advertiser_list, f)
    async def test_get_customer_center_advertiser_list(self,cc_account_id:int,account_source:Literal['AD','ENTERPRISE','LOCAL'],access_token:str):
        plugin = OceanEnginePlugin()
        customer_center_advertiser_list = await plugin._get_customer_center_advertiser_list(cc_account_id, account_source, access_token)
        print(f"customer_center_advertiser_list: {customer_center_advertiser_list}")
        with open('customer_center_advertiser_list.json', 'w',encoding='utf-8') as f:
            json.dump(customer_center_advertiser_list, f)
    async def test_refresh_access_token_without_params(self):
        plugin = OceanEnginePlugin()
        access_token = await plugin._refresh_access_token()
        print(f"access_token: {access_token}")
        with open('refresh_access_token_without_params.json', 'w',encoding='utf-8') as f:
            json.dump(access_token, f)

    async def test_get_authorized_accounts(self,access_token:str|None = None):
        plugin = OceanEnginePlugin()
        authorized_accounts = await plugin._get_authorized_accounts(access_token)
        print(f"authorized_accounts: {authorized_accounts}")
        with open('authorized_accounts.json', 'w',encoding='utf-8') as f:
            json.dump(authorized_accounts, f)
    async def test__fetch_data(self,access_token: str,
    advertiser_id: int,
    data_topic: str,
    dimensions: list[str],
    metrics: list[str],
    start_time: str,
    end_time: str,
    *,
    filters: dict,
    order_by: dict,
    page: int = 1,
    page_size: int = 10):
        plugin = OceanEnginePlugin()
        fetch_data = await plugin._fetch_data(access_token,advertiser_id,data_topic,dimensions,metrics,start_time,end_time,filters=filters,order_by=order_by)
        print(f"fetch_data: {fetch_data}")
        with open('fetch_data.json', 'w',encoding='utf-8') as f:
            json.dump(fetch_data, f,ensure_ascii=False)

    async def test_begin(self,**kwargs):
        # await self.test_get_access_token(kwargs['auth_code'])
        # await self.test_refresh_access_token(kwargs['refresh_token'])
        # await self.test_get_available_dimensions_and_metrics_by_data_topic(kwargs['advertiser_id'], kwargs['data_topics'], kwargs['access_token'])
        # await self.test_get_advertiser_list(kwargs['access_token'])
        # await self.test_get_customer_center_advertiser_list(kwargs['cc_account_id'], kwargs['account_source'], kwargs['access_token'])
        # await test__fetch_data(access_token=kwargs['access_token'],advertiser_id=kwargs['advertiser_id'])
        await self.test_refresh_access_token_without_params()

if __name__ == "__main__":
    app_id = '1805969627151371'
    secret = '0cb84b67505483a617f983e3eaf33434b690baab'
    auth_code = '064e1947d00659bbc1a523434a315c69d5e80650'
    refresh_token = 'aeb8a6f7b1138b534008e11ec8e54f1603cea3ac'
    advertiser_id = 1813535994941443
    access_token = 'a6e2751f68a250f8cc4764a2eee5f346901dd6b0'
    data_topics = ['BASIC_DATA','BIDWORD_DATA','DMP_DATA','MATERIAL_DATA','ONE_KEY_BOOST_DATA','PRODUCT_DATA','QUERY_DATA','VIDEO_DUARATION_DATA']
    cc_account_id = 1800168496063497
    account_source = 'AD'
    test = TestOceanEnginePlugin(app_id, secret)
    # asyncio.run(test.test_begin(auth_code=auth_code,refresh_token=refresh_token,advertiser_id=advertiser_id,access_token=access_token,data_topics=data_topics,cc_account_id=cc_account_id,account_source=account_source))
    # asyncio.run(test.test_refresh_access_token_without_params())
    asyncio.run(test.test_get_authorized_accounts())