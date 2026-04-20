from .base import PlatformPluginInterface
from typing import  Any
from httpx import AsyncClient
import json
from typing import Literal


class _Utils:
    async def get_dimensions_and_metrics_cache(self,cache_path:str = 'dimensions_and_metrics.json'):
        with open(cache_path,'rb') as f:
            data = json.load(f)
        return data 
    
    async def build_exclusion_mappings(self,data_topic: str, full_data: dict) -> tuple:
        """
        根据指定的 data_topic 构建排除映射。
        返回: (dim_exclusions, metric_exclusions, dim_name_map, metric_name_map)
        """
        # 找到对应的 data_topic
        topic_list = full_data.get('data', {}).get('list', [])
        topic_info = None
        for topic in topic_list:
            if topic.get('data_topic') == data_topic:
                topic_info = topic
                break
        if not topic_info:
            raise ValueError(f"未找到 data_topic: {data_topic}")

        dimensions = topic_info.get('dimensions', [])
        metrics = topic_info.get('metrics', [])

        dim_exclusions = {}
        dim_name_map = {}
        for dim in dimensions:
            field = dim['field']
            dim_name_map[field] = dim.get('name', field)
            dim_exclusions[field] = {
                'ex_dims': set(dim.get('exclusion_dims', [])),
                'ex_metrics': set(dim.get('exclusion_metrics', []))
            }

        metric_exclusions = {}
        metric_name_map = {}
        for metric in metrics:
            field = metric['field']
            metric_name_map[field] = metric.get('name', field)
            metric_exclusions[field] = {
                'ex_dims': set(metric.get('exclusion_dims', []))
            }

        return dim_exclusions, metric_exclusions, dim_name_map, metric_name_map

    async def check_conflicts(self,chosen_dims: list[str],
                        chosen_metrics: list[str],
                        dim_exclusions: dict[str, dict[str, set[str]]],
                        metric_exclusions: dict[str, dict[str, set[str]]],
                        dim_name_map: dict[str, str],
                        metric_name_map: dict[str, str]) -> dict[str, Any]:
        """
        检测维度和指标组合是否存在冲突。

        参数:
            chosen_dims: 选择的维度字段名列表
            chosen_metrics: 选择的指标字段名列表
            dim_exclusions: 维度的排除规则映射 (由 build_exclusion_mappings 生成)
            metric_exclusions: 指标的排除规则映射 (由 build_exclusion_mappings 生成)
            dim_name_map: 维度字段名 -> 中文名称
            metric_name_map: 指标字段名 -> 中文名称

        返回:
            {
                'has_conflict': bool,          # 是否存在冲突
                'conflicts': [                 # 冲突详情列表
                    {
                        'type': 'dim-dim' | 'dim-metric' | 'metric-dim',
                        'source_field': str,   # 产生排除规则的字段
                        'target_field': str,   # 被排除的字段
                        'rule': 'exclusion_dims' | 'exclusion_metrics',
                        'message': str         # 友好的中文冲突描述
                    },
                    ...
                ]
            }
        """
        # 1. 先调用之前的 detect_conflicts 函数获得原始冲突列表
        raw_conflicts = self._detect_conflicts_raw(chosen_dims, chosen_metrics,
                                            dim_exclusions, metric_exclusions)

        if not raw_conflicts:
            return {'has_conflict': False, 'conflicts': []}

        # 2. 转换为带友好消息的格式
        conflicts_detail = []
        for c in raw_conflicts:
            source = c['source_field']
            target = c['target_field']
            rule = c['rule']
            ctype = c['type']

            # 获取源的中文名称
            if ctype in ('dim-dim', 'dim-metric'):
                source_name = dim_name_map.get(source, source)
            else:  # metric-dim
                source_name = metric_name_map.get(source, source)

            # 获取目标的中文名称
            if ctype == 'dim-dim':
                target_name = dim_name_map.get(target, target)
                msg = f"维度「{source_name}」的 {rule} 禁止与维度「{target_name}」同时使用。"
            elif ctype == 'dim-metric':
                target_name = metric_name_map.get(target, target)
                msg = f"维度「{source_name}」的 {rule} 禁止与指标「{target_name}」同时使用。"
            else:  # metric-dim
                target_name = dim_name_map.get(target, target)
                msg = f"指标「{source_name}」的 {rule} 禁止与维度「{target_name}」同时使用。"

            conflicts_detail.append({
                'type': ctype,
                'source_field': source,
                'target_field': target,
                'rule': rule,
                'message': msg
            })

        return {'has_conflict': True, 'conflicts': conflicts_detail}


    def _detect_conflicts_raw(self,chosen_dims: list[str],
                            chosen_metrics: list[str],
                            dim_exclusions: dict,
                            metric_exclusions: dict) -> list[dict]:
        """原始冲突检测，返回字段级别的冲突列表（内部使用）"""
        conflicts = []
        dim_set = set(chosen_dims)
        metric_set = set(chosen_metrics)

        # 维度‑维度
        for d in chosen_dims:
            if d not in dim_exclusions:
                continue
            ex_dims = dim_exclusions[d].get('ex_dims', set())
            for other in ex_dims:
                if other in dim_set and other != d:
                    conflicts.append({
                        'type': 'dim-dim',
                        'source_field': d,
                        'target_field': other,
                        'rule': 'exclusion_dims'
                    })

        # 维度‑指标
        for d in chosen_dims:
            if d not in dim_exclusions:
                continue
            ex_metrics = dim_exclusions[d].get('ex_metrics', set())
            for m in ex_metrics:
                if m in metric_set:
                    conflicts.append({
                        'type': 'dim-metric',
                        'source_field': d,
                        'target_field': m,
                        'rule': 'exclusion_metrics'
                    })

        # 指标‑维度
        for m in chosen_metrics:
            if m not in metric_exclusions:
                continue
            ex_dims = metric_exclusions[m].get('ex_dims', set())
            for d in ex_dims:
                if d in dim_set:
                    conflicts.append({
                        'type': 'metric-dim',
                        'source_field': m,
                        'target_field': d,
                        'rule': 'exclusion_dims'
                    })

        return conflicts

class OceanEnginePlugin(PlatformPluginInterface):
    _utils = _Utils()
    def get_platform_name(self) -> str:
        return "ocean_engine"
    
    async def fetch_data(self, credentials: dict[str, str], report_type: str, dimensions: list[str], metrics: list[str], start_time: str, end_time: str) -> list[dict[str, Any]]:
        ...
    async def _get_access_token(self,app_id:str,secret:str,auth_code:str) -> dict[str, Any]:
        host = 'https://api.oceanengine.com'
        path = '/open_api/oauth2/access_token/'
        url = host + path
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'app_id': app_id,
            'secret': secret,
            'auth_code': auth_code
        }
        async with AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            return response.json()
    async def _refresh_access_token(self,app_id:str,secret:str,refresh_token:str) -> dict[str, Any]:
        host = 'https://api.oceanengine.com'
        path = '/open_api/oauth2/refresh_token/'
        url = host + path
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'app_id': app_id,
            'secret': secret,
            'refresh_token': refresh_token
        }
        async with AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            return response.json()
    async def _get_available_dimensions_and_metrics_by_data_topic(self,advertiser_id:int,data_topics:list[str],access_token:str) -> dict[str, Any]:
        host = 'https://api.oceanengine.com'
        path = '/open_api/v3.0/report/custom/config/get/'
        url = host + path
        headers = {
            'Access-Token': access_token
        }
        data = {
            'advertiser_id': advertiser_id,
            'data_topics': json.dumps(data_topics)
        }
        async with AsyncClient() as client:
            response = await client.get(url, headers=headers, params=data)
            return response.json()
    async def _get_advertiser_list(self,access_token:str) -> dict[str, Any]:
        host = 'https://api.oceanengine.com'
        path = '/open_api/oauth2/advertiser/get/'
        url = host + path
        headers = {
            'Access-Token': access_token
        }
        async with AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.json()
    async def _get_customer_center_advertiser_list(self,cc_account_id:int,account_source:Literal['AD','ENTERPRISE','LOCAL'],access_token:str) -> dict[str, Any]:
        host = 'https://api.oceanengine.com'
        path = '/open_api/2/customer_center/advertiser/list/'
        url = host + path
        headers = {
            'Access-Token': access_token
        }
        params = {
            'cc_account_id': cc_account_id,
            'account_source': account_source
        }
        async with AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            return response.json()
    async def _fetch_data(self,access_token:str,advertiser_id:int,data_topic:str,dimensions:list[str],metrics:list[str],start_time:str,end_time:str,*,filters:dict,order_by:dict,page:int=1,page_size:int=10):
        cache_data = await self._utils.get_dimensions_and_metrics_cache('dimensions_and_metrics.json')
        dim_exclusions, metric_exclusions, dim_name_map, metric_name_map = await self._utils.build_exclusion_mappings(data_topic,cache_data)
        conflict_result = await self._utils.check_conflicts(dimensions,metrics,dim_exclusions,metric_exclusions,dim_name_map,metric_name_map)
        if conflict_result['has_conflict']:
            print("存在冲突：")
            for conflict in conflict_result['conflicts']:
                print(conflict['message'])
        else:
            print("无冲突，可以继续执行查询")


