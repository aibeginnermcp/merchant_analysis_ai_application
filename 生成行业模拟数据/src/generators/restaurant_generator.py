"""
餐饮行业数据生成器
负责生成餐饮店的模拟数据，包括订单信息、顾客就餐数据、外卖数据和服务质量数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
from config.restaurant_config import (
    DISH_CONFIG,
    RESTAURANT_TYPE_CONFIG,
    DINING_DURATION_CONFIG,
    PROMOTION_CONFIG,
    SERVICE_QUALITY_CONFIG,
    DELIVERY_CONFIG,
    BUSINESS_HOURS_CONFIG
)

class RestaurantGenerator:
    """餐饮行业数据生成器类
    
    负责生成完整的餐饮行业模拟数据集，包括：
    1. 顾客基础信息
    2. 堂食订单数据
    3. 外卖订单数据
    4. 服务质量数据
    
    主要特点：
    - 模拟真实的餐饮运营特征
    - 考虑餐位周转率和高峰期特征
    - 实现堂食和外卖双渠道数据
    - 包含服务质量和投诉反馈
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
        
        # 初始化顾客数量
        self.customer_count = np.random.randint(
            VOLUME_CONFIG['min_users'],
            VOLUME_CONFIG['max_users']
        )
        
        # 初始化日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 初始化餐厅类型
        self.restaurant_type = np.random.choice(
            list(RESTAURANT_TYPE_CONFIG['type_distribution'].keys()),
            p=list(RESTAURANT_TYPE_CONFIG['type_distribution'].values())
        )
        
        # 初始化价格等级
        self.price_level = np.random.choice(
            ['low', 'medium', 'high'],
            p=[0.4, 0.4, 0.2]
        )
        
        # 获取营业时间
        self.business_hours = BUSINESS_HOURS_CONFIG[self.restaurant_type]
        
        # 获取用餐时长配置
        self.dining_duration = DINING_DURATION_CONFIG[self.restaurant_type]
        
        # 数据质量控制参数
        self.quality_metrics = {
            'missing_rate': 0.03,  # 缺失值比例
            'anomaly_rate': 0.05,  # 异常值比例
            'data_validation_rules': {
                'min_order_amount': 20,   # 最小订单金额
                'max_order_amount': 2000, # 最大订单金额
                'max_table_time': 180     # 最大餐桌占用时间（分钟）
            }
        }
        
    def generate_customer_base(self) -> pd.DataFrame:
        """生成顾客基础信息表
        
        生成规则：
        1. 顾客ID全局唯一
        2. 首次光顾时间在指定范围内随机分布
        3. 顾客属性符合预设的分布概率
        4. 会员用户占比控制在15%左右
        
        Returns:
            pd.DataFrame: 顾客基础信息数据框
        """
        self.logger.info(f"开始生成{self.customer_count}个顾客的基础信息...")
        
        customers = []
        for _ in range(self.customer_count):
            first_visit = self.faker.date_time_between(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # 按配置的分布随机选择顾客属性
            age_group = np.random.choice(
                USER_ATTRIBUTES['age_groups'],
                p=USER_ATTRIBUTES['age_distribution']
            )
            gender = np.random.choice(
                list(USER_ATTRIBUTES['gender_distribution'].keys()),
                p=list(USER_ATTRIBUTES['gender_distribution'].values())
            )
            city_tier = np.random.choice(
                USER_ATTRIBUTES['city_tiers'],
                p=list(USER_ATTRIBUTES['city_distribution'].values())
            )
            
            # 会员判定：结合首次光顾时间和消费频率
            is_member = (
                (self.end_date - first_visit).days > 90 and 
                np.random.random() < 0.3
            )
            
            # 用餐偏好
            preferences = self._generate_customer_preferences()
            
            customer = {
                'customer_id': f'c_{uuid.uuid4().hex[:8]}',
                'first_visit': first_visit,
                'customer_type': 'member' if is_member else 'regular',
                'age_group': age_group,
                'gender': gender,
                'city_tier': city_tier,
                'spicy_preference': preferences['spicy_food'],
                'is_vegetarian': preferences['vegetarian'],
                'seafood_preference': preferences['seafood'],
                'alcohol_preference': preferences['alcohol'],
                'lifetime_value': 0.0  # 初始化顾客终身价值
            }
            customers.append(customer)
        
        df = pd.DataFrame(customers)
        
        # 数据质量检查
        self._validate_customer_data(df)
        
        self.logger.info(f"顾客基础信息生成完成，共{len(df)}条记录")
        return df
    
    def generate_dine_in_orders(self, customer_df: pd.DataFrame) -> pd.DataFrame:
        """生成堂食订单数据
        
        生成规则：
        1. 考虑餐位容量和周转率
        2. 实现高峰期特征
        3. 模拟不同规模的用餐群体
        4. 计算并更新顾客终身价值
        
        Args:
            customer_df (pd.DataFrame): 顾客基础信息表
            
        Returns:
            pd.DataFrame: 堂食订单数据框
        """
        self.logger.info("开始生成堂食订单数据...")
        
        orders = []
        customer_visit_history = {}  # 记录顾客就餐历史
        
        # 遍历每一天
        current_date = self.start_date
        while current_date <= self.end_date:
            # 判断是否为工作日
            is_weekday = current_date.weekday() < 5
            
            # 获取营业时间
            operation_hours = self._get_business_hours(current_date)
            
            # 生成当天的订单
            daily_orders = self._generate_daily_dine_in_orders(
                current_date,
                customer_df,
                is_weekday
            )
            orders.extend(daily_orders)
            
            # 更新日期
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(orders)
        
        # 数据质量检查
        self._validate_dine_in_order_data(df)
        
        # 更新顾客终身价值
        self._update_customer_lifetime_value(customer_df, df)
        
        self.logger.info(f"堂食订单数据生成完成，共{len(df)}条记录")
        return df
    
    def generate_delivery_orders(self, customer_df: pd.DataFrame) -> pd.DataFrame:
        """生成外卖订单数据"""
        self.logger.info("开始生成外卖订单数据...")
        
        orders = []
        # 只有部分顾客会使用外卖
        delivery_customers = customer_df.sample(
            n=int(len(customer_df) * 0.6)  # 假设60%的顾客会使用外卖
        )
        
        for _, customer in delivery_customers.iterrows():
            # 根据用户属性确定下单频率
            base_frequency = 8 if customer['customer_type'] == 'member' else 4
            city_multiplier = 1.2 if customer['city_tier'] in ['一线城市', '二线城市'] else 1.0
            age_multiplier = 1.3 if customer['age_group'] in ['25-34', '35-44'] else 1.0
            
            order_frequency = int(base_frequency * city_multiplier * age_multiplier)
            
            # 生成该顾客的所有外卖订单
            customer_orders = self._generate_customer_delivery_orders(
                customer,
                order_frequency
            )
            orders.extend(customer_orders)
        
        df = pd.DataFrame(orders)
        
        # 数据质量检查
        self._validate_delivery_order_data(df)
        
        self.logger.info(f"外卖订单数据生成完成，共{len(df)}条记录")
        return df
    
    def generate_service_quality(
        self,
        dine_in_df: pd.DataFrame,
        delivery_df: pd.DataFrame
    ) -> pd.DataFrame:
        """生成服务质量数据
        
        生成规则：
        1. 记录等待时间
        2. 统计投诉情况
        3. 跟踪退菜记录
        4. 分析服务满意度
        
        Args:
            dine_in_df (pd.DataFrame): 堂食订单数据
            delivery_df (pd.DataFrame): 外卖订单数据
            
        Returns:
            pd.DataFrame: 服务质量数据框
        """
        self.logger.info("开始生成服务质量数据...")
        
        quality_records = []
        
        # 处理堂食订单的服务质量记录
        for _, order in dine_in_df.iterrows():
            record = self._generate_dine_in_quality_record(order)
            quality_records.append(record)
            
        # 处理外卖订单的服务质量记录
        for _, order in delivery_df.iterrows():
            record = self._generate_delivery_quality_record(order)
            quality_records.append(record)
        
        df = pd.DataFrame(quality_records)
        
        # 数据质量检查
        self._validate_service_quality_data(df)
        
        self.logger.info(f"服务质量数据生成完成，共{len(df)}条记录")
        return df
    
    def _generate_customer_preferences(self) -> Dict[str, bool]:
        """生成顾客偏好"""
        preferences = {
            'spicy_food': np.random.random() < 0.6,
            'vegetarian': np.random.random() < 0.1,
            'seafood': np.random.random() < 0.7,
            'alcohol': np.random.random() < 0.3
        }
        return preferences
    
    def _get_business_hours(self, date: datetime) -> Dict[str, str]:
        """获取指定日期的营业时间"""
        if self.restaurant_type == 'fast_food':
            return self.business_hours['all_day']
        else:
            return {
                'lunch': self.business_hours['lunch'],
                'dinner': self.business_hours['dinner']
            }
    
    def _generate_daily_dine_in_orders(
        self,
        date: datetime,
        customer_df: pd.DataFrame,
        is_weekday: bool
    ) -> List[dict]:
        """生成一天的堂食订单数据"""
        orders = []
        
        # 基础客流量（根据餐厅类型和价格等级调整）
        base_traffic = 100 if is_weekday else 150
        base_traffic *= RESTAURANT_TYPE_CONFIG['type_distribution'][self.restaurant_type]
        
        # 根据餐厅类型获取营业时段
        if self.restaurant_type == 'fast_food':
            # 快餐店全天营业
            all_day = self.business_hours['all_day']
            orders.extend(self._generate_all_day_orders(
                date,
                customer_df,
                all_day,
                base_traffic
            ))
        else:
            # 其他类型餐厅分午餐和晚餐时段
            for meal_time in ['lunch', 'dinner']:
                time_slot = self.business_hours[meal_time]
                # 午餐和晚餐的客流量分布
                traffic_multiplier = 1.2 if meal_time == 'dinner' else 1.0
                peak_traffic = int(base_traffic * traffic_multiplier)
                
                orders.extend(self._generate_meal_time_orders(
                    date,
                    customer_df,
                    time_slot,
                    peak_traffic,
                    meal_time
                ))
        
        return orders
        
    def _generate_all_day_orders(
        self,
        date: datetime,
        customer_df: pd.DataFrame,
        time_slot: dict,
        base_traffic: int
    ) -> List[dict]:
        """生成全天营业的订单数据"""
        orders = []
        start_time = datetime.strptime(time_slot['start'], '%H:%M').time()
        end_time = datetime.strptime(time_slot['end'], '%H:%M').time()
        
        # 按小时生成订单
        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        while current_time < end_datetime:
            # 获取当前小时的流量系数
            hour = current_time.hour
            hour_multiplier = self._get_hour_multiplier(hour)
            
            # 计算当前小时的订单数
            hour_orders = int(base_traffic * hour_multiplier / 12)  # 将基础流量平均分配到营业时间
            
            # 生成订单
            for _ in range(hour_orders):
                order = self._generate_single_order(
                    customer_df,
                    current_time
                )
                if order:
                    orders.append(order)
            
            current_time += timedelta(hours=1)
        
        return orders
        
    def _generate_meal_time_orders(
        self,
        date: datetime,
        customer_df: pd.DataFrame,
        time_slot: dict,
        peak_traffic: int,
        meal_time: str
    ) -> List[dict]:
        """生成午餐或晚餐时段的订单数据"""
        orders = []
        start_time = datetime.strptime(time_slot['start'], '%H:%M').time()
        end_time = datetime.strptime(time_slot['end'], '%H:%M').time()
        
        # 计算高峰期和非高峰期
        duration = datetime.combine(date, end_time) - datetime.combine(date, start_time)
        peak_start = datetime.combine(date, start_time) + duration / 4  # 高峰期从开始后1/4时间开始
        peak_end = datetime.combine(date, start_time) + duration * 3/4   # 高峰期到结束前1/4时间结束
        
        # 按30分钟为单位生成订单
        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        while current_time < end_datetime:
            # 判断是否在高峰期
            is_peak = peak_start <= current_time <= peak_end
            
            # 根据时段调整流量
            if is_peak:
                traffic = int(peak_traffic * 1.5)  # 高峰期流量提升50%
            else:
                traffic = int(peak_traffic * 0.7)  # 非高峰期流量降低30%
            
            # 生成30分钟的订单
            half_hour_orders = int(traffic / ((duration.seconds/3600) * 2))  # 将流量平均分配到每半小时
            
            for _ in range(half_hour_orders):
                order = self._generate_single_order(
                    customer_df,
                    current_time
                )
                if order:
                    orders.append(order)
            
            current_time += timedelta(minutes=30)
        
        return orders
        
    def _get_hour_multiplier(self, hour: int) -> float:
        """获取不同时段的流量系数"""
        if 11 <= hour <= 13:  # 午餐高峰
            return 1.5
        elif 17 <= hour <= 20:  # 晚餐高峰
            return 1.8
        elif 14 <= hour <= 16:  # 下午茶时段
            return 0.8
        elif 21 <= hour <= 22:  # 夜宵早期
            return 1.2
        elif 23 <= hour or hour <= 6:  # 深夜和凌晨
            return 0.3
        else:  # 其他时段
            return 1.0
    
    def _generate_customer_delivery_orders(
        self,
        customer: pd.Series,
        frequency: int
    ) -> List[dict]:
        """生成单个顾客的外卖订单"""
        orders = []
        
        for _ in range(frequency):
            # 生成订单时间
            order_time = self.faker.date_time_between(
                start_date=max(self.start_date, customer['first_visit']),
                end_date=self.end_date
            )
            
            # 计算订单金额
            price_range = RESTAURANT_TYPE_CONFIG['price_level'][self.restaurant_type][self.price_level]
            base_amount = np.random.uniform(
                price_range['min'],
                price_range['max']
            )
            
            # 外卖订单通常是1-2人份
            items_count = np.random.choice([1, 2], p=[0.7, 0.3])
            total_amount = base_amount * items_count
            
            # 考虑会员折扣
            if customer['customer_type'] == 'member':
                total_amount *= 0.9  # 会员9折
            
            # 添加配送费
            delivery_fee = DELIVERY_CONFIG['delivery_fee']['base_fee']
            # 随机配送距离
            distance = np.random.uniform(0.5, 5.0)
            delivery_fee += DELIVERY_CONFIG['delivery_fee']['distance_fee'] * distance
            
            # 选择配送平台
            platform = np.random.choice(
                list(DELIVERY_CONFIG['platforms'].keys()),
                p=list(DELIVERY_CONFIG['platforms'].values())
            )
            
            # 计算平台抽成
            commission = total_amount * DELIVERY_CONFIG['commission_rate'][platform]
            
            # 选择支付方式（外卖都是在线支付）
            payment_method = np.random.choice(
                list(PAYMENT_METHODS['online'].keys()),
                p=list(PAYMENT_METHODS['online'].values())
            )
            
            # 计算配送时间
            delivery_time = np.random.randint(
                DELIVERY_CONFIG['delivery_time']['normal']['min'],
                DELIVERY_CONFIG['delivery_time']['normal']['max']
            )
            
            order = {
                'order_id': f'd_{uuid.uuid4().hex[:8]}',
                'customer_id': customer['customer_id'],
                'restaurant_type': self.restaurant_type,
                'price_level': self.price_level,
                'order_time': order_time,
                'items_count': items_count,
                'total_amount': round(total_amount, 2),
                'delivery_fee': round(delivery_fee, 2),
                'platform': platform,
                'commission': round(commission, 2),
                'payment_method': payment_method,
                'delivery_time': delivery_time,
                'delivery_distance': round(distance, 1),
                'is_member': customer['customer_type'] == 'member'
            }
            
            orders.append(order)
        
        return orders
    
    def _generate_single_order(
        self,
        customer_df: pd.DataFrame,
        order_time: datetime
    ) -> Optional[dict]:
        """生成单个订单数据"""
        # 随机选择一个顾客
        customer = customer_df.sample(n=1).iloc[0]
        
        # 确定就餐人数
        party_size = np.random.choice(
            [1, 2, 3, 4, 5, 6, 7, 8],
            p=[0.1, 0.3, 0.25, 0.15, 0.1, 0.05, 0.03, 0.02]
        )
        
        # 计算用餐时长（分钟）
        dining_duration = np.random.randint(
            self.dining_duration['min'],
            self.dining_duration['max']
        )
        
        # 计算订单金额
        price_range = RESTAURANT_TYPE_CONFIG['price_level'][self.restaurant_type][self.price_level]
        per_person_amount = np.random.uniform(
            price_range['min'],
            price_range['max']
        )
        total_amount = per_person_amount * party_size
        
        # 考虑会员折扣
        if customer['customer_type'] == 'member':
            total_amount *= 0.9  # 会员9折
        
        # 选择支付方式
        payment_method = np.random.choice(
            list(PAYMENT_METHODS['offline'].keys()),
            p=list(PAYMENT_METHODS['offline'].values())
        )
        
        # 生成订单ID
        order_id = f'o_{uuid.uuid4().hex[:8]}'
        
        order = {
            'order_id': order_id,
            'customer_id': customer['customer_id'],
            'restaurant_type': self.restaurant_type,
            'price_level': self.price_level,
            'order_time': order_time,
            'party_size': party_size,
            'dining_duration': dining_duration,
            'total_amount': round(total_amount, 2),
            'payment_method': payment_method,
            'is_member': customer['customer_type'] == 'member'
        }
        
        return order
    
    def _generate_dine_in_quality_record(self, order: pd.Series) -> dict:
        """生成堂食订单的服务质量记录"""
        # 生成基础评分
        base_scores = {}
        for aspect, weight in SERVICE_QUALITY_CONFIG['rating_weights'].items():
            # 根据评分分布生成评分
            score = np.random.choice(
                list(SERVICE_QUALITY_CONFIG['rating_distribution'].keys()),
                p=list(SERVICE_QUALITY_CONFIG['rating_distribution'].values())
            )
            base_scores[aspect] = score
        
        # 计算总体评分（加权平均）
        overall_score = sum(
            score * weight
            for (aspect, score), (aspect_weight, weight)
            in zip(base_scores.items(), SERVICE_QUALITY_CONFIG['rating_weights'].items())
        )
        overall_score = round(overall_score)  # 四舍五入到整数
        
        # 确定是否有投诉
        has_complaint = overall_score <= 2
        complaint_info = None
        if has_complaint:
            # 随机选择投诉类型
            complaint_type = np.random.choice(
                list(SERVICE_QUALITY_CONFIG['complaint_types'].keys()),
                p=list(SERVICE_QUALITY_CONFIG['complaint_types'].values())
            )
            
            # 随机选择解决时间
            resolution = np.random.choice(
                list(SERVICE_QUALITY_CONFIG['resolution_time'].keys()),
                p=[item['probability'] for item in SERVICE_QUALITY_CONFIG['resolution_time'].values()]
            )
            resolution_time = SERVICE_QUALITY_CONFIG['resolution_time'][resolution]['time']
            
            complaint_info = {
                'type': complaint_type,
                'resolution_time': resolution_time,
                'status': 'resolved'
            }
        
        # 生成评价记录
        record = {
            'order_id': order['order_id'],
            'customer_id': order['customer_id'],
            'rating_time': order['order_time'] + timedelta(hours=2),  # 假设在用餐后2小时评价
            'overall_score': overall_score,
            'food_taste_score': base_scores['food_taste'],
            'service_attitude_score': base_scores['service_attitude'],
            'environment_score': base_scores['environment'],
            'price_performance_score': base_scores['price_performance'],
            'has_complaint': has_complaint
        }
        
        # 如果有投诉，添加投诉信息
        if complaint_info:
            record.update({
                'complaint_type': complaint_info['type'],
                'resolution_time': complaint_info['resolution_time'],
                'complaint_status': complaint_info['status']
            })
        
        return record
    
    def _generate_delivery_quality_record(self, order: pd.Series) -> dict:
        """生成外卖订单的服务质量记录"""
        # 生成基础评分
        base_scores = {}
        for aspect, weight in SERVICE_QUALITY_CONFIG['rating_weights'].items():
            # 根据评分分布生成评分
            score = np.random.choice(
                list(SERVICE_QUALITY_CONFIG['rating_distribution'].keys()),
                p=list(SERVICE_QUALITY_CONFIG['rating_distribution'].values())
            )
            base_scores[aspect] = score
        
        # 计算总体评分（加权平均）
        overall_score = sum(
            score * weight
            for (aspect, score), (aspect_weight, weight)
            in zip(base_scores.items(), SERVICE_QUALITY_CONFIG['rating_weights'].items())
        )
        overall_score = round(overall_score)  # 四舍五入到整数
        
        # 确定是否有投诉
        has_complaint = overall_score <= 2
        complaint_info = None
        if has_complaint:
            # 随机选择投诉类型
            complaint_type = np.random.choice(
                list(SERVICE_QUALITY_CONFIG['complaint_types'].keys()),
                p=list(SERVICE_QUALITY_CONFIG['complaint_types'].values())
            )
            
            # 随机选择解决时间
            resolution = np.random.choice(
                list(SERVICE_QUALITY_CONFIG['resolution_time'].keys()),
                p=[item['probability'] for item in SERVICE_QUALITY_CONFIG['resolution_time'].values()]
            )
            resolution_time = SERVICE_QUALITY_CONFIG['resolution_time'][resolution]['time']
            
            complaint_info = {
                'type': complaint_type,
                'resolution_time': resolution_time,
                'status': 'resolved'
            }
        
        # 生成评价记录
        record = {
            'order_id': order['order_id'],
            'customer_id': order['customer_id'],
            'rating_time': order['order_time'] + timedelta(minutes=order['delivery_time'] + 30),  # 假设在送达后30分钟评价
            'overall_score': overall_score,
            'food_taste_score': base_scores['food_taste'],
            'service_attitude_score': base_scores['service_attitude'],
            'delivery_speed_score': base_scores['environment'],  # 用环境分数替代配送速度分数
            'price_performance_score': base_scores['price_performance'],
            'has_complaint': has_complaint,
            'delivery_time': order['delivery_time'],
            'delivery_distance': order['delivery_distance'],
            'platform': order['platform']
        }
        
        # 如果有投诉，添加投诉信息
        if complaint_info:
            record.update({
                'complaint_type': complaint_info['type'],
                'resolution_time': complaint_info['resolution_time'],
                'complaint_status': complaint_info['status']
            })
        
        return record
    
    def _validate_customer_data(self, df: pd.DataFrame) -> None:
        """验证顾客数据的有效性"""
        # 检查必填字段
        required_fields = [
            'customer_id', 'first_visit', 'customer_type',
            'age_group', 'gender', 'city_tier'
        ]
        for field in required_fields:
            if field not in df.columns:
                self.logger.warning(f"缺少必填字段: {field}")
        
        # 检查ID唯一性
        if df['customer_id'].duplicated().any():
            self.logger.warning("发现重复的顾客ID")
        
        # 验证时间范围
        if df['first_visit'].min() < self.start_date or df['first_visit'].max() > self.end_date:
            self.logger.warning("发现超出范围的首次光顾时间")
        
        # 验证顾客类型
        invalid_types = df[~df['customer_type'].isin(['member', 'regular'])]
        if not invalid_types.empty:
            self.logger.warning(f"发现{len(invalid_types)}个无效的顾客类型")
        
        # 验证年龄组
        invalid_ages = df[~df['age_group'].isin(USER_ATTRIBUTES['age_groups'])]
        if not invalid_ages.empty:
            self.logger.warning(f"发现{len(invalid_ages)}个无效的年龄组")
        
        # 验证性别
        invalid_genders = df[~df['gender'].isin(USER_ATTRIBUTES['gender_distribution'].keys())]
        if not invalid_genders.empty:
            self.logger.warning(f"发现{len(invalid_genders)}个无效的性别")
        
        # 验证城市等级
        invalid_cities = df[~df['city_tier'].isin(USER_ATTRIBUTES['city_tiers'])]
        if not invalid_cities.empty:
            self.logger.warning(f"发现{len(invalid_cities)}个无效的城市等级")
    
    def _validate_dine_in_order_data(self, df: pd.DataFrame) -> None:
        """验证堂食订单数据质量
        
        Args:
            df (pd.DataFrame): 订单数据框
        """
        # 检查订单ID唯一性
        if df['order_id'].duplicated().any():
            self.logger.warning("发现重复的订单ID")
            
        # 检查订单金额范围
        amount_min = self.quality_metrics['data_validation_rules']['min_order_amount']
        amount_max = self.quality_metrics['data_validation_rules']['max_order_amount']
        invalid_amounts = df[
            (df['total_amount'] < amount_min) | (df['total_amount'] > amount_max)
        ]
        if len(invalid_amounts) > 0:
            self.logger.warning(f"发现{len(invalid_amounts)}笔订单金额超出有效范围")
            
        # 检查就餐时间合理性
        if (df['dining_duration'] > self.quality_metrics['data_validation_rules']['max_table_time']).any():
            self.logger.warning("发现异常的就餐时长")
    
    def _validate_delivery_order_data(self, df: pd.DataFrame) -> None:
        """验证外卖订单数据的有效性"""
        # 检查必填字段
        required_fields = [
            'order_id', 'customer_id', 'order_time',
            'total_amount', 'delivery_fee', 'platform'
        ]
        for field in required_fields:
            if field not in df.columns:
                self.logger.warning(f"缺少必填字段: {field}")
        
        # 检查ID唯一性
        if df['order_id'].duplicated().any():
            self.logger.warning("发现重复的订单ID")
        
        # 验证时间范围
        if df['order_time'].min() < self.start_date or df['order_time'].max() > self.end_date:
            self.logger.warning("发现超出范围的订单时间")
        
        # 验证金额范围
        invalid_amounts = df[
            (df['total_amount'] < 20) |  # 最小订单金额
            (df['total_amount'] > 1000)   # 最大订单金额
        ]
        if not invalid_amounts.empty:
            self.logger.warning(f"发现{len(invalid_amounts)}笔订单金额超出有效范围")
        
        # 验证配送费范围
        invalid_fees = df[
            (df['delivery_fee'] < DELIVERY_CONFIG['delivery_fee']['base_fee']) |
            (df['delivery_fee'] > 50)  # 最大配送费
        ]
        if not invalid_fees.empty:
            self.logger.warning(f"发现{len(invalid_fees)}笔配送费超出有效范围")
        
        # 验证配送平台
        invalid_platforms = df[~df['platform'].isin(DELIVERY_CONFIG['platforms'].keys())]
        if not invalid_platforms.empty:
            self.logger.warning(f"发现{len(invalid_platforms)}个无效的配送平台")
    
    def _validate_service_quality_data(self, df: pd.DataFrame) -> None:
        """验证服务质量数据的有效性"""
        # 检查必填字段
        required_fields = [
            'order_id', 'customer_id', 'rating_time',
            'overall_score', 'has_complaint'
        ]
        for field in required_fields:
            if field not in df.columns:
                self.logger.warning(f"缺少必填字段: {field}")
        
        # 检查订单ID唯一性
        if df['order_id'].duplicated().any():
            self.logger.warning("发现重复的订单ID")
        
        # 验证评分范围
        score_fields = [
            'overall_score', 'food_taste_score',
            'service_attitude_score', 'price_performance_score'
        ]
        for field in score_fields:
            if field in df.columns:
                invalid_scores = df[
                    (df[field] < 1) |
                    (df[field] > 5)
                ]
                if not invalid_scores.empty:
                    self.logger.warning(f"发现{len(invalid_scores)}个无效的{field}")
        
        # 验证时间范围
        if df['rating_time'].min() < self.start_date or df['rating_time'].max() > self.end_date:
            self.logger.warning("发现超出范围的评价时间")
        
        # 验证投诉类型
        complaint_records = df[df['has_complaint']]
        if not complaint_records.empty:
            invalid_types = complaint_records[
                ~complaint_records['complaint_type'].isin(
                    SERVICE_QUALITY_CONFIG['complaint_types'].keys()
                )
            ]
            if not invalid_types.empty:
                self.logger.warning(f"发现{len(invalid_types)}个无效的投诉类型")
    
    def _update_customer_lifetime_value(
        self,
        customer_df: pd.DataFrame,
        order_df: pd.DataFrame
    ) -> None:
        """更新顾客终身价值
        
        Args:
            customer_df (pd.DataFrame): 顾客数据框
            order_df (pd.DataFrame): 订单数据框
        """
        # 计算每个顾客的总消费金额
        customer_total = order_df.groupby('customer_id')['total_amount'].sum()
        
        # 更新顾客终身价值
        for customer_id, total_amount in customer_total.items():
            customer_type = customer_df.loc[
                customer_df['customer_id'] == customer_id,
                'customer_type'
            ].iloc[0]
            multiplier = 1.1 if customer_type == 'member' else 1.0
            customer_df.loc[
                customer_df['customer_id'] == customer_id,
                'lifetime_value'
            ] = total_amount * multiplier
    
    def generate_all_data(self) -> Dict[str, pd.DataFrame]:
        """生成所有数据表
        
        Returns:
            Dict[str, pd.DataFrame]: 包含所有数据表的字典
        """
        self.logger.info("开始生成全部数据...")
        
        # 生成顾客基础信息
        customer_df = self.generate_customer_base()
        
        # 生成堂食订单数据
        dine_in_df = self.generate_dine_in_orders(customer_df)
        
        # 生成外卖订单数据
        delivery_df = self.generate_delivery_orders(customer_df)
        
        # 生成服务质量数据
        quality_df = self.generate_service_quality(dine_in_df, delivery_df)
        
        self.logger.info("所有数据生成完成")
        
        return {
            'customer_base': customer_df,
            'dine_in_orders': dine_in_df,
            'delivery_orders': delivery_df,
            'service_quality': quality_df
        } 