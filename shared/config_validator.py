"""配置验证工具"""
from typing import Dict, Any, List, Optional
import re
from pathlib import Path
import yaml
from pydantic import BaseModel, validator, ValidationError
from .config import BaseConfig

class ConfigValidationError(Exception):
    """配置验证错误"""
    
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("\n".join(errors))

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, config_dir: str = "config"):
        """初始化配置验证器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        
    def validate_yaml_syntax(self, filename: str) -> List[str]:
        """验证YAML语法
        
        Args:
            filename: 文件名
            
        Returns:
            List[str]: 错误列表
        """
        errors = []
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return [f"配置文件 {filename} 不存在"]
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"YAML语法错误: {str(e)}")
            
        return errors
        
    def validate_environment_variables(
        self,
        config: BaseConfig,
        env_vars: Dict[str, str]
    ) -> List[str]:
        """验证环境变量
        
        Args:
            config: 配置对象
            env_vars: 环境变量字典
            
        Returns:
            List[str]: 错误列表
        """
        errors = []
        required_fields = config.__fields__
        
        # 检查必需的环境变量
        for field_name, field in required_fields.items():
            if field.required:
                env_var = field_name.upper()
                if env_var not in env_vars:
                    errors.append(f"缺少必需的环境变量: {env_var}")
                    
        # 验证环境变量值
        for var_name, var_value in env_vars.items():
            field_name = var_name.lower()
            if field_name in required_fields:
                field = required_fields[field_name]
                try:
                    field.type_(var_value)
                except (ValueError, ValidationError) as e:
                    errors.append(f"环境变量 {var_name} 值无效: {str(e)}")
                    
        return errors
        
    def validate_mongodb_uri(self, uri: str) -> List[str]:
        """验证MongoDB URI
        
        Args:
            uri: MongoDB URI
            
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        # 验证URI格式
        uri_pattern = r"^mongodb(\+srv)?://([^:]+:[^@]+@)?[^/]+(:\d+)?(/[^?]+)?(\?.*)?$"
        if not re.match(uri_pattern, uri):
            errors.append("MongoDB URI格式无效")
            
        return errors
        
    def validate_redis_uri(self, uri: str) -> List[str]:
        """验证Redis URI
        
        Args:
            uri: Redis URI
            
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        # 验证URI格式
        uri_pattern = r"^redis://([^:]+:[^@]+@)?[^/]+(:\d+)?(/\d+)?$"
        if not re.match(uri_pattern, uri):
            errors.append("Redis URI格式无效")
            
        return errors
        
    def validate_service_config(
        self,
        service_name: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """验证服务配置
        
        Args:
            service_name: 服务名称
            config: 配置数据
            
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        # 验证基础配置
        if "SERVICE_NAME" not in config:
            errors.append("缺少服务名称配置")
        if "SERVICE_PORT" not in config:
            errors.append("缺少服务端口配置")
            
        # 验证数据库配置
        if "MONGODB_URI" in config:
            errors.extend(self.validate_mongodb_uri(config["MONGODB_URI"]))
            
        # 验证Redis配置
        if "REDIS_URI" in config:
            errors.extend(self.validate_redis_uri(config["REDIS_URI"]))
            
        # 验证服务特定配置
        if service_name == "data-simulator":
            if "SIMULATION_BATCH_SIZE" not in config:
                errors.append("缺少批处理大小配置")
            if "SIMULATION_THREADS" not in config:
                errors.append("缺少线程数配置")
                
        elif service_name == "cashflow":
            if "MODEL_PATH" not in config:
                errors.append("缺少模型路径配置")
            if "PREDICTION_WINDOW" not in config:
                errors.append("缺少预测窗口配置")
                
        elif service_name == "cost-analyzer":
            if "ANALYSIS_THREADS" not in config:
                errors.append("缺少分析线程数配置")
            if "COST_CATEGORIES" not in config:
                errors.append("缺少成本类别配置")
                
        elif service_name == "compliance":
            if "RULES_PATH" not in config:
                errors.append("缺少规则路径配置")
            if "UPDATE_INTERVAL" not in config:
                errors.append("缺少更新间隔配置")
                
        return errors
        
    def validate_all_configs(self) -> Dict[str, List[str]]:
        """验证所有配置
        
        Returns:
            Dict[str, List[str]]: 服务名称到错误列表的映射
        """
        validation_results = {}
        
        # 验证全局配置
        global_errors = self.validate_yaml_syntax("global.yml")
        if global_errors:
            validation_results["global"] = global_errors
            
        # 验证服务配置
        for service_name in [
            "data-simulator",
            "cashflow",
            "cost-analyzer",
            "compliance"
        ]:
            errors = self.validate_yaml_syntax(f"{service_name}.yml")
            if errors:
                validation_results[service_name] = errors
                
        return validation_results
        
    def validate_config_dependencies(self, config: Dict[str, Any]) -> List[str]:
        """验证配置依赖关系
        
        Args:
            config: 配置数据
            
        Returns:
            List[str]: 错误列表
        """
        errors = []
        
        # 验证文件路径
        for key in ["MODEL_PATH", "RULES_PATH"]:
            if key in config:
                path = Path(config[key])
                if not path.exists():
                    errors.append(f"路径不存在: {path}")
                    
        # 验证端口冲突
        used_ports = set()
        for key in config:
            if key.endswith("_PORT"):
                port = config[key]
                if port in used_ports:
                    errors.append(f"端口 {port} 已被使用")
                used_ports.add(port)
                
        # 验证服务依赖
        if "DEPENDENCIES" in config:
            for dep in config["DEPENDENCIES"]:
                if dep not in config:
                    errors.append(f"缺少依赖服务配置: {dep}")
                    
        return errors
        
# 导出验证器实例
config_validator = ConfigValidator() 