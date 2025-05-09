"""
合规检查服务实现

提供商户合规性检查功能：
- 财务合规检查
- 运营合规检查
- 资质合规检查
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from services.shared.service import BaseService
from services.shared.models import QueryParams

class ComplianceRule(BaseModel):
    """合规规则模型"""
    id: str = Field(..., description="规则ID")
    name: str = Field(..., description="规则名称")
    category: str = Field(..., description="规则类别")
    description: str = Field(..., description="规则描述")
    check_function: str = Field(..., description="检查函数名称")
    severity: str = Field(..., description="违规严重程度")
    enabled: bool = Field(default=True, description="是否启用")

class ComplianceCheck(BaseModel):
    """合规检查结果模型"""
    rule_id: str = Field(..., description="规则ID")
    passed: bool = Field(..., description="是否通过")
    details: Optional[Dict] = Field(default=None, description="详细信息")
    checked_at: datetime = Field(default_factory=datetime.utcnow, description="检查时间")

class ComplianceService(BaseService):
    """合规检查服务"""
    
    def __init__(self):
        super().__init__(
            collection_name="compliance_checks",
            service_name="compliance_service"
        )
        self.rules: Dict[str, ComplianceRule] = {}
        self._load_rules()
    
    def _load_rules(self):
        """加载合规检查规则"""
        # 这里应该从配置文件或数据库加载规则
        # 为演示目的，我们直接定义一些规则
        rules = [
            ComplianceRule(
                id="FIN001",
                name="现金流充足率检查",
                category="财务合规",
                description="检查商户现金流是否满足最低要求",
                check_function="check_cash_flow_ratio",
                severity="HIGH"
            ),
            ComplianceRule(
                id="FIN002",
                name="资产负债率检查",
                category="财务合规",
                description="检查商户资产负债率是否在合理范围",
                check_function="check_debt_ratio",
                severity="MEDIUM"
            ),
            ComplianceRule(
                id="OPS001",
                name="营业执照有效期检查",
                category="运营合规",
                description="检查商户营业执照是否在有效期内",
                check_function="check_license_validity",
                severity="HIGH"
            ),
            ComplianceRule(
                id="OPS002",
                name="经营场所合规检查",
                category="运营合规",
                description="检查商户经营场所是否符合要求",
                check_function="check_business_premises",
                severity="MEDIUM"
            )
        ]
        
        for rule in rules:
            self.rules[rule.id] = rule
    
    async def check_merchant_compliance(
        self,
        merchant_id: str,
        check_categories: Optional[List[str]] = None
    ) -> Dict:
        """
        检查商户合规性
        
        Args:
            merchant_id: 商户ID
            check_categories: 要检查的规则类别列表
        
        Returns:
            Dict: 检查结果
        """
        # 获取商户信息
        merchant_data = await self._get_merchant_data(merchant_id)
        if not merchant_data:
            raise ValueError(f"商户不存在: {merchant_id}")
        
        # 筛选要执行的规则
        rules_to_check = self.rules.values()
        if check_categories:
            rules_to_check = [
                rule for rule in rules_to_check
                if rule.category in check_categories
            ]
        
        # 执行检查
        check_results = []
        for rule in rules_to_check:
            if not rule.enabled:
                continue
                
            check_function = getattr(self, rule.check_function)
            try:
                passed, details = await check_function(merchant_data)
                check_results.append(
                    ComplianceCheck(
                        rule_id=rule.id,
                        passed=passed,
                        details=details
                    )
                )
            except Exception as e:
                check_results.append(
                    ComplianceCheck(
                        rule_id=rule.id,
                        passed=False,
                        details={"error": str(e)}
                    )
                )
        
        # 保存检查结果
        result = {
            "merchant_id": merchant_id,
            "check_time": datetime.utcnow(),
            "results": [r.dict() for r in check_results]
        }
        await self.create(result)
        
        return result
    
    async def _get_merchant_data(self, merchant_id: str) -> Optional[Dict]:
        """获取商户数据"""
        # 首先尝试从缓存获取
        cache_key = f"merchant:{merchant_id}"
        cached_data = await self.get_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库获取
        merchant_data = await self.db["merchants"].find_one({"_id": merchant_id})
        if merchant_data:
            # 缓存数据
            await self.set_cache(cache_key, merchant_data, expire=3600)
        
        return merchant_data
    
    async def check_cash_flow_ratio(self, merchant_data: Dict) -> tuple[bool, Dict]:
        """检查现金流充足率"""
        try:
            cash_inflow = merchant_data.get("monthly_cash_inflow", 0)
            cash_outflow = merchant_data.get("monthly_cash_outflow", 0)
            
            if cash_outflow == 0:
                return True, {"message": "无现金流出"}
            
            ratio = cash_inflow / cash_outflow
            passed = ratio >= 1.2  # 要求现金流入是流出的1.2倍以上
            
            return passed, {
                "current_ratio": ratio,
                "minimum_required": 1.2,
                "message": "现金流充足" if passed else "现金流不足"
            }
        except Exception as e:
            return False, {"error": f"计算现金流充足率时出错: {str(e)}"}
    
    async def check_debt_ratio(self, merchant_data: Dict) -> tuple[bool, Dict]:
        """检查资产负债率"""
        try:
            total_assets = merchant_data.get("total_assets", 0)
            total_liabilities = merchant_data.get("total_liabilities", 0)
            
            if total_assets == 0:
                return False, {"message": "总资产为0"}
            
            ratio = total_liabilities / total_assets
            passed = ratio <= 0.7  # 要求资产负债率不超过70%
            
            return passed, {
                "current_ratio": ratio,
                "maximum_allowed": 0.7,
                "message": "资产负债率正常" if passed else "资产负债率过高"
            }
        except Exception as e:
            return False, {"error": f"计算资产负债率时出错: {str(e)}"}
    
    async def check_license_validity(self, merchant_data: Dict) -> tuple[bool, Dict]:
        """检查营业执照有效期"""
        try:
            license_expire_date = merchant_data.get("license_expire_date")
            if not license_expire_date:
                return False, {"message": "未提供营业执照有效期信息"}
            
            expire_date = datetime.fromisoformat(license_expire_date)
            now = datetime.utcnow()
            
            # 检查是否在有效期内，且距离过期还有3个月以上
            days_to_expire = (expire_date - now).days
            passed = days_to_expire > 90
            
            return passed, {
                "expire_date": license_expire_date,
                "days_to_expire": days_to_expire,
                "message": "营业执照有效" if passed else "营业执照即将过期或已过期"
            }
        except Exception as e:
            return False, {"error": f"检查营业执照有效期时出错: {str(e)}"}
    
    async def check_business_premises(self, merchant_data: Dict) -> tuple[bool, Dict]:
        """检查经营场所合规性"""
        try:
            premises_type = merchant_data.get("premises_type")
            if not premises_type:
                return False, {"message": "未提供经营场所信息"}
            
            # 检查经营场所类型是否允许
            allowed_types = ["self_owned", "leased", "authorized"]
            if premises_type not in allowed_types:
                return False, {
                    "current_type": premises_type,
                    "allowed_types": allowed_types,
                    "message": "经营场所类型不符合要求"
                }
            
            # 如果是租赁，检查租约有效期
            if premises_type == "leased":
                lease_expire_date = merchant_data.get("lease_expire_date")
                if not lease_expire_date:
                    return False, {"message": "未提供租约到期日信息"}
                
                expire_date = datetime.fromisoformat(lease_expire_date)
                now = datetime.utcnow()
                days_to_expire = (expire_date - now).days
                
                if days_to_expire <= 90:
                    return False, {
                        "expire_date": lease_expire_date,
                        "days_to_expire": days_to_expire,
                        "message": "租约即将到期"
                    }
            
            return True, {
                "premises_type": premises_type,
                "message": "经营场所合规"
            }
        except Exception as e:
            return False, {"error": f"检查经营场所时出错: {str(e)}"}
    
    async def get_compliance_history(
        self,
        merchant_id: str,
        query_params: Optional[QueryParams] = None
    ) -> Dict:
        """获取商户合规检查历史"""
        if not query_params:
            query_params = QueryParams()
        
        # 添加商户ID过滤条件
        if not query_params.filters:
            query_params.filters = []
        query_params.filters.append({
            "field": "merchant_id",
            "operator": "eq",
            "value": merchant_id
        })
        
        return await self.get_many(query_params) 