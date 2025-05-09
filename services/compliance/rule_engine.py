"""规则引擎模块"""
from typing import Dict, Any, List, Callable, Awaitable
from datetime import datetime
import re
from .models import ComplianceRule, ComplianceViolation

class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        """初始化规则引擎"""
        self.rules_registry: Dict[str, ComplianceRule] = {}
        self.rule_executors: Dict[str, Callable] = {
            "阈值": self._check_threshold,
            "模式匹配": self._check_pattern,
            "时间序列": self._check_time_series,
            "清单": self._check_checklist
        }
    
    def register_rule(self, rule: ComplianceRule) -> None:
        """注册规则"""
        self.rules_registry[rule.rule_id] = rule
        
    def register_rules(self, rules: List[ComplianceRule]) -> None:
        """批量注册规则"""
        for rule in rules:
            self.register_rule(rule)
            
    async def evaluate_rule(
        self,
        rule_id: str,
        data: Dict[str, Any]
    ) -> ComplianceViolation:
        """评估规则"""
        if rule_id not in self.rules_registry:
            raise ValueError(f"未找到规则: {rule_id}")
            
        rule = self.rules_registry[rule_id]
        executor = self.rule_executors.get(rule.check_method)
        
        if not executor:
            raise ValueError(f"不支持的检查方法: {rule.check_method}")
            
        return await executor(rule, data)
        
    async def evaluate_rules(
        self,
        category: str = None,
        data: Dict[str, Any] = None
    ) -> List[ComplianceViolation]:
        """评估多个规则"""
        violations = []
        
        for rule_id, rule in self.rules_registry.items():
            if category and rule.category != category:
                continue
                
            try:
                violation = await self.evaluate_rule(rule_id, data)
                if violation:
                    violations.append(violation)
            except Exception as e:
                # 记录错误但继续执行其他规则
                print(f"规则 {rule_id} 评估失败: {str(e)}")
                
        return violations
        
    async def _check_threshold(
        self,
        rule: ComplianceRule,
        data: Dict[str, Any]
    ) -> ComplianceViolation:
        """阈值检查"""
        for key, threshold in rule.parameters.items():
            if key.startswith("min_") and data.get(key[4:], 0) < threshold:
                return self._create_violation(
                    rule,
                    f"{key[4:]}低于最小阈值 {threshold}"
                )
            elif key.startswith("max_") and data.get(key[4:], 0) > threshold:
                return self._create_violation(
                    rule,
                    f"{key[4:]}超过最大阈值 {threshold}"
                )
        return None
        
    async def _check_pattern(
        self,
        rule: ComplianceRule,
        data: Dict[str, Any]
    ) -> ComplianceViolation:
        """模式匹配检查"""
        patterns = rule.parameters.get("patterns", [])
        for pattern in patterns:
            if isinstance(pattern, str):
                # 字符串模式匹配
                if any(re.search(pattern, str(v)) for v in data.values()):
                    return self._create_violation(
                        rule,
                        f"匹配到违规模式: {pattern}"
                    )
            elif isinstance(pattern, dict):
                # 复杂模式匹配
                if self._match_complex_pattern(pattern, data):
                    return self._create_violation(
                        rule,
                        f"匹配到复杂违规模式"
                    )
        return None
        
    async def _check_time_series(
        self,
        rule: ComplianceRule,
        data: Dict[str, Any]
    ) -> ComplianceViolation:
        """时间序列检查"""
        time_data = data.get("time_series", [])
        if not time_data:
            return None
            
        # 检查时间范围
        allowed_ranges = rule.parameters.get("allowed_ranges", {})
        for timestamp, value in time_data:
            dt = datetime.fromisoformat(timestamp)
            range_key = "weekend" if dt.weekday() >= 5 else "weekday"
            
            if range_key in allowed_ranges:
                allowed = allowed_ranges[range_key]
                if not (allowed["start"] <= dt.time().strftime("%H:%M") <= allowed["end"]):
                    return self._create_violation(
                        rule,
                        f"时间 {dt} 超出允许范围"
                    )
                    
        return None
        
    async def _check_checklist(
        self,
        rule: ComplianceRule,
        data: Dict[str, Any]
    ) -> ComplianceViolation:
        """清单检查"""
        required_items = set(rule.parameters.get("required_items", []))
        current_items = set(data.get("items", []))
        
        missing_items = required_items - current_items
        if missing_items:
            return self._create_violation(
                rule,
                f"缺少必需项: {', '.join(missing_items)}"
            )
            
        return None
        
    def _create_violation(
        self,
        rule: ComplianceRule,
        description: str
    ) -> ComplianceViolation:
        """创建违规记录"""
        return ComplianceViolation(
            rule_id=rule.rule_id,
            timestamp=datetime.now(),
            severity=rule.severity,
            description=description,
            evidence={},  # 需要根据具体场景补充证据
            suggested_actions=self._get_suggested_actions(rule)
        )
        
    def _match_complex_pattern(
        self,
        pattern: Dict[str, Any],
        data: Dict[str, Any]
    ) -> bool:
        """匹配复杂模式"""
        for key, condition in pattern.items():
            if key not in data:
                continue
                
            value = data[key]
            if isinstance(condition, dict):
                if "min" in condition and value < condition["min"]:
                    return True
                if "max" in condition and value > condition["max"]:
                    return True
                if "pattern" in condition and re.search(condition["pattern"], str(value)):
                    return True
                    
        return False
        
    def _get_suggested_actions(self, rule: ComplianceRule) -> List[str]:
        """获取建议措施"""
        # 这里可以根据规则类型和参数生成具体的建议
        return [
            f"请检查{rule.category}相关的合规要求",
            f"及时整改{rule.name}相关的问题",
            "保存相关证据材料"
        ] 