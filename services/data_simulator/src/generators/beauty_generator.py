"""
美妆个护行业数据生成器
负责生成美妆个护零售店的模拟数据，包括商品信息、会员信息、销售数据和库存数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
import uuid
from faker import Faker
from typing import Dict, List, Tuple, Optional
import logging

from config.base_config import (
    TIME_CONFIG,
    VOLUME_CONFIG,
    USER_ATTRIBUTES,
    PAYMENT_METHODS
)
from config.beauty_config import (
    PRODUCT_CATEGORY_CONFIG,
    USER_PROFILE_CONFIG,
    CHANNEL_CONFIG,
    PROMOTION_CONFIG,
    USER_BEHAVIOR_CONFIG,
    INVENTORY_CONFIG,
    MEMBERSHIP_CONFIG
)

class BeautyGenerator:
    """美妆个护行业数据生成器类
    
    负责生成完整的美妆个护零售模拟数据集，包括：
    1. 商品基础信息
    2. 会员信息（包含用户画像）
    3. 销售订单数据
    4. 库存数据
    5. 用户行为数据
    
    主要特点：
    - 模拟线上线下全渠道销售
    - 实现会员画像和个性化推荐
    - 包含商品生命周期管理
    - 模拟用户购物行为轨迹
    """
    
    def __init__(self, seed: Optional[int] = None):
        """初始化数据生成器
        
        Args:
            seed (Optional[int]): 随机种子，用于保证数据可重复生成
        """
        # 设置随机种子
        if seed is not None:
            np.random.seed(seed)
            
        self.faker = Faker('zh_CN')
        self.start_date = datetime.strptime(TIME_CONFIG['start_date'], '%Y-%m-%d')
        self.end_date = datetime.strptime(TIME_CONFIG['end_date'], '%Y-%m-%d')
        
        # 初始化商品和会员数量
        self.product_count = np.random.randint(800, 1500)  # 商品数量
        self.member_count = np.random.randint(
            VOLUME_CONFIG['min_users'],
            VOLUME_CONFIG['max_users']
        )
        
        # 初始化日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 数据质量控制参数
        self.quality_metrics = {
            'missing_rate': 0.02,  # 缺失值比例
            'anomaly_rate': 0.03,  # 异常值比例
            'data_validation_rules': {
                'min_order_amount': 30,    # 最小订单金额
                'max_order_amount': 5000,  # 最大订单金额
                'max_single_purchase': 5   # 单次最大购买数量
            }
        }
        
    def generate_product_base(self) -> pd.DataFrame:
        """生成商品基础信息表
        
        生成规则：
        1. 商品ID全局唯一
        2. 按配置的品类分布生成商品
        3. 包含品牌、功效、价格等信息
        4. 设置上下架时间和保质期
        
        Returns:
            pd.DataFrame: 商品基础信息数据框
        """
        self.logger.info(f"开始生成{self.product_count}个商品的基础信息...")
        
        products = []
        for _ in range(self.product_count):
            # 选择商品品类
            category = np.random.choice(
                list(PRODUCT_CATEGORY_CONFIG['category_distribution'].keys()),
                p=list(PRODUCT_CATEGORY_CONFIG['category_distribution'].values())
            )
            
            # 选择子品类
            subcategory = np.random.choice(
                PRODUCT_CATEGORY_CONFIG['categories'][category]['subcategories']
            )
            
            # 选择品牌定位
            brand_position = np.random.choice(
                list(PRODUCT_CATEGORY_CONFIG['categories'][category]['brand_distribution'].keys()),
                p=list(PRODUCT_CATEGORY_CONFIG['categories'][category]['brand_distribution'].values())
            )
            
            # 生成价格
            price_range = PRODUCT_CATEGORY_CONFIG['categories'][category]['price_ranges'][subcategory]
            price = round(np.random.uniform(price_range['min'], price_range['max']), 2)
            
            # 生成上架时间
            launch_date = self.faker.date_time_between(
                start_date=self.start_date - timedelta(days=180),
                end_date=self.end_date - timedelta(days=30)
            )
            
            # 计算保质期
            shelf_life = INVENTORY_CONFIG['shelf_life'][category]
            expiry_date = launch_date + timedelta(days=shelf_life)
            
            # 设置商品状态
            if (self.end_date - launch_date).days > 365:
                status = np.random.choice(['active', 'discontinued'], p=[0.85, 0.15])
            else:
                status = 'active'
            
            product = {
                'product_id': f'p_{uuid.uuid4().hex[:8]}',
                'category': category,
                'subcategory': subcategory,
                'brand_position': brand_position,
                'brand': self._generate_brand_name(brand_position, category),
                'name': self._generate_product_name(category, subcategory),
                'price': price,
                'launch_date': launch_date,
                'expiry_date': expiry_date,
                'status': status,
                'efficacy': self._generate_efficacy(category, subcategory),
                'target_skin_type': self._generate_target_skin_type(category),
                'ingredients': self._generate_ingredients(category, subcategory),
                'storage_requirements': self._generate_storage_requirements(category),
                'min_stock': self._determine_min_stock(category, subcategory)
            }
            products.append(product)
        
        df = pd.DataFrame(products)
        
        # 数据质量检查
        self._validate_product_data(df)
        
        self.logger.info(f"商品基础信息生成完成，共{len(df)}条记录")
        return df
    
    def generate_member_base(self) -> pd.DataFrame:
        """生成会员基础信息表
        
        生成规则：
        1. 会员ID全局唯一
        2. 包含基础属性和用户画像
        3. 记录消费累计和积分情况
        4. 设置会员权益和偏好信息
        
        Returns:
            pd.DataFrame: 会员基础信息数据框
        """
        self.logger.info(f"开始生成{self.member_count}个会员的基础信息...")
        
        members = []
        for _ in range(self.member_count):
            # 生成注册时间
            register_date = self.faker.date_time_between(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # 生成会员属性
            age_group = np.random.choice(
                USER_ATTRIBUTES['age_groups'],
                p=USER_ATTRIBUTES['age_distribution']
            )
            gender = np.random.choice(
                list(USER_ATTRIBUTES['gender_distribution'].keys()),
                p=list(USER_ATTRIBUTES['gender_distribution'].values())
            )
            
            # 生成用户画像
            skin_type = np.random.choice(
                list(USER_PROFILE_CONFIG['skin_types']['distribution'].keys()),
                p=list(USER_PROFILE_CONFIG['skin_types']['distribution'].values())
            )
            
            makeup_style = np.random.choice(
                list(USER_PROFILE_CONFIG['makeup_styles']['distribution'].keys()),
                p=list(USER_PROFILE_CONFIG['makeup_styles']['distribution'].values())
            )
            
            fragrance_preference = np.random.choice(
                list(USER_PROFILE_CONFIG['fragrance_preferences']['distribution'].keys()),
                p=list(USER_PROFILE_CONFIG['fragrance_preferences']['distribution'].values())
            )
            
            # 生成购物行为特征
            purchase_frequency = np.random.choice(
                list(USER_PROFILE_CONFIG['purchase_behavior']['frequency'].keys()),
                p=list(USER_PROFILE_CONFIG['purchase_behavior']['frequency'].values())
            )
            
            price_sensitivity = np.random.choice(
                list(USER_PROFILE_CONFIG['purchase_behavior']['price_sensitivity'].keys()),
                p=list(USER_PROFILE_CONFIG['purchase_behavior']['price_sensitivity'].values())
            )
            
            member = {
                'member_id': f'm_{uuid.uuid4().hex[:8]}',
                'register_date': register_date,
                'age_group': age_group,
                'gender': gender,
                'skin_type': skin_type,
                'makeup_style': makeup_style,
                'fragrance_preference': fragrance_preference,
                'purchase_frequency': purchase_frequency,
                'price_sensitivity': price_sensitivity,
                'level': 'bronze',
                'total_spending': 0.0,
                'points': 0,
                'last_purchase_date': None,
                'preferred_channel': self._determine_preferred_channel(),
                'preferred_categories': self._determine_preferred_categories(
                    skin_type,
                    makeup_style
                )
            }
            members.append(member)
        
        df = pd.DataFrame(members)
        
        # 数据质量检查
        self._validate_member_data(df)
        
        self.logger.info(f"会员基础信息生成完成，共{len(df)}条记录")
        return df
    
    def _generate_brand_name(self, brand_position: str, category: str) -> str:
        """生成品牌名称
        
        Args:
            brand_position (str): 品牌定位
            category (str): 商品品类
            
        Returns:
            str: 品牌名称
        """
        # 根据品牌定位和品类生成合适的品牌名称
        if brand_position == 'luxury':
            prefixes = ['LA', 'DE', 'LE']
            suffixes = ['LUXE', 'PREMIUM', 'ELITE']
        elif brand_position == 'high_end':
            prefixes = ['PURE', 'NATURAL', 'BIO']
            suffixes = ['BEAUTY', 'CARE', 'ESSENCE']
        else:
            prefixes = ['DAILY', 'BASIC', 'SIMPLE']
            suffixes = ['SKIN', 'LIFE', 'PLUS']
            
        return f"{np.random.choice(prefixes)} {np.random.choice(suffixes)}"
    
    def _generate_product_name(self, category: str, subcategory: str) -> str:
        """生成商品名称
        
        Args:
            category (str): 商品品类
            subcategory (str): 子品类
            
        Returns:
            str: 商品名称
        """
        # 根据品类和子品类生成合适的名称
        if category == 'skincare':
            effects = ['保湿', '修护', '清爽', '滋润', '净化']
            return f"{np.random.choice(effects)}{subcategory.replace('_', ' ').title()}"
        elif category == 'makeup':
            colors = ['自然', '裸妆', '珊瑚', '玫瑰', '蜜桃']
            return f"{np.random.choice(colors)}{subcategory.replace('_', ' ').title()}"
        elif category == 'perfume':
            notes = ['花香', '木质', '清新', '东方', '果香']
            return f"{np.random.choice(notes)}{subcategory.replace('_', ' ').title()}"
        else:
            return f"{subcategory.replace('_', ' ').title()}"
    
    def _generate_efficacy(self, category: str, subcategory: str) -> List[str]:
        """生成商品功效标签
        
        Args:
            category (str): 商品品类
            subcategory (str): 子品类
            
        Returns:
            List[str]: 功效标签列表
        """
        efficacy_pool = {
            'skincare': ['保湿', '补水', '控油', '美白', '抗衰', '修护'],
            'makeup': ['遮瑕', '持久', '防水', '滋润', '自然'],
            'perfume': ['持久', '清新', '淡雅', '浓郁'],
            'personal_care': ['清洁', '护理', '滋养', '防护']
        }
        
        # 随机选择2-4个功效标签
        return np.random.choice(
            efficacy_pool[category],
            size=np.random.randint(2, 5),
            replace=False
        ).tolist()
    
    def _generate_target_skin_type(self, category: str) -> Optional[str]:
        """生成目标肤质
        
        Args:
            category (str): 商品品类
            
        Returns:
            Optional[str]: 目标肤质
        """
        if category in ['skincare', 'makeup']:
            return np.random.choice(
                list(USER_PROFILE_CONFIG['skin_types']['distribution'].keys())
            )
        return None
    
    def _generate_ingredients(self, category: str, subcategory: str) -> List[str]:
        """生成商品成分列表
        
        Args:
            category (str): 商品品类
            subcategory (str): 子品类
            
        Returns:
            List[str]: 成分列表
        """
        # 根据品类和子品类生成主要成分
        base_ingredients = ['水', '甘油', '丙二醇']
        special_ingredients = {
            'skincare': ['玻尿酸', '维生素C', '烟酰胺', '神经酰胺'],
            'makeup': ['二氧化钛', '云母粉', '硅油', '色素'],
            'perfume': ['乙醇', '香精', '定香剂'],
            'personal_care': ['椰油酰胺', 'SLES', '防腐剂']
        }
        
        # 组合成分列表
        ingredients = base_ingredients.copy()
        ingredients.extend(
            np.random.choice(
                special_ingredients[category],
                size=np.random.randint(2, 4),
                replace=False
            )
        )
        return ingredients
    
    def _generate_storage_requirements(self, category: str) -> str:
        """生成存储要求
        
        Args:
            category (str): 商品品类
            
        Returns:
            str: 存储要求
        """
        requirements = []
        
        if category in ['skincare', 'makeup']:
            requirements.append('请置于阴凉干燥处')
            if category == 'skincare':
                requirements.append('避免阳光直射')
        elif category == 'perfume':
            requirements.append('避免高温和阳光直射')
        
        return '，'.join(requirements) if requirements else '常温存储' 