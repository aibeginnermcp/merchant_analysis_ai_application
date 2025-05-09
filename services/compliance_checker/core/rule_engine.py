"""
合规检查规则引擎实现
"""
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import uuid
import logging
from .models import RuleDefinition, CheckResult, MerchantInfo

class RuleEngine:
    """
    规则引擎类
    负责规则的注册、执行和结果评估
    """
    
    def __init__(self):
        """初始化规则引擎"""
        self._rules: Dict[str, RuleDefinition] = {}
        self._check_methods: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_rule(self, rule: RuleDefinition) -> None:
        """
        注册新规则
        
        Args:
            rule (RuleDefinition): 规则定义对象
        """
        if rule.rule_id in self._rules:
            self.logger.warning(f"规则 {rule.rule_id} 已存在，将被覆盖")
        self._rules[rule.rule_id] = rule
        
    def register_check_method(self, method_name: str, method: Callable) -> None:
        """
        注册检查方法
        
        Args:
            method_name (str): 方法名称
            method (Callable): 检查方法实现
        """
        self._check_methods[method_name] = method
        
    def get_rule(self, rule_id: str) -> Optional[RuleDefinition]:
        """
        获取规则定义
        
        Args:
            rule_id (str): 规则ID
            
        Returns:
            Optional[RuleDefinition]: 规则定义对象
        """
        return self._rules.get(rule_id)
        
    def list_rules(self, rule_type: Optional[str] = None) -> List[RuleDefinition]:
        """
        列出所有规则
        
        Args:
            rule_type (Optional[str]): 规则类型过滤
            
        Returns:
            List[RuleDefinition]: 规则列表
        """
        if rule_type:
            return [rule for rule in self._rules.values() if rule.rule_type == rule_type]
        return list(self._rules.values())
        
    def execute_rule(self, rule_id: str, merchant: MerchantInfo, context: Dict[str, Any] = None) -> CheckResult:
        """
        执行单个规则检查
        
        Args:
            rule_id (str): 规则ID
            merchant (MerchantInfo): 商户信息
            context (Dict[str, Any], optional): 额外上下文信息
            
        Returns:
            CheckResult: 检查结果
            
        Raises:
            ValueError: 规则不存在或检查方法未注册
        """
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"规则 {rule_id} 不存在")
            
        if not rule.enabled:
            self.logger.info(f"规则 {rule_id} 已禁用，跳过检查")
            return CheckResult(
                check_id=str(uuid.uuid4()),
                merchant_id=merchant.merchant_id,
                rule_id=rule_id,
                result=True,
                risk_level="low",
                check_time=datetime.now()
            )
            
        check_method = self._check_methods.get(rule.check_method)
        if not check_method:
            raise ValueError(f"检查方法 {rule.check_method} 未注册")
            
        try:
            check_context = {
                "merchant": merchant.dict(),
                **(context or {})
            }
            
            # 执行检查方法
            result, details = check_method(check_context, rule.parameters)
            
            return CheckResult(
                check_id=str(uuid.uuid4()),
                merchant_id=merchant.merchant_id,
                rule_id=rule_id,
                result=result,
                violation_details=details if not result else None,
                risk_level=rule.severity if not result else "low",
                check_time=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"执行规则 {rule_id} 时发生错误: {str(e)}")
            raise
            
    def check_merchant(self, merchant: MerchantInfo, rule_types: Optional[List[str]] = None) -> List[CheckResult]:
        """
        对商户执行所有适用规则检查
        
        Args:
            merchant (MerchantInfo): 商户信息
            rule_types (Optional[List[str]]): 规则类型过滤列表
            
        Returns:
            List[CheckResult]: 检查结果列表
        """
        results = []
        rules = self.list_rules()
        
        if rule_types:
            rules = [rule for rule in rules if rule.rule_type in rule_types]
            
        for rule in rules:
            try:
                result = self.execute_rule(rule.rule_id, merchant)
                results.append(result)
            except Exception as e:
                self.logger.error(f"检查规则 {rule.rule_id} 失败: {str(e)}")
                continue
                
        return results
        
    def evaluate_risk_score(self, results: List[CheckResult]) -> float:
        """
        根据检查结果评估风险分数
        
        Args:
            results (List[CheckResult]): 检查结果列表
            
        Returns:
            float: 风险评分 (0-100)
        """
        if not results:
            return 0.0
            
        # 风险等级权重
        risk_weights = {
            "high": 1.0,
            "medium": 0.6,
            "low": 0.3
        }
        
        # 计算加权风险分数
        total_weight = 0
        total_score = 0
        
        for result in results:
            if not result.result:  # 只考虑未通过的检查
                weight = risk_weights.get(result.risk_level, 0.3)
                total_weight += weight
                total_score += weight * 100
                
        if total_weight == 0:
            return 0.0
            
        return round(total_score / total_weight, 2) 