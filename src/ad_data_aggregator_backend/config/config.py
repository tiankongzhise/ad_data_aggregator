from ad_data_aggregator_backend.logger import update_logger_config,add_custom_logger_level,CustomLoggerLevel,LoggerParams
from loguru import logger
import tomllib


def _load_config(config_file: str) -> dict:
    with open(config_file, "rb") as f:
        return tomllib.load(f)

def _get_logger_config(config: dict) -> tuple[list[CustomLoggerLevel]|None,list[LoggerParams]|None]:
    logger_config = config.get("logger",{})
    if not logger_config:
        return None,None
    logger_params_config = logger_config.get("sink")
    custom_logger_levels_config = logger_config.get("custom_level")
    if custom_logger_levels_config is None:
        logger_levels = None
    else:
        logger_levels = []
        for key,value in custom_logger_levels_config.items():
            logger_levels.append(CustomLoggerLevel(level_name=key, level_num=value.get("level_num"), color=value.get("color"), icon=value.get("icon")))
    if logger_params_config is None:
        logger_params = None
    else:
        logger_params = []
        for _,value in logger_params_config.items():
            logger_params.append(LoggerParams(**value))
    return logger_levels,logger_params


def _update_logger_settings(logger_levels: list[CustomLoggerLevel]|None,logger_params: list[LoggerParams]|None):
    try:
        if logger_levels is not None:
            add_custom_logger_level(logger_levels)
        if logger_params is not None:
            update_logger_config(logger_params)
    except Exception as e:
        logger.error(f"更新日志配置失败: {e},将使用默认日志配置")
        raise e 


class AdDataAggregatorConfig:
    def __init__(self, config_file: str):
        self._config = _load_config(config_file)

    
    def update_logger_settings(self):
        logger_levels,logger_params = _get_logger_config(self._config)
        _update_logger_settings(logger_levels,logger_params)






ad_data_aggregator_config = AdDataAggregatorConfig("config.toml")
ad_data_aggregator_config.update_logger_settings()



if __name__ == "__main__":
    logger.log("SERVICE_INFO","test")
    logger.log("SERVICE_DEBUG","test")
    logger.log("METHOD_INFO","test")
    logger.log("METHOD_DEBUG","test")
    logger.log("PRIVATE_IMPLEMENTATION_INFO","test")
    logger.log("PRIVATE_IMPLEMENTATION_DEBUG","test")
    logger.log("CORE_INFO","test")
    logger.log("CORE_DEBUG","test")
