"""
规则加载器模块
用于动态加载和管理审计规则
"""

import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class RuleLoader:
    """规则加载器类"""
    
    def __init__(self, rules_dir: str = "audit_rules"):
        """
        初始化规则加载器
        
        Args:
            rules_dir: 规则文件目录
        """
        self.rules_dir = Path(rules_dir)
        self.rules_cache: Dict[str, Any] = {}
        self.last_load_time: Dict[str, datetime] = {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("RuleLoader")
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler("logs/rule_loader.log")
        file_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def load_rules(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载所有规则
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            Dict[str, Any]: 加载的规则字典
        """
        all_rules = {}
        
        try:
            # 确保规则目录存在
            self.rules_dir.mkdir(parents=True, exist_ok=True)
            
            # 遍历所有YAML文件
            for rule_file in self.rules_dir.glob("*.yaml"):
                rules = self._load_rule_file(rule_file, force_reload)
                if rules:
                    all_rules[rule_file.stem] = rules
            
            self.logger.info(f"成功加载 {len(all_rules)} 个规则文件")
            return all_rules
            
        except Exception as e:
            self.logger.error(f"加载规则时发生错误: {str(e)}")
            raise
    
    def _load_rule_file(self, file_path: Path, force_reload: bool) -> Optional[Dict]:
        """
        加载单个规则文件
        
        Args:
            file_path: 规则文件路径
            force_reload: 是否强制重新加载
            
        Returns:
            Optional[Dict]: 规则字典或None
        """
        try:
            # 检查文件是否需要重新加载
            if not force_reload and file_path.stem in self.rules_cache:
                last_load = self.last_load_time.get(file_path.stem)
                last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if last_load and last_load > last_modified:
                    self.logger.debug(f"使用缓存的规则: {file_path.name}")
                    return self.rules_cache[file_path.stem]
            
            # 加载并解析YAML文件
            with open(file_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            # 验证规则格式
            self._validate_rules(rules, file_path.name)
            
            # 更新缓存
            self.rules_cache[file_path.stem] = rules
            self.last_load_time[file_path.stem] = datetime.now()
            
            self.logger.info(f"成功加载规则文件: {file_path.name}")
            return rules
            
        except Exception as e:
            self.logger.error(f"加载规则文件 {file_path.name} 时发生错误: {str(e)}")
            return None
    
    def _validate_rules(self, rules: Dict, file_name: str) -> None:
        """
        验证规则格式
        
        Args:
            rules: 规则字典
            file_name: 规则文件名
        
        Raises:
            ValueError: 规则格式无效时抛出
        """
        required_fields = {'name', 'description', 'condition', 'severity', 'action'}
        
        for rule_type, rule_group in rules.items():
            for rule_id, rule in rule_group.items():
                missing_fields = required_fields - set(rule.keys())
                if missing_fields:
                    raise ValueError(
                        f"规则文件 {file_name} 中的规则 {rule_id} "
                        f"缺少必需字段: {missing_fields}"
                    )
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """
        根据规则ID获取规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            Optional[Dict]: 规则字典或None
        """
        for rules in self.rules_cache.values():
            for rule_group in rules.values():
                if rule_id in rule_group:
                    return rule_group[rule_id]
        return None
    
    def get_rules_by_type(self, rule_type: str) -> List[Dict]:
        """
        获取指定类型的所有规则
        
        Args:
            rule_type: 规则类型
            
        Returns:
            List[Dict]: 规则列表
        """
        rules = []
        for rule_file in self.rules_cache.values():
            if rule_type in rule_file:
                rules.extend(rule_file[rule_type].values())
        return rules
    
    def get_rules_by_severity(self, severity: str) -> List[Dict]:
        """
        获取指定严重程度的所有规则
        
        Args:
            severity: 严重程度
            
        Returns:
            List[Dict]: 规则列表
        """
        rules = []
        for rule_file in self.rules_cache.values():
            for rule_group in rule_file.values():
                for rule in rule_group.values():
                    if rule['severity'] == severity:
                        rules.append(rule)
        return rules
    
    def reload_rules(self) -> None:
        """强制重新加载所有规则"""
        self.rules_cache.clear()
        self.last_load_time.clear()
        self.load_rules(force_reload=True)
        self.logger.info("已重新加载所有规则")

if __name__ == "__main__":
    # 测试规则加载器
    loader = RuleLoader()
    rules = loader.load_rules()
    
    # 打印加载的规则统计信息
    total_rules = sum(
        len(rule_group) 
        for rule_file in rules.values() 
        for rule_group in rule_file.values()
    )
    print(f"共加载 {total_rules} 条规则")
    
    # 按类型统计规则数量
    for rule_file in rules.values():
        for rule_type, rule_group in rule_file.items():
            print(f"{rule_type}: {len(rule_group)} 条规则") 