"""
3C数码行业数据生成器
负责生成3C数码零售店的模拟数据，包括商品信息、销售数据、会员数据和售后服务数据
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
from config.electronics_config import (
    PRODUCT_CATEGORY_CONFIG,
    CHANNEL_CONFIG,
    USER_BEHAVIOR_CONFIG,
    PROMOTION_CONFIG,
    AFTER_SALES_CONFIG,
    INVENTORY_CONFIG,
    MEMBERSHIP_CONFIG
)

class ElectronicsGenerator:
    """3C数码行业数据生成器类
    
    负责生成完整的3C数码零售模拟数据集，包括：
    1. 商品基础信息
    2. 会员信息
    3. 销售订单数据
    4. 库存数据
    5. 售后服务数据
    
    主要特点：
    - 模拟线上线下全渠道销售
    - 实现会员等级和权益系统
    - 包含商品生命周期管理
    - 模拟售后服务流程
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
        self.product_count = np.random.randint(500, 1000)  # 商品数量
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
                'min_order_amount': 50,    # 最小订单金额
                'max_order_amount': 50000, # 最大订单金额
                'max_single_purchase': 3   # 单次最大购买数量
            }
        }
        
    def generate_product_base(self) -> pd.DataFrame:
        """生成商品基础信息表
        
        生成规则：
        1. 商品ID全局唯一
        2. 按配置的品类分布生成商品
        3. 包含品牌、型号、价格等信息
        4. 设置上下架时间和库存预警值
        
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
            
            # 选择品牌
            brand = np.random.choice(
                list(PRODUCT_CATEGORY_CONFIG['categories'][category]['brand_distribution'].keys()),
                p=list(PRODUCT_CATEGORY_CONFIG['categories'][category]['brand_distribution'].values())
            )
            
            # 生成价格
            price_range = PRODUCT_CATEGORY_CONFIG['categories'][category]['price_ranges'][subcategory]
            price = round(np.random.uniform(price_range['min'], price_range['max']), 2)
            
            # 生成上架时间
            launch_date = self.faker.date_time_between(
                start_date=self.start_date - timedelta(days=180),  # 考虑更早上架的商品
                end_date=self.end_date - timedelta(days=30)  # 预留下架时间
            )
            
            # 设置商品状态
            if (self.end_date - launch_date).days > 365:
                status = np.random.choice(['active', 'discontinued'], p=[0.8, 0.2])
            else:
                status = 'active'
            
            product = {
                'product_id': f'p_{uuid.uuid4().hex[:8]}',
                'category': category,
                'subcategory': subcategory,
                'brand': brand,
                'model': f'{brand}_{self.faker.random_number(digits=6)}',
                'name': self._generate_product_name(brand, subcategory),
                'price': price,
                'launch_date': launch_date,
                'status': status,
                'warranty_period': AFTER_SALES_CONFIG['warranty_period'][category],
                'min_stock': self._determine_min_stock(category, subcategory),
                'storage_cost': INVENTORY_CONFIG['storage_cost'][category]
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
        2. 包含基础属性和会员等级信息
        3. 记录消费累计和积分情况
        4. 设置会员权益和优惠信息
        
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
            
            # 初始化会员等级
            initial_level = 'bronze'
            
            member = {
                'member_id': f'm_{uuid.uuid4().hex[:8]}',
                'register_date': register_date,
                'age_group': age_group,
                'gender': gender,
                'level': initial_level,
                'total_spending': 0.0,
                'points': 0,
                'last_purchase_date': None,
                'preferred_channel': self._determine_preferred_channel(),
                'device_preference': self._determine_device_preference()
            }
            members.append(member)
        
        df = pd.DataFrame(members)
        
        # 数据质量检查
        self._validate_member_data(df)
        
        self.logger.info(f"会员基础信息生成完成，共{len(df)}条记录")
        return df
    
    def _generate_product_name(self, brand: str, subcategory: str) -> str:
        """生成商品名称
        
        Args:
            brand (str): 品牌名
            subcategory (str): 子品类名
            
        Returns:
            str: 商品名称
        """
        # 根据子品类生成合适的名称模板
        templates = {
            'smartphone': [f'{brand} 智能手机', f'{brand} 5G手机', f'{brand} 折叠屏手机'],
            'laptop': [f'{brand} 笔记本电脑', f'{brand} 轻薄本', f'{brand} 游戏本'],
            'dslr': [f'{brand} 单反相机', f'{brand} 专业相机', f'{brand} 高清相机'],
            'headphone': [f'{brand} 无线耳机', f'{brand} 降噪耳机', f'{brand} 游戏耳机']
        }
        
        if subcategory in templates:
            return np.random.choice(templates[subcategory])
        else:
            return f'{brand} {subcategory.replace("_", " ").title()}'
    
    def _determine_min_stock(self, category: str, subcategory: str) -> int:
        """确定商品最小库存
        
        Args:
            category (str): 商品品类
            subcategory (str): 子品类
            
        Returns:
            int: 最小库存数量
        """
        # 基础最小库存
        base_stock = {
            'mobile': 20,
            'computer': 15,
            'camera': 10,
            'accessory': 50
        }
        
        # 根据子品类调整
        multiplier = 1.0
        if subcategory in ['smartphone', 'laptop', 'headphone']:
            multiplier = 1.5
        elif subcategory in ['feature_phone', 'desktop', 'case']:
            multiplier = 0.8
            
        return int(base_stock[category] * multiplier)
    
    def _determine_preferred_channel(self) -> str:
        """确定会员偏好购物渠道
        
        Returns:
            str: 偏好渠道
        """
        if np.random.random() < CHANNEL_CONFIG['online']['distribution']:
            return np.random.choice(
                list(CHANNEL_CONFIG['online']['platforms'].keys()),
                p=list(CHANNEL_CONFIG['online']['platforms'].values())
            )
        else:
            return np.random.choice(
                list(CHANNEL_CONFIG['offline']['store_types'].keys()),
                p=list(CHANNEL_CONFIG['offline']['store_types'].values())
            )
    
    def _determine_device_preference(self) -> str:
        """确定会员偏好使用设备
        
        Returns:
            str: 偏好设备
        """
        return np.random.choice(
            list(USER_BEHAVIOR_CONFIG['device_preferences'].keys()),
            p=list(USER_BEHAVIOR_CONFIG['device_preferences'].values())
        )
    
    def _validate_product_data(self, df: pd.DataFrame) -> None:
        """验证商品数据质量
        
        Args:
            df (pd.DataFrame): 商品数据框
        """
        # 检查商品ID唯一性
        if df['product_id'].duplicated().any():
            self.logger.warning("发现重复的商品ID")
            
        # 检查必填字段完整性
        required_fields = [
            'product_id', 'category', 'subcategory',
            'brand', 'price', 'launch_date'
        ]
        for field in required_fields:
            missing_rate = df[field].isnull().mean()
            if missing_rate > self.quality_metrics['missing_rate']:
                self.logger.warning(f"字段{field}的缺失率({missing_rate:.2%})超过阈值")
                
        # 检查价格合理性
        for category in PRODUCT_CATEGORY_CONFIG['categories']:
            for subcategory, price_range in PRODUCT_CATEGORY_CONFIG['categories'][category]['price_ranges'].items():
                invalid_prices = df[
                    (df['category'] == category) &
                    (df['subcategory'] == subcategory) &
                    ((df['price'] < price_range['min']) | (df['price'] > price_range['max']))
                ]
                if len(invalid_prices) > 0:
                    self.logger.warning(f"发现{len(invalid_prices)}个{category}-{subcategory}价格异常的商品")
    
    def _validate_member_data(self, df: pd.DataFrame) -> None:
        """验证会员数据质量
        
        Args:
            df (pd.DataFrame): 会员数据框
        """
        # 检查会员ID唯一性
        if df['member_id'].duplicated().any():
            self.logger.warning("发现重复的会员ID")
            
        # 检查必填字段完整性
        required_fields = [
            'member_id', 'register_date', 'level',
            'total_spending', 'points'
        ]
        for field in required_fields:
            missing_rate = df[field].isnull().mean()
            if missing_rate > self.quality_metrics['missing_rate']:
                self.logger.warning(f"字段{field}的缺失率({missing_rate:.2%})超过阈值")
                
        # 检查会员等级有效性
        if not df['level'].isin(MEMBERSHIP_CONFIG['levels'].keys()).all():
            self.logger.warning("发现无效的会员等级") 
    
    def generate_sales_orders(
        self,
        product_df: pd.DataFrame,
        member_df: pd.DataFrame
    ) -> pd.DataFrame:
        """生成销售订单数据
        
        生成规则：
        1. 考虑线上线下渠道特征
        2. 实现促销活动影响
        3. 模拟会员购买行为
        4. 计算订单相关费用
        
        Args:
            product_df (pd.DataFrame): 商品基础信息表
            member_df (pd.DataFrame): 会员基础信息表
            
        Returns:
            pd.DataFrame: 销售订单数据框
        """
        self.logger.info("开始生成销售订单数据...")
        
        orders = []
        
        # 遍历每一天
        current_date = self.start_date
        while current_date <= self.end_date:
            # 判断是否特殊日期
            special_date = (current_date.month, current_date.day)
            is_special_date = special_date in PROMOTION_CONFIG['special_dates']
            
            # 计算基础订单量
            base_orders = int(len(member_df) * 0.02)  # 基础日均2%的会员下单
            if is_special_date:
                base_orders = int(
                    base_orders * 
                    PROMOTION_CONFIG['special_dates'][special_date]['traffic_multiplier']
                )
            
            # 生成当天订单
            daily_orders = self._generate_daily_orders(
                current_date,
                product_df,
                member_df,
                base_orders,
                is_special_date
            )
            orders.extend(daily_orders)
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(orders)
        
        # 数据质量检查
        self._validate_sales_order_data(df)
        
        # 更新会员消费记录
        self._update_member_purchase_history(member_df, df)
        
        self.logger.info(f"销售订单数据生成完成，共{len(df)}条记录")
        return df
    
    def generate_inventory_records(
        self,
        product_df: pd.DataFrame,
        sales_df: pd.DataFrame
    ) -> pd.DataFrame:
        """生成库存记录数据
        
        生成规则：
        1. 跟踪商品库存变化
        2. 实现补货机制
        3. 计算库存成本
        4. 记录库存预警
        
        Args:
            product_df (pd.DataFrame): 商品基础信息表
            sales_df (pd.DataFrame): 销售订单数据表
            
        Returns:
            pd.DataFrame: 库存记录数据框
        """
        self.logger.info("开始生成库存记录数据...")
        
        inventory_records = []
        
        # 初始化每个商品的库存
        for _, product in product_df.iterrows():
            initial_stock = self._calculate_initial_stock(product)
            
            record = {
                'record_id': f'ir_{uuid.uuid4().hex[:8]}',
                'product_id': product['product_id'],
                'date': self.start_date,
                'opening_stock': initial_stock,
                'closing_stock': initial_stock,
                'replenishment_qty': 0,
                'sales_qty': 0,
                'storage_cost': round(initial_stock * product['storage_cost'] / 30, 2),  # 日均存储成本
                'stock_status': self._determine_stock_status(initial_stock, product['min_stock'])
            }
            inventory_records.append(record)
        
        # 按日期更新库存记录
        current_date = self.start_date + timedelta(days=1)
        while current_date <= self.end_date:
            # 获取前一天的库存记录
            prev_date = current_date - timedelta(days=1)
            prev_records = {r['product_id']: r for r in inventory_records if r['date'] == prev_date}
            
            # 获取当天的销售数据
            daily_sales = sales_df[
                sales_df['order_date'].dt.date == current_date.date()
            ]
            
            # 更新每个商品的库存
            for _, product in product_df.iterrows():
                prev_record = prev_records.get(product['product_id'])
                if not prev_record:
                    continue
                
                # 计算销售数量
                sales_qty = daily_sales[
                    daily_sales['product_id'] == product['product_id']
                ]['quantity'].sum()
                
                # 判断是否需要补货
                opening_stock = prev_record['closing_stock']
                replenishment_qty = self._calculate_replenishment_qty(
                    opening_stock,
                    product['min_stock'],
                    product
                )
                
                # 计算期末库存
                closing_stock = opening_stock + replenishment_qty - sales_qty
                
                record = {
                    'record_id': f'ir_{uuid.uuid4().hex[:8]}',
                    'product_id': product['product_id'],
                    'date': current_date,
                    'opening_stock': opening_stock,
                    'closing_stock': closing_stock,
                    'replenishment_qty': replenishment_qty,
                    'sales_qty': sales_qty,
                    'storage_cost': round(closing_stock * product['storage_cost'] / 30, 2),
                    'stock_status': self._determine_stock_status(closing_stock, product['min_stock'])
                }
                inventory_records.append(record)
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(inventory_records)
        
        # 数据质量检查
        self._validate_inventory_data(df)
        
        self.logger.info(f"库存记录数据生成完成，共{len(df)}条记录")
        return df
    
    def generate_after_sales(
        self,
        sales_df: pd.DataFrame,
        product_df: pd.DataFrame
    ) -> pd.DataFrame:
        """生成售后服务数据
        
        生成规则：
        1. 模拟维修、退换货情况
        2. 考虑保修期内外区别
        3. 记录处理结果和成本
        4. 跟踪服务满意度
        
        Args:
            sales_df (pd.DataFrame): 销售订单数据表
            product_df (pd.DataFrame): 商品基础信息表
            
        Returns:
            pd.DataFrame: 售后服务数据框
        """
        self.logger.info("开始生成售后服务数据...")
        
        after_sales_records = []
        
        # 遍历销售订单
        for _, order in sales_df.iterrows():
            # 判断是否发生售后问题
            if np.random.random() > 0.05:  # 假设5%的订单会有售后问题
                continue
            
            # 获取商品信息
            product = product_df[
                product_df['product_id'] == order['product_id']
            ].iloc[0]
            
            # 生成售后时间
            service_date = self.faker.date_time_between(
                start_date=order['order_date'],
                end_date=order['order_date'] + timedelta(days=365)
            )
            
            # 判断是否在保修期内
            in_warranty = (service_date - order['order_date']).days <= product['warranty_period']
            
            # 生成售后记录
            record = self._generate_after_sales_record(
                order,
                product,
                service_date,
                in_warranty
            )
            after_sales_records.append(record)
        
        df = pd.DataFrame(after_sales_records)
        
        # 数据质量检查
        self._validate_after_sales_data(df)
        
        self.logger.info(f"售后服务数据生成完成，共{len(df)}条记录")
        return df
    
    def _generate_daily_orders(
        self,
        date: datetime,
        product_df: pd.DataFrame,
        member_df: pd.DataFrame,
        order_count: int,
        is_special_date: bool
    ) -> List[dict]:
        """生成某一天的订单数据
        
        Args:
            date (datetime): 日期
            product_df (pd.DataFrame): 商品数据
            member_df (pd.DataFrame): 会员数据
            order_count (int): 订单数量
            is_special_date (bool): 是否特殊日期
            
        Returns:
            List[dict]: 订单记录列表
        """
        orders = []
        
        # 随机选择下单会员
        selected_members = member_df.sample(n=min(order_count, len(member_df)))
        
        for _, member in selected_members.iterrows():
            # 确定购买渠道
            channel = self._determine_purchase_channel(member['preferred_channel'])
            
            # 生成订单时间
            order_time = self._generate_order_time(date, channel)
            
            # 选择购买商品
            order_items = self._generate_order_items(
                product_df,
                member,
                is_special_date
            )
            
            # 计算订单金额
            total_amount = sum(item['price'] * item['quantity'] for item in order_items)
            
            # 应用会员折扣
            member_discount = MEMBERSHIP_CONFIG['levels'][member['level']]['discount']
            final_amount = round(total_amount * member_discount, 2)
            
            # 计算积分
            points_earned = int(
                final_amount * 
                MEMBERSHIP_CONFIG['levels'][member['level']]['point_rate']
            )
            
            order = {
                'order_id': f'o_{uuid.uuid4().hex[:8]}',
                'member_id': member['member_id'],
                'order_date': order_time,
                'channel': channel,
                'items': order_items,
                'total_amount': total_amount,
                'final_amount': final_amount,
                'points_earned': points_earned,
                'payment_method': self._determine_payment_method(channel)
            }
            
            # 添加渠道特定信息
            if channel in CHANNEL_CONFIG['online']['platforms']:
                order.update({
                    'platform_commission': round(
                        final_amount * 
                        CHANNEL_CONFIG['online']['commission_rates'][channel],
                        2
                    ),
                    'delivery_fee': self._calculate_delivery_fee(total_amount)
                })
            
            orders.append(order)
        
        return orders
    
    def _calculate_initial_stock(self, product: pd.Series) -> int:
        """计算商品初始库存
        
        Args:
            product (pd.Series): 商品信息
            
        Returns:
            int: 初始库存数量
        """
        base_stock = product['min_stock'] * 2
        
        # 根据品类调整
        if product['category'] in ['mobile', 'computer']:
            base_stock = int(base_stock * 1.2)  # 高价值商品多备货20%
        elif product['category'] == 'accessory':
            base_stock = int(base_stock * 1.5)  # 配件类商品多备货50%
            
        return base_stock
    
    def _calculate_replenishment_qty(
        self,
        current_stock: int,
        min_stock: int,
        product: pd.Series
    ) -> int:
        """计算补货数量
        
        Args:
            current_stock (int): 当前库存
            min_stock (int): 最小库存
            product (pd.Series): 商品信息
            
        Returns:
            int: 补货数量
        """
        if current_stock > min_stock:
            return 0
            
        # 基础补货量
        base_qty = min_stock * 2 - current_stock
        
        # 根据商品类型调整
        if product['category'] in ['mobile', 'computer']:
            base_qty = int(base_qty * 0.8)  # 高价值商品补货量较少
        elif product['category'] == 'accessory':
            base_qty = int(base_qty * 1.2)  # 配件类商品补货量较多
            
        return max(base_qty, 0)
    
    def _determine_stock_status(self, current_stock: int, min_stock: int) -> str:
        """确定库存状态
        
        Args:
            current_stock (int): 当前库存
            min_stock (int): 最小库存
            
        Returns:
            str: 库存状态
        """
        if current_stock <= 0:
            return 'out_of_stock'
        elif current_stock < min_stock:
            return 'low_stock'
        elif current_stock < min_stock * 2:
            return 'normal'
        else:
            return 'sufficient'
    
    def _generate_after_sales_record(
        self,
        order: pd.Series,
        product: pd.Series,
        service_date: datetime,
        in_warranty: bool
    ) -> dict:
        """生成售后服务记录
        
        Args:
            order (pd.Series): 订单信息
            product (pd.Series): 商品信息
            service_date (datetime): 服务日期
            in_warranty (bool): 是否在保修期内
            
        Returns:
            dict: 售后服务记录
        """
        # 确定问题类型
        issue_type = np.random.choice(
            list(AFTER_SALES_CONFIG['issue_types'].keys()),
            p=list(AFTER_SALES_CONFIG['issue_types'].values())
        )
        
        # 确定服务类型
        if issue_type in ['hardware_failure', 'software_issue']:
            service_type = 'repair'
        else:
            service_type = np.random.choice(['repair', 'replacement'])
        
        # 确定是否收费
        if in_warranty:
            is_paid = np.random.random() < AFTER_SALES_CONFIG['service_types'][service_type]['warranty']['paid']
        else:
            is_paid = True
        
        # 生成服务费用
        service_fee = 0
        if is_paid:
            if service_type == 'repair':
                service_fee = round(product['price'] * np.random.uniform(0.1, 0.3), 2)
            else:
                service_fee = round(product['price'] * np.random.uniform(0.5, 0.8), 2)
        
        return {
            'service_id': f'as_{uuid.uuid4().hex[:8]}',
            'order_id': order['order_id'],
            'product_id': product['product_id'],
            'service_date': service_date,
            'issue_type': issue_type,
            'service_type': service_type,
            'in_warranty': in_warranty,
            'is_paid': is_paid,
            'service_fee': service_fee,
            'status': 'completed',
            'satisfaction_score': np.random.randint(1, 6)  # 1-5分
        }
    
    def _validate_sales_order_data(self, df: pd.DataFrame) -> None:
        """验证销售订单数据质量
        
        Args:
            df (pd.DataFrame): 订单数据框
        """
        # 检查订单ID唯一性
        if df['order_id'].duplicated().any():
            self.logger.warning("发现重复的订单ID")
            
        # 检查订单金额范围
        invalid_amounts = df[
            (df['final_amount'] < self.quality_metrics['data_validation_rules']['min_order_amount']) |
            (df['final_amount'] > self.quality_metrics['data_validation_rules']['max_order_amount'])
        ]
        if len(invalid_amounts) > 0:
            self.logger.warning(f"发现{len(invalid_amounts)}笔金额异常的订单")
            
        # 检查渠道有效性
        valid_channels = (
            list(CHANNEL_CONFIG['online']['platforms'].keys()) +
            list(CHANNEL_CONFIG['offline']['store_types'].keys())
        )
        if not df['channel'].isin(valid_channels).all():
            self.logger.warning("发现无效的销售渠道")
    
    def _validate_inventory_data(self, df: pd.DataFrame) -> None:
        """验证库存数据质量
        
        Args:
            df (pd.DataFrame): 库存数据框
        """
        # 检查记录ID唯一性
        if df['record_id'].duplicated().any():
            self.logger.warning("发现重复的库存记录ID")
            
        # 检查库存逻辑
        invalid_stock = df[df['closing_stock'] < 0]
        if len(invalid_stock) > 0:
            self.logger.warning(f"发现{len(invalid_stock)}条负库存记录")
            
        # 检查补货逻辑
        invalid_replenishment = df[
            (df['replenishment_qty'] < 0) |
            (df['replenishment_qty'] > 1000)  # 假设单次补货不超过1000
        ]
        if len(invalid_replenishment) > 0:
            self.logger.warning(f"发现{len(invalid_replenishment)}条异常补货记录")
    
    def _validate_after_sales_data(self, df: pd.DataFrame) -> None:
        """验证售后服务数据质量
        
        Args:
            df (pd.DataFrame): 售后服务数据框
        """
        # 检查服务记录ID唯一性
        if df['service_id'].duplicated().any():
            self.logger.warning("发现重复的服务记录ID")
            
        # 检查服务类型有效性
        valid_service_types = list(AFTER_SALES_CONFIG['service_types'].keys())
        if not df['service_type'].isin(valid_service_types).all():
            self.logger.warning("发现无效的服务类型")
            
        # 检查问题类型有效性
        valid_issue_types = list(AFTER_SALES_CONFIG['issue_types'].keys())
        if not df['issue_type'].isin(valid_issue_types).all():
            self.logger.warning("发现无效的问题类型")
            
        # 检查满意度评分范围
        if not df['satisfaction_score'].between(1, 5).all():
            self.logger.warning("发现超出范围的满意度评分")
    
    def generate_all_data(self) -> Dict[str, pd.DataFrame]:
        """生成所有数据表
        
        Returns:
            Dict[str, pd.DataFrame]: 包含所有数据表的字典
        """
        self.logger.info("开始生成全部数据...")
        
        # 生成商品基础信息
        product_df = self.generate_product_base()
        
        # 生成会员基础信息
        member_df = self.generate_member_base()
        
        # 生成销售订单数据
        sales_df = self.generate_sales_orders(product_df, member_df)
        
        # 生成库存记录数据
        inventory_df = self.generate_inventory_records(product_df, sales_df)
        
        # 生成售后服务数据
        after_sales_df = self.generate_after_sales(sales_df, product_df)
        
        self.logger.info("所有数据生成完成")
        
        return {
            'product_base': product_df,
            'member_base': member_df,
            'sales_orders': sales_df,
            'inventory_records': inventory_df,
            'after_sales': after_sales_df
        }
    
    def _determine_purchase_channel(self, preferred_channel: str) -> str:
        """确定实际购买渠道
        
        Args:
            preferred_channel (str): 偏好渠道
            
        Returns:
            str: 实际购买渠道
        """
        # 80%概率使用偏好渠道
        if np.random.random() < 0.8:
            return preferred_channel
            
        # 20%概率选择其他渠道
        if preferred_channel in CHANNEL_CONFIG['online']['platforms']:
            # 线上用户偶尔会去线下店
            return np.random.choice(
                list(CHANNEL_CONFIG['offline']['store_types'].keys()),
                p=list(CHANNEL_CONFIG['offline']['store_types'].values())
            )
        else:
            # 线下用户偶尔会在线上购买
            return np.random.choice(
                list(CHANNEL_CONFIG['online']['platforms'].keys()),
                p=list(CHANNEL_CONFIG['online']['platforms'].values())
            )
    
    def _generate_order_time(self, date: datetime, channel: str) -> datetime:
        """生成订单时间
        
        Args:
            date (datetime): 日期
            channel (str): 购买渠道
            
        Returns:
            datetime: 订单时间
        """
        if channel in CHANNEL_CONFIG['online']['platforms']:
            # 线上订单全天24小时都可能产生
            hour = np.random.randint(0, 24)
            minute = np.random.randint(0, 60)
        else:
            # 线下店铺通常10:00-22:00营业
            hour = np.random.randint(10, 22)
            minute = np.random.randint(0, 60)
            
        return datetime.combine(date.date(), time(hour, minute))
    
    def _generate_order_items(
        self,
        product_df: pd.DataFrame,
        member: pd.Series,
        is_special_date: bool
    ) -> List[dict]:
        """生成订单商品明细
        
        Args:
            product_df (pd.DataFrame): 商品数据
            member (pd.Series): 会员信息
            is_special_date (bool): 是否特殊日期
            
        Returns:
            List[dict]: 订单商品明细列表
        """
        # 确定购买商品数量
        if is_special_date:
            item_count = np.random.randint(1, 4)  # 特殊日期可能买多件
        else:
            item_count = np.random.randint(1, 3)  # 普通日期通常买1-2件
            
        items = []
        # 选择要购买的商品
        available_products = product_df[product_df['status'] == 'active']
        selected_products = available_products.sample(n=min(item_count, len(available_products)))
        
        for _, product in selected_products.iterrows():
            # 确定购买数量
            if product['category'] in ['mobile', 'computer', 'camera']:
                quantity = 1  # 大件商品通常买一个
            else:
                quantity = np.random.randint(1, self.quality_metrics['data_validation_rules']['max_single_purchase'] + 1)
                
            # 计算商品价格（考虑促销）
            unit_price = self._calculate_product_price(
                product,
                is_special_date,
                member['level']
            )
            
            item = {
                'product_id': product['product_id'],
                'quantity': quantity,
                'unit_price': unit_price,
                'price': round(unit_price * quantity, 2)
            }
            items.append(item)
            
        return items
    
    def _calculate_product_price(
        self,
        product: pd.Series,
        is_special_date: bool,
        member_level: str
    ) -> float:
        """计算商品实际销售价格
        
        Args:
            product (pd.Series): 商品信息
            is_special_date (bool): 是否特殊日期
            member_level (str): 会员等级
            
        Returns:
            float: 实际销售价格
        """
        base_price = product['price']
        
        # 特殊日期折扣
        if is_special_date:
            special_date = (datetime.now().month, datetime.now().day)
            if special_date in PROMOTION_CONFIG['special_dates']:
                discount_range = PROMOTION_CONFIG['special_dates'][special_date]['discount_range']
                discount = np.random.uniform(discount_range[0], discount_range[1])
                base_price = round(base_price * discount, 2)
                
        # 会员折扣
        member_discount = MEMBERSHIP_CONFIG['levels'][member_level]['discount']
        final_price = round(base_price * member_discount, 2)
        
        return final_price
    
    def _determine_payment_method(self, channel: str) -> str:
        """确定支付方式
        
        Args:
            channel (str): 购买渠道
            
        Returns:
            str: 支付方式
        """
        if channel in CHANNEL_CONFIG['online']['platforms']:
            # 线上以电子支付为主
            return np.random.choice(
                list(PAYMENT_METHODS['online'].keys()),
                p=list(PAYMENT_METHODS['online'].values())
            )
        else:
            # 线下支持更多支付方式
            return np.random.choice(
                list(PAYMENT_METHODS['offline'].keys()),
                p=list(PAYMENT_METHODS['offline'].values())
            )
    
    def _calculate_delivery_fee(self, order_amount: float) -> float:
        """计算配送费
        
        Args:
            order_amount (float): 订单金额
            
        Returns:
            float: 配送费
        """
        if order_amount >= 2000:  # 订单满2000免运费
            return 0.0
        elif order_amount >= 1000:  # 订单满1000收取基础运费的一半
            return 10.0
        else:
            return 20.0  # 基础运费
    
    def _update_member_purchase_history(
        self,
        member_df: pd.DataFrame,
        order_df: pd.DataFrame
    ) -> None:
        """更新会员购买历史
        
        Args:
            member_df (pd.DataFrame): 会员数据框
            order_df (pd.DataFrame): 订单数据框
        """
        # 按会员统计消费
        member_stats = order_df.groupby('member_id').agg({
            'final_amount': 'sum',
            'points_earned': 'sum',
            'order_date': 'max'
        }).reset_index()
        
        # 更新会员信息
        for _, stats in member_stats.iterrows():
            member_df.loc[
                member_df['member_id'] == stats['member_id'],
                ['total_spending', 'points', 'last_purchase_date']
            ] = [
                stats['final_amount'],
                stats['points_earned'],
                stats['order_date']
            ]
            
            # 更新会员等级
            self._update_member_level(
                member_df,
                stats['member_id'],
                stats['final_amount']
            )
    
    def _update_member_level(
        self,
        member_df: pd.DataFrame,
        member_id: str,
        total_spending: float
    ) -> None:
        """更新会员等级
        
        Args:
            member_df (pd.DataFrame): 会员数据框
            member_id (str): 会员ID
            total_spending (float): 总消费金额
        """
        # 确定新的会员等级
        new_level = 'bronze'
        for level, config in MEMBERSHIP_CONFIG['levels'].items():
            if total_spending >= config['spending_threshold']:
                new_level = level
                
        # 更新会员等级
        member_df.loc[
            member_df['member_id'] == member_id,
            'level'
        ] = new_level 