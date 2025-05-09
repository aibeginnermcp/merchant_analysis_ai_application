"""
成本穿透分析服务

提供以下功能:
- 成本结构分析
- 成本趋势分析
- 成本预警分析
- 成本优化建议

Classes:
    CostCategory: 成本类别模型
    CostAnalysis: 成本分析结果模型
    CostAnalysisService: 成本穿透分析服务实现
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

from services.shared.service import BaseService
from services.shared.models import QueryParams

class CostCategory(BaseModel):
    """
    成本类别模型
    
    Attributes:
        id (str): 类别ID
        name (str): 类别名称
        parent_id (Optional[str]): 父类别ID
        description (str): 类别描述
        attributes (Dict[str, str]): 类别属性
    """
    id: str = Field(..., description="类别ID")
    name: str = Field(..., description="类别名称")
    parent_id: Optional[str] = Field(None, description="父类别ID")
    description: str = Field(..., description="类别描述")
    attributes: Dict[str, str] = Field(default_factory=dict, description="类别属性")

class CostItem(BaseModel):
    """成本项目模型"""
    id: str = Field(..., description="项目ID")
    category_id: str = Field(..., description="类别ID")
    name: str = Field(..., description="项目名称")
    amount: Decimal = Field(..., description="金额")
    unit: str = Field(..., description="计量单位")
    frequency: str = Field(..., description="发生频率")
    is_fixed: bool = Field(..., description="是否固定成本")
    start_date: datetime = Field(..., description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    tags: List[str] = Field(default_factory=list, description="标签")

class CostAnalysis(BaseModel):
    """
    成本分析结果模型
    
    Attributes:
        total_cost (Decimal): 总成本
        fixed_cost (Decimal): 固定成本
        variable_cost (Decimal): 变动成本
        cost_structure (Dict[str, Decimal]): 成本结构
        major_items (List[Dict]): 主要成本项
        trend_analysis (Dict): 趋势分析
        optimization_suggestions (List[str]): 优化建议
    """
    total_cost: Decimal = Field(..., description="总成本")
    fixed_cost: Decimal = Field(..., description="固定成本")
    variable_cost: Decimal = Field(..., description="变动成本")
    cost_structure: Dict[str, Decimal] = Field(..., description="成本结构")
    major_items: List[Dict] = Field(..., description="主要成本项")
    trend_analysis: Dict = Field(..., description="趋势分析")
    optimization_suggestions: List[str] = Field(..., description="优化建议")

class CostAnalysisService(BaseService):
    """
    成本穿透分析服务
    
    提供成本分析相关的核心功能实现,包括:
    - 成本类别管理
    - 成本数据分析
    - 成本趋势预测
    - 成本优化建议
    
    Attributes:
        categories (Dict[str, CostCategory]): 成本类别字典
    """
    
    def __init__(self):
        """
        初始化成本分析服务
        
        - 调用父类初始化
        - 初始化成本类别字典
        - 加载预定义成本类别
        """
        super().__init__(
            collection_name="cost_analysis",
            service_name="cost_analysis_service"
        )
        self.categories: Dict[str, CostCategory] = {}
        self._load_categories()
    
    def _load_categories(self):
        """
        加载成本类别
        
        从预定义配置中加载成本类别数据,包括:
        - 原材料成本
        - 人工成本
        - 制造费用
        - 运营费用
        """
        categories = [
            CostCategory(
                id="RAW_MATERIAL",
                name="原材料成本",
                description="直接用于生产的原材料成本",
                attributes={
                    "type": "direct",
                    "controllable": "yes"
                }
            ),
            CostCategory(
                id="LABOR",
                name="人工成本",
                description="直接和间接人工成本",
                attributes={
                    "type": "mixed",
                    "controllable": "partial"
                }
            ),
            CostCategory(
                id="OVERHEAD",
                name="制造费用",
                description="生产过程中的间接费用",
                attributes={
                    "type": "indirect",
                    "controllable": "partial"
                }
            ),
            CostCategory(
                id="OPERATION",
                name="运营费用",
                description="日常运营相关费用",
                attributes={
                    "type": "indirect",
                    "controllable": "yes"
                }
            )
        ]
        
        for category in categories:
            self.categories[category.id] = category
    
    async def analyze_cost_structure(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime,
        category_ids: Optional[List[str]] = None
    ) -> CostAnalysis:
        """
        分析成本结构
        
        Args:
            merchant_id: 商户ID
            start_date: 开始日期
            end_date: 结束日期
            category_ids: 成本类别ID列表
        
        Returns:
            CostAnalysis: 成本分析结果
        """
        # 获取成本数据
        cost_data = await self._get_cost_data(
            merchant_id,
            start_date,
            end_date,
            category_ids
        )
        
        # 计算总成本
        total_cost = sum(item.amount for item in cost_data)
        
        # 计算固定成本和变动成本
        fixed_cost = sum(item.amount for item in cost_data if item.is_fixed)
        variable_cost = total_cost - fixed_cost
        
        # 分析成本结构
        cost_structure = {}
        for category in self.categories.values():
            category_items = [
                item for item in cost_data
                if item.category_id == category.id
            ]
            if category_items:
                cost_structure[category.name] = sum(
                    item.amount for item in category_items
                )
        
        # 识别主要成本项
        sorted_items = sorted(
            cost_data,
            key=lambda x: x.amount,
            reverse=True
        )
        major_items = [
            {
                "name": item.name,
                "category": self.categories[item.category_id].name,
                "amount": item.amount,
                "percentage": (item.amount / total_cost * 100)
                if total_cost else 0
            }
            for item in sorted_items[:5]  # 取前5个主要成本项
        ]
        
        # 分析成本趋势
        trend_analysis = await self._analyze_cost_trend(
            merchant_id,
            start_date,
            end_date
        )
        
        # 生成优化建议
        optimization_suggestions = await self._generate_optimization_suggestions(
            cost_data,
            cost_structure,
            trend_analysis
        )
        
        return CostAnalysis(
            total_cost=total_cost,
            fixed_cost=fixed_cost,
            variable_cost=variable_cost,
            cost_structure=cost_structure,
            major_items=major_items,
            trend_analysis=trend_analysis,
            optimization_suggestions=optimization_suggestions
        )
    
    async def _get_cost_data(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime,
        category_ids: Optional[List[str]] = None
    ) -> List[CostItem]:
        """获取成本数据"""
        # 构建查询条件
        query = {
            "merchant_id": merchant_id,
            "start_date": {"$lte": end_date},
            "$or": [
                {"end_date": None},
                {"end_date": {"$gte": start_date}}
            ]
        }
        
        if category_ids:
            query["category_id"] = {"$in": category_ids}
        
        # 从数据库获取数据
        cursor = self.db["cost_items"].find(query)
        items = []
        async for doc in cursor:
            items.append(CostItem(**doc))
        
        return items
    
    async def _analyze_cost_trend(
        self,
        merchant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """分析成本趋势"""
        # 按月聚合成本数据
        pipeline = [
            {
                "$match": {
                    "merchant_id": merchant_id,
                    "start_date": {"$lte": end_date},
                    "$or": [
                        {"end_date": None},
                        {"end_date": {"$gte": start_date}}
                    ]
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$start_date"},
                        "month": {"$month": "$start_date"},
                        "category_id": "$category_id"
                    },
                    "total_amount": {"$sum": "$amount"}
                }
            },
            {
                "$sort": {
                    "_id.year": 1,
                    "_id.month": 1
                }
            }
        ]
        
        cursor = self.db["cost_items"].aggregate(pipeline)
        monthly_data = {}
        async for doc in cursor:
            year_month = f"{doc['_id']['year']}-{doc['_id']['month']:02d}"
            category_id = doc["_id"]["category_id"]
            if year_month not in monthly_data:
                monthly_data[year_month] = {}
            monthly_data[year_month][category_id] = doc["total_amount"]
        
        # 计算环比和同比
        trend_analysis = {
            "monthly_data": monthly_data,
            "mom_changes": {},  # 环比变化
            "yoy_changes": {}   # 同比变化
        }
        
        # TODO: 实现环比和同比计算
        
        return trend_analysis
    
    async def _generate_optimization_suggestions(
        self,
        cost_data: List[CostItem],
        cost_structure: Dict[str, Decimal],
        trend_analysis: Dict
    ) -> List[str]:
        """生成成本优化建议"""
        suggestions = []
        
        # 分析固定成本占比
        total_cost = sum(cost_structure.values())
        if total_cost > 0:
            fixed_cost = sum(
                item.amount for item in cost_data if item.is_fixed
            )
            fixed_cost_ratio = fixed_cost / total_cost
            
            if fixed_cost_ratio > 0.7:
                suggestions.append(
                    "固定成本占比过高(>70%)，建议考虑将部分固定成本转化为变动成本，"
                    "提高成本弹性"
                )
        
        # 分析成本集中度
        if cost_structure:
            max_category_cost = max(cost_structure.values())
            max_category_ratio = max_category_cost / total_cost
            
            if max_category_ratio > 0.5:
                suggestions.append(
                    "单一成本类别占比过高(>50%)，建议适当分散成本结构，"
                    "降低成本集中风险"
                )
        
        # 分析成本趋势
        # TODO: 基于趋势分析生成更多建议
        
        return suggestions
    
    async def get_cost_history(
        self,
        merchant_id: str,
        query_params: Optional[QueryParams] = None
    ) -> Dict:
        """获取成本历史记录"""
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