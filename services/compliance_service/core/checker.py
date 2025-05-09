"""
合规检查器实现
"""
from typing import List, Dict, Any, Tuple
import uuid
from datetime import datetime
from .models import MerchantInfo, CheckResult, ComplianceReport
from .rule_engine import RuleEngine

class ComplianceChecker:
    """
    合规检查器类
    负责执行合规检查并生成报告
    """
    
    def __init__(self, rule_engine: RuleEngine):
        """
        初始化检查器
        
        Args:
            rule_engine (RuleEngine): 规则引擎实例
        """
        self.rule_engine = rule_engine
        self._register_default_check_methods()
        
    def _register_default_check_methods(self):
        """注册默认检查方法"""
        self.rule_engine.register_check_method("check_registered_capital", self._check_registered_capital)
        self.rule_engine.register_check_method("check_business_scope", self._check_business_scope)
        self.rule_engine.register_check_method("check_establishment_period", self._check_establishment_period)
        
    def _check_registered_capital(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        检查注册资本是否满足要求
        
        Args:
            context (Dict[str, Any]): 检查上下文
            parameters (Dict[str, Any]): 规则参数
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (是否通过, 违规详情)
        """
        merchant = context["merchant"]
        min_capital = parameters.get("min_capital", 0)
        
        if merchant["registered_capital"] < min_capital:
            return False, {
                "current_capital": merchant["registered_capital"],
                "required_capital": min_capital,
                "difference": min_capital - merchant["registered_capital"]
            }
        return True, {}
        
    def _check_business_scope(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        检查经营范围是否包含必需项
        
        Args:
            context (Dict[str, Any]): 检查上下文
            parameters (Dict[str, Any]): 规则参数
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (是否通过, 违规详情)
        """
        merchant = context["merchant"]
        required_items = parameters.get("required_items", [])
        business_scope = merchant["business_scope"].lower()
        
        missing_items = [
            item for item in required_items
            if item.lower() not in business_scope
        ]
        
        if missing_items:
            return False, {
                "missing_items": missing_items
            }
        return True, {}
        
    def _check_establishment_period(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        检查成立时间是否满足要求
        
        Args:
            context (Dict[str, Any]): 检查上下文
            parameters (Dict[str, Any]): 规则参数
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (是否通过, 违规详情)
        """
        merchant = context["merchant"]
        min_years = parameters.get("min_years", 0)
        
        establishment_date = datetime.fromisoformat(merchant["establishment_date"])
        years = (datetime.now() - establishment_date).days / 365
        
        if years < min_years:
            return False, {
                "current_years": round(years, 1),
                "required_years": min_years,
                "difference": round(min_years - years, 1)
            }
        return True, {}
        
    def check_merchant(self, merchant: MerchantInfo, rule_types: List[str] = None) -> ComplianceReport:
        """
        执行商户合规检查
        
        Args:
            merchant (MerchantInfo): 商户信息
            rule_types (List[str], optional): 规则类型过滤
            
        Returns:
            ComplianceReport: 合规检查报告
        """
        # 执行所有适用规则检查
        check_results = self.rule_engine.check_merchant(merchant, rule_types)
        
        # 计算风险评分
        risk_score = self.rule_engine.evaluate_risk_score(check_results)
        
        # 确定整体合规状态
        if risk_score >= 70:
            overall_status = "high_risk"
        elif risk_score >= 30:
            overall_status = "medium_risk"
        else:
            overall_status = "low_risk"
            
        # 生成改进建议
        recommendations = self._generate_recommendations(check_results)
        
        # 生成总体评估
        summary = self._generate_summary(check_results, risk_score)
        
        # 创建报告
        report = ComplianceReport(
            report_id=str(uuid.uuid4()),
            merchant_id=merchant.merchant_id,
            check_time=datetime.now(),
            overall_status=overall_status,
            risk_score=risk_score,
            check_results=check_results,
            summary=summary,
            recommendations=recommendations
        )
        
        return report
        
    def _generate_recommendations(self, results: List[CheckResult]) -> List[str]:
        """
        根据检查结果生成改进建议
        
        Args:
            results (List[CheckResult]): 检查结果列表
            
        Returns:
            List[str]: 改进建议列表
        """
        recommendations = []
        
        for result in results:
            if not result.result:  # 检查未通过
                rule = self.rule_engine.get_rule(result.rule_id)
                if rule:
                    if rule.rule_type == "financial":
                        recommendations.append(
                            f"建议完善财务管理制度，特别是在{rule.rule_name}方面"
                        )
                    elif rule.rule_type == "qualification":
                        recommendations.append(
                            f"需要补充或更新{rule.rule_name}相关资质文件"
                        )
                    elif rule.rule_type == "risk":
                        recommendations.append(
                            f"建议加强{rule.rule_name}相关风险控制"
                        )
                        
        return list(set(recommendations))  # 去重
        
    def _generate_summary(self, results: List[CheckResult], risk_score: float) -> str:
        """
        生成总体评估摘要
        
        Args:
            results (List[CheckResult]): 检查结果列表
            risk_score (float): 风险评分
            
        Returns:
            str: 评估摘要
        """
        total_checks = len(results)
        failed_checks = len([r for r in results if not r.result])
        high_risk_issues = len([r for r in results if not r.result and r.risk_level == "high"])
        
        summary = f"本次合规检查共执行{total_checks}项检查，"
        
        if failed_checks == 0:
            summary += "未发现违规问题。"
        else:
            summary += f"发现{failed_checks}项不合规情况，"
            if high_risk_issues > 0:
                summary += f"其中{high_risk_issues}项为高风险问题，"
            summary += f"整体风险评分为{risk_score}分。"
            
        return summary 