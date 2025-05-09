"""配置管理工具"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from .config import get_config, get_service_config

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.config_cache: Dict[str, Any] = {}
        
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """加载YAML配置文件
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 配置数据
        """
        file_path = self.config_dir / filename
        if not file_path.exists():
            return {}
            
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def save_yaml(self, filename: str, data: Dict[str, Any]) -> None:
        """保存YAML配置文件
        
        Args:
            filename: 文件名
            data: 配置数据
        """
        file_path = self.config_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)
            
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """获取服务配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            Dict[str, Any]: 服务配置
        """
        if service_name not in self.config_cache:
            # 加载基础配置
            config = get_service_config(service_name)
            base_config = {
                k: v for k, v in config.dict().items()
                if not k.startswith("_")
            }
            
            # 加载YAML配置
            yaml_config = self.load_yaml(f"{service_name}.yml")
            
            # 合并配置
            self.config_cache[service_name] = {
                **base_config,
                **yaml_config
            }
            
        return self.config_cache[service_name]
        
    def update_service_config(
        self,
        service_name: str,
        updates: Dict[str, Any]
    ) -> None:
        """更新服务配置
        
        Args:
            service_name: 服务名称
            updates: 更新数据
        """
        # 获取当前配置
        current_config = self.get_service_config(service_name)
        
        # 更新配置
        current_config.update(updates)
        
        # 保存到YAML
        self.save_yaml(f"{service_name}.yml", current_config)
        
        # 清除缓存
        self.config_cache.pop(service_name, None)
        
    def get_global_config(self) -> Dict[str, Any]:
        """获取全局配置
        
        Returns:
            Dict[str, Any]: 全局配置
        """
        if "global" not in self.config_cache:
            # 加载基础配置
            config = get_config()
            base_config = {
                k: v for k, v in config.dict().items()
                if not k.startswith("_")
            }
            
            # 加载YAML配置
            yaml_config = self.load_yaml("global.yml")
            
            # 合并配置
            self.config_cache["global"] = {
                **base_config,
                **yaml_config
            }
            
        return self.config_cache["global"]
        
    def update_global_config(self, updates: Dict[str, Any]) -> None:
        """更新全局配置
        
        Args:
            updates: 更新数据
        """
        # 获取当前配置
        current_config = self.get_global_config()
        
        # 更新配置
        current_config.update(updates)
        
        # 保存到YAML
        self.save_yaml("global.yml", current_config)
        
        # 清除缓存
        self.config_cache.pop("global", None)
        
    def reload_config(self, service_name: Optional[str] = None) -> None:
        """重新加载配置
        
        Args:
            service_name: 服务名称，为None时重载所有配置
        """
        if service_name:
            self.config_cache.pop(service_name, None)
        else:
            self.config_cache.clear()
            
    def validate_config(self, service_name: str) -> bool:
        """验证服务配置
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 配置是否有效
        """
        try:
            config = get_service_config(service_name)
            return True
        except Exception:
            return False
            
    def get_environment_overrides(self) -> Dict[str, str]:
        """获取环境变量覆盖值
        
        Returns:
            Dict[str, str]: 环境变量字典
        """
        return {
            key: value for key, value in os.environ.items()
            if key.startswith((
                "SERVICE_",
                "MONGODB_",
                "REDIS_",
                "JWT_",
                "CONSUL_",
                "DATA_SIMULATOR_",
                "CASHFLOW_",
                "COST_ANALYZER_",
                "COMPLIANCE_"
            ))
        }
        
    def apply_environment_overrides(self) -> None:
        """应用环境变量覆盖值"""
        overrides = self.get_environment_overrides()
        
        for service_name in [
            "data-simulator",
            "cashflow",
            "cost-analyzer",
            "compliance"
        ]:
            config = self.get_service_config(service_name)
            updates = {
                key: value for key, value in overrides.items()
                if key.startswith(f"{service_name.upper()}_")
            }
            if updates:
                self.update_service_config(service_name, updates)
                
# 导出配置管理器实例
config_manager = ConfigManager() 