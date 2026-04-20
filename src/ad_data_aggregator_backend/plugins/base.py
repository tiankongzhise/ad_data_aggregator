from typing import List, Dict, Any
from abc import ABC, abstractmethod

class PlatformPluginInterface(ABC):
    """所有广告平台插件必须实现的接口"""
    
    @abstractmethod
    async def fetch_data(
        self,
        credentials: Dict[str, str],   # 解密后的API密钥等
        report_type: str,              # 如 "ad_plan_daily"
        dimensions: List[str],         # ["date", "plan_id"]
        metrics: List[str],            # ["cost", "click"]
        start_time: str,               # 数据起始时间（字符串形式如"2026-01-01" 或者"2026-01-01 00:00:00"）
        end_time: str,                 # 数据结束时间（字符串形式如"2026-01-01" 或者"2026-01-01 00:00:00"） 起止时间格式必须一致    
    ) -> List[Dict[str, Any]]:
        """
        调用平台API，返回原始数据列表。
        每个dict包含维度字段和指标字段，字段名保持平台原始命名。
        """
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        pass
