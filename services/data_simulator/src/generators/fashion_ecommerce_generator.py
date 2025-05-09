"""
服饰电商数据生成器
负责生成服饰电商的模拟数据，包括用户信息、交易数据、行为日志和NPS数据
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
    PAYMENT_METHODS,
    NPS_CONFIG
)
from config.fashion_ecommerce_config import (
    CATEGORY_CONFIG,
    RETURN_CONFIG,
    USER_BEHAVIOR_CONFIG,
    PROMOTION_CONFIG,
    CONVERSION_CONFIG
)

class FashionEcommerceGenerator:
    """服饰电商数据生成器类
    
    负责生成完整的服饰电商模拟数据集，包括：
    1. 用户基础信息
    2. 交易流水
    3. 用户行为日志
    4. NPS调研数据
    
    主要特点：
    - 保持数据业务逻辑的合理性
    - 模拟真实的用户行为路径
    - 考虑季节性和促销活动的影响
    - 实现数据质量控制
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
        
        # 初始化用户数量
        self.user_count = np.random.randint(
            VOLUME_CONFIG['min_users'],
            VOLUME_CONFIG['max_users']
        )
        
        # 初始化日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 数据质量控制参数
        self.quality_metrics = {
            'missing_rate': 0.03,  # 缺失值比例
            'anomaly_rate': 0.05,  # 异常值比例
            'data_validation_rules': {
                'amount_min': 50,   # 最小交易金额
                'amount_max': 5000, # 最大交易金额
                'max_purchases_per_day': 5  # 每用户每日最大购买次数
            }
        }
        
    def generate_user_base(self) -> pd.DataFrame:
        """生成用户基础信息表
        
        生成规则：
        1. 用户ID全局唯一
        2. 注册时间在指定范围内随机分布
        3. 用户属性符合预设的分布概率
        4. VIP用户占比控制在20%左右
        
        Returns:
            pd.DataFrame: 用户基础信息数据框
        """
        self.logger.info(f"开始生成{self.user_count}个用户的基础信息...")
        
        users = []
        for _ in range(self.user_count):
            register_time = self.faker.date_time_between(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # 按配置的分布随机选择用户属性
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
                p=USER_ATTRIBUTES['city_distribution']
            )
            
            # VIP用户判定：结合城市等级和注册时间
            is_vip = (city_tier in ['T1', 'T2'] and np.random.random() < 0.3) or \
                     (city_tier in ['T3', 'T4'] and np.random.random() < 0.1)
            
            user = {
                'user_id': f'u_{uuid.uuid4().hex[:8]}',
                'register_time': register_time,
                'user_type': 'vip' if is_vip else 'normal',
                'age_group': age_group,
                'gender': gender,
                'city_tier': city_tier,
                'lifetime_value': 0.0  # 初始化客户终身价值
            }
            users.append(user)
        
        df = pd.DataFrame(users)
        
        # 数据质量检查
        self._validate_user_data(df)
        
        self.logger.info(f"用户基础信息生成完成，共{len(df)}条记录")
        return df
    
    def generate_transactions(self, user_df: pd.DataFrame) -> pd.DataFrame:
        """生成交易流水数据
        
        生成规则：
        1. 考虑用户属性影响购买频率和金额
        2. 实现季节性和促销期的影响
        3. 模拟商品类别和子类别的选择
        4. 计算并更新客户终身价值
        
        Args:
            user_df (pd.DataFrame): 用户基础信息表
            
        Returns:
            pd.DataFrame: 交易流水数据框
        """
        self.logger.info("开始生成交易流水数据...")
        
        transactions = []
        user_purchase_history = {}  # 记录用户购买历史
        
        for _, user in user_df.iterrows():
            # 根据用户属性确定购买频率
            base_frequency = 12 if user['user_type'] == 'vip' else 6
            city_multiplier = 1.2 if user['city_tier'] in ['T1', 'T2'] else 1.0
            age_multiplier = 1.3 if user['age_group'] in ['25-34', '35-44'] else 1.0
            
            purchase_frequency = int(base_frequency * city_multiplier * age_multiplier)
            
            # 生成该用户的所有购买记录
            user_transactions = []
            for _ in range(purchase_frequency):
                transaction = self._generate_single_transaction(user)
                user_transactions.append(transaction)
            
            # 检查并调整同一天的购买次数
            adjusted_transactions = self._adjust_daily_purchases(user_transactions)
            transactions.extend(adjusted_transactions)
            
            # 更新用户购买历史
            user_purchase_history[user['user_id']] = adjusted_transactions
        
        df = pd.DataFrame(transactions)
        
        # 数据质量检查
        self._validate_transaction_data(df)
        
        # 更新用户终身价值
        self._update_user_lifetime_value(user_df, df)
        
        self.logger.info(f"交易流水数据生成完成，共{len(df)}条记录")
        return df
    
    def _generate_single_transaction(self, user: pd.Series) -> dict:
        """生成单条交易记录
        
        Args:
            user (pd.Series): 用户信息
            
        Returns:
            dict: 交易记录字典
        """
        # 确定购买时间
        transaction_time = self.faker.date_time_between(
            start_date=user['register_time'],
            end_date=self.end_date
        )
        
        # 选择商品类别和子类别
        category = np.random.choice(
            list(CATEGORY_CONFIG['category_distribution'].keys()),
            p=list(CATEGORY_CONFIG['category_distribution'].values())
        )
        subcategory = np.random.choice(
            CATEGORY_CONFIG['categories'][category]['subcategories']
        )
        
        # 确定商品价格
        price_range = CATEGORY_CONFIG['categories'][category]['price_ranges'][subcategory]
        base_amount = np.random.uniform(price_range['min'], price_range['max'])
        
        # 应用各种价格调整因素
        amount = self._adjust_price(
            base_amount,
            user,
            transaction_time,
            category
        )
        
        # 确定购买数量
        quantity = self._determine_quantity(amount, user['user_type'])
        
        # 计算是否退货
        is_refunded = self._determine_refund(
            amount,
            category,
            user['user_type']
        )
        
        return {
            'transaction_id': f't_{uuid.uuid4().hex[:8]}',
            'user_id': user['user_id'],
            'transaction_time': transaction_time,
            'amount': round(amount, 2),
            'payment_method': self._select_payment_method(amount),
            'category': category,
            'subcategory': subcategory,
            'quantity': quantity,
            'is_refunded': is_refunded
        }
    
    def _adjust_price(
        self,
        base_amount: float,
        user: pd.Series,
        transaction_time: datetime,
        category: str
    ) -> float:
        """调整商品价格
        
        考虑因素：
        1. 季节性影响
        2. 促销活动
        3. 用户类型
        4. 商品类别
        
        Args:
            base_amount (float): 基础价格
            user (pd.Series): 用户信息
            transaction_time (datetime): 交易时间
            category (str): 商品类别
            
        Returns:
            float: 调整后的价格
        """
        amount = base_amount
        
        # 季节性调整
        season = self._get_season(transaction_time)
        season_multiplier = CATEGORY_CONFIG['categories'][category]['season_multiplier'][season]
        amount *= season_multiplier
        
        # 促销期调整
        if self._is_promotion_period(transaction_time):
            discount = np.random.uniform(
                PROMOTION_CONFIG['min_discount'],
                PROMOTION_CONFIG['max_discount']
            )
            amount *= discount
        
        # VIP用户折扣
        if user['user_type'] == 'vip':
            amount *= 0.95
        
        # 确保价格在合理范围内
        amount = max(
            self.quality_metrics['data_validation_rules']['amount_min'],
            min(amount, self.quality_metrics['data_validation_rules']['amount_max'])
        )
        
        return amount
    
    def _determine_quantity(self, amount: float, user_type: str) -> int:
        """确定购买数量
        
        规则：
        1. 金额越大，数量倾向越少
        2. VIP用户更可能购买多件
        
        Args:
            amount (float): 商品金额
            user_type (str): 用户类型
            
        Returns:
            int: 购买数量
        """
        if amount > 1000:
            max_quantity = 2
        elif amount > 500:
            max_quantity = 3
        else:
            max_quantity = 4
            
        if user_type == 'vip':
            max_quantity += 1
            
        return np.random.randint(1, max_quantity + 1)
    
    def _determine_refund(
        self,
        amount: float,
        category: str,
        user_type: str
    ) -> bool:
        """确定是否退货
        
        考虑因素：
        1. 商品金额（金额越大退货概率越高）
        2. 商品类别（不同品类退货率不同）
        3. 用户类型（VIP用户退货率较低）
        
        Args:
            amount (float): 商品金额
            category (str): 商品类别
            user_type (str): 用户类型
            
        Returns:
            bool: 是否退货
        """
        base_rate = RETURN_CONFIG['base_return_rate']
        
        # 金额影响
        amount_factor = min(amount / 1000, 2.0)
        
        # 品类影响
        category_factor = RETURN_CONFIG['category_factors'].get(category, 1.0)
        
        # 用户类型影响
        user_factor = 0.8 if user_type == 'vip' else 1.0
        
        final_rate = base_rate * amount_factor * category_factor * user_factor
        
        return np.random.random() < final_rate
    
    def _select_payment_method(self, amount: float) -> str:
        """选择支付方式
        
        规则：
        1. 大额订单更倾向于信用卡支付
        2. 小额订单更倾向于移动支付
        
        Args:
            amount (float): 交易金额
            
        Returns:
            str: 支付方式
        """
        if amount > 2000:
            methods = ['credit_card', 'wechat', 'alipay']
            weights = [0.5, 0.25, 0.25]
        elif amount > 1000:
            methods = ['credit_card', 'wechat', 'alipay']
            weights = [0.3, 0.35, 0.35]
        else:
            methods = ['wechat', 'alipay', 'credit_card', 'debit_card']
            weights = [0.4, 0.4, 0.15, 0.05]
            
        return np.random.choice(methods, p=weights)
    
    def _adjust_daily_purchases(
        self,
        transactions: List[dict]
    ) -> List[dict]:
        """调整用户每日购买次数
        
        确保同一用户每天的购买次数不超过设定的最大值
        
        Args:
            transactions (List[dict]): 交易记录列表
            
        Returns:
            List[dict]: 调整后的交易记录列表
        """
        # 按日期分组
        daily_transactions = {}
        for trans in transactions:
            date = trans['transaction_time'].date()
            if date not in daily_transactions:
                daily_transactions[date] = []
            daily_transactions[date].append(trans)
        
        # 调整每日购买次数
        adjusted_transactions = []
        max_daily = self.quality_metrics['data_validation_rules']['max_purchases_per_day']
        
        for date, trans_list in daily_transactions.items():
            if len(trans_list) > max_daily:
                # 随机选择指定数量的交易保留
                selected_trans = np.random.choice(
                    trans_list,
                    size=max_daily,
                    replace=False
                )
                adjusted_transactions.extend(selected_trans)
            else:
                adjusted_transactions.extend(trans_list)
        
        return adjusted_transactions
    
    def _update_user_lifetime_value(
        self,
        user_df: pd.DataFrame,
        transaction_df: pd.DataFrame
    ) -> None:
        """更新用户终身价值
        
        计算规则：
        1. 累计所有未退货订单金额
        2. VIP用户额外增加10%权重
        
        Args:
            user_df (pd.DataFrame): 用户数据框
            transaction_df (pd.DataFrame): 交易数据框
        """
        # 计算每个用户的有效购买总额
        valid_transactions = transaction_df[~transaction_df['is_refunded']]
        user_total_amount = valid_transactions.groupby('user_id')['amount'].sum()
        
        # 更新用户终身价值
        for user_id, total_amount in user_total_amount.items():
            user_type = user_df.loc[user_df['user_id'] == user_id, 'user_type'].iloc[0]
            multiplier = 1.1 if user_type == 'vip' else 1.0
            user_df.loc[user_df['user_id'] == user_id, 'lifetime_value'] = total_amount * multiplier
    
    def _validate_user_data(self, df: pd.DataFrame) -> None:
        """验证用户数据质量
        
        检查项目：
        1. 用户ID唯一性
        2. 必填字段完整性
        3. 字段值有效性
        
        Args:
            df (pd.DataFrame): 用户数据框
        """
        # 检查用户ID唯一性
        if df['user_id'].duplicated().any():
            self.logger.warning("发现重复的用户ID")
            
        # 检查必填字段完整性
        required_fields = ['user_id', 'register_time', 'user_type', 'age_group', 'gender', 'city_tier']
        for field in required_fields:
            missing_rate = df[field].isnull().mean()
            if missing_rate > self.quality_metrics['missing_rate']:
                self.logger.warning(f"字段{field}的缺失率({missing_rate:.2%})超过阈值")
                
        # 检查字段值有效性
        if not df['user_type'].isin(['normal', 'vip']).all():
            self.logger.warning("发现无效的用户类型")
        if not df['city_tier'].isin(['T1', 'T2', 'T3', 'T4']).all():
            self.logger.warning("发现无效的城市等级")
    
    def _validate_transaction_data(self, df: pd.DataFrame) -> None:
        """验证交易数据质量
        
        检查项目：
        1. 交易ID唯一性
        2. 交易金额合理性
        3. 时间顺序正确性
        
        Args:
            df (pd.DataFrame): 交易数据框
        """
        # 检查交易ID唯一性
        if df['transaction_id'].duplicated().any():
            self.logger.warning("发现重复的交易ID")
            
        # 检查交易金额范围
        amount_min = self.quality_metrics['data_validation_rules']['amount_min']
        amount_max = self.quality_metrics['data_validation_rules']['amount_max']
        invalid_amounts = df[
            (df['amount'] < amount_min) | (df['amount'] > amount_max)
        ]
        if len(invalid_amounts) > 0:
            self.logger.warning(f"发现{len(invalid_amounts)}笔交易金额超出有效范围")
            
        # 检查交易时间顺序
        df_sorted = df.sort_values('transaction_time')
        if not df_sorted.equals(df):
            self.logger.warning("交易记录的时间顺序不正确")
    
    def _get_season(self, date: datetime) -> str:
        """根据日期判断季节
        
        Args:
            date (datetime): 日期
            
        Returns:
            str: 季节名称（spring/summer/autumn/winter）
        """
        month = date.month
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'
    
    def _is_promotion_period(self, date: datetime) -> bool:
        """判断是否为促销期
        
        促销期包括：
        1. 节假日
        2. 月末
        3. 季末
        4. 特殊促销日（如双11）
        
        Args:
            date (datetime): 日期
            
        Returns:
            bool: 是否为促销期
        """
        # 特殊促销日
        special_dates = {
            (11, 11),  # 双11
            (12, 12),  # 双12
            (6, 18),   # 618
        }
        
        # 判断是否为特殊促销日
        if (date.month, date.day) in special_dates:
            return True
            
        # 判断是否为月末（最后3天）
        if date.day >= 28:
            return True
            
        # 判断是否为季末
        if date.month in [3, 6, 9, 12] and date.day >= 25:
            return True
            
        return False
    
    def _generate_feedback_text(self, score: int) -> str:
        """根据NPS评分生成反馈文本
        
        Args:
            score (int): NPS评分（0-10）
            
        Returns:
            str: 反馈文本
        """
        if score >= 9:  # 推荐者
            templates = [
                "商品质量很好，款式新颖时尚，物流速度快",
                "客服服务态度很好，购物体验非常愉快",
                "价格实惠，质量可靠，会继续关注",
                "包装很精致，穿着舒适，很满意"
            ]
        elif score >= 7:  # 中立者
            templates = [
                "商品还可以，但是价格稍贵",
                "质量不错，但是发货有点慢",
                "款式还行，但是尺码不太准",
                "整体还行，但是退换货比较麻烦"
            ]
        else:  # 批评者
            templates = [
                "商品质量一般，不太值这个价",
                "发货太慢了，物流体验差",
                "客服态度不好，售后很困难",
                "尺码标注不准确，穿着不舒服"
            ]
            
        return np.random.choice(templates)
    
    def generate_user_behaviors(self, user_df: pd.DataFrame) -> pd.DataFrame:
        """生成用户行为日志
        
        生成规则：
        1. 模拟完整的用户行为路径
        2. 考虑设备偏好
        3. 实现合理的时间间隔
        4. 关联交易转化
        
        Args:
            user_df (pd.DataFrame): 用户基础信息表
            
        Returns:
            pd.DataFrame: 用户行为日志数据框
        """
        self.logger.info("开始生成用户行为日志...")
        
        behaviors = []
        
        for _, user in user_df.iterrows():
            # 根据用户类型和城市等级确定行为频率
            base_paths = np.random.randint(20, 50)
            if user['user_type'] == 'vip':
                base_paths = int(base_paths * 1.5)
            if user['city_tier'] in ['T1', 'T2']:
                base_paths = int(base_paths * 1.2)
                
            # 生成用户的所有行为路径
            user_behaviors = self._generate_user_behavior_paths(
                user,
                base_paths
            )
            behaviors.extend(user_behaviors)
        
        df = pd.DataFrame(behaviors)
        
        # 数据质量检查
        self._validate_behavior_data(df)
        
        self.logger.info(f"用户行为日志生成完成，共{len(df)}条记录")
        return df
        
    def _generate_user_behavior_paths(
        self,
        user: pd.Series,
        num_paths: int
    ) -> List[dict]:
        """生成用户行为路径
        
        Args:
            user (pd.Series): 用户信息
            num_paths (int): 行为路径数量
            
        Returns:
            List[dict]: 行为记录列表
        """
        behaviors = []
        
        for _ in range(num_paths):
            # 选择行为路径模式
            path_type = np.random.choice(
                list(USER_BEHAVIOR_CONFIG['path_patterns'].keys()),
                p=[p['probability'] for p in USER_BEHAVIOR_CONFIG['path_patterns'].values()]
            )
            path_steps = USER_BEHAVIOR_CONFIG['path_patterns'][path_type]['steps']
            
            # 确定设备类型（用户倾向于使用同一设备）
            device_preference = np.random.random()
            if device_preference < 0.7:  # 70%用户主要使用移动端
                primary_device = 'mobile'
                device_switch_prob = 0.1
            else:
                primary_device = 'pc'
                device_switch_prob = 0.2
            
            # 生成行为时间（在用户注册时间之后）
            base_time = self.faker.date_time_between(
                start_date=user['register_time'],
                end_date=self.end_date
            )
            
            # 生成每一步的行为记录
            current_time = base_time
            for step in path_steps:
                # 确定本次行为的设备类型
                if np.random.random() < device_switch_prob:
                    device_type = 'pc' if primary_device == 'mobile' else 'mobile'
                else:
                    device_type = primary_device
                
                # 确定停留时间
                duration_config = USER_BEHAVIOR_CONFIG['step_duration'][step]
                base_duration = np.random.randint(
                    duration_config['min'],
                    duration_config['max']
                )
                
                # 根据设备类型调整停留时间
                if device_type == 'pc':
                    stay_time = int(base_duration * 1.2)  # PC端停留时间较长
                else:
                    stay_time = base_duration
                
                # 创建行为记录
                behavior = {
                    'log_id': f'l_{uuid.uuid4().hex[:8]}',
                    'user_id': user['user_id'],
                    'behavior_time': current_time,
                    'behavior_type': step,
                    'stay_time': stay_time,
                    'device_type': device_type,
                    'path_type': path_type
                }
                behaviors.append(behavior)
                
                # 更新时间（考虑用户思考时间）
                think_time = np.random.randint(5, 20)  # 5-20秒思考时间
                current_time += timedelta(seconds=stay_time + think_time)
        
        return behaviors
        
    def generate_nps_surveys(self, user_df: pd.DataFrame) -> pd.DataFrame:
        """生成NPS调研数据
        
        生成规则：
        1. 控制调研参与率
        2. 模拟不同满意度用户的评分分布
        3. 生成符合评分的反馈文本
        4. 实现多渠道调研
        
        Args:
            user_df (pd.DataFrame): 用户基础信息表
            
        Returns:
            pd.DataFrame: NPS调研数据框
        """
        self.logger.info("开始生成NPS调研数据...")
        
        surveys = []
        
        # 根据用户类型和城市等级调整参与率
        for _, user in user_df.iterrows():
            # 计算基础参与概率
            base_prob = 0.6  # 基础参与率60%
            
            # VIP用户更可能参与
            if user['user_type'] == 'vip':
                base_prob *= 1.2
            
            # 一二线城市用户参与度更高
            if user['city_tier'] in ['T1', 'T2']:
                base_prob *= 1.1
                
            # 决定是否参与调研
            if np.random.random() < base_prob:
                survey = self._generate_single_survey(user)
                surveys.append(survey)
        
        df = pd.DataFrame(surveys)
        
        # 数据质量检查
        self._validate_nps_data(df)
        
        self.logger.info(f"NPS调研数据生成完成，共{len(df)}条记录")
        return df
        
    def _generate_single_survey(self, user: pd.Series) -> dict:
        """生成单条NPS调研记录
        
        Args:
            user (pd.Series): 用户信息
            
        Returns:
            dict: 调研记录字典
        """
        # 根据用户类型调整评分概率
        if user['user_type'] == 'vip':
            promoter_prob = 0.7  # VIP用户推荐概率更高
            detractor_prob = 0.1
        else:
            promoter_prob = 0.6
            detractor_prob = 0.2
            
        # 确定NPS评分
        rand = np.random.random()
        if rand < promoter_prob:  # 推荐者
            score = np.random.choice([9, 10], p=[0.4, 0.6])
        elif rand < (1 - detractor_prob):  # 中立者
            score = np.random.choice([7, 8], p=[0.5, 0.5])
        else:  # 批评者
            score = np.random.randint(0, 7)
        
        # 选择调研渠道（考虑用户属性）
        if user['age_group'] in ['18-24', '25-34']:
            # 年轻用户更倾向于使用APP
            channel_weights = [0.2, 0.3, 0.5]  # sms, email, app
        else:
            # 年长用户更倾向于使用短信
            channel_weights = [0.4, 0.3, 0.3]
            
        return {
            'survey_id': f's_{uuid.uuid4().hex[:8]}',
            'user_id': user['user_id'],
            'survey_time': self.faker.date_time_between(
                start_date=user['register_time'],
                end_date=self.end_date
            ),
            'nps_score': score,
            'feedback_text': self._generate_feedback_text(score),
            'survey_channel': np.random.choice(
                ['sms', 'email', 'app'],
                p=channel_weights
            )
        }
        
    def _validate_behavior_data(self, df: pd.DataFrame) -> None:
        """验证用户行为数据质量
        
        检查项目：
        1. 行为ID唯一性
        2. 行为时间顺序
        3. 停留时间合理性
        4. 行为路径完整性
        
        Args:
            df (pd.DataFrame): 行为数据框
        """
        # 检查行为ID唯一性
        if df['log_id'].duplicated().any():
            self.logger.warning("发现重复的行为日志ID")
            
        # 检查行为时间顺序
        df_sorted = df.sort_values(['user_id', 'behavior_time'])
        if not df_sorted.equals(df):
            self.logger.warning("行为记录的时间顺序不正确")
            
        # 检查停留时间合理性
        invalid_duration = df[
            (df['stay_time'] < 0) | (df['stay_time'] > 3600)  # 超过1小时的停留时间
        ]
        if len(invalid_duration) > 0:
            self.logger.warning(f"发现{len(invalid_duration)}条异常停留时间记录")
            
        # 检查设备类型有效性
        if not df['device_type'].isin(['mobile', 'pc']).all():
            self.logger.warning("发现无效的设备类型")
            
        # 检查行为类型有效性
        valid_behaviors = set()
        for pattern in USER_BEHAVIOR_CONFIG['path_patterns'].values():
            valid_behaviors.update(pattern['steps'])
        if not df['behavior_type'].isin(valid_behaviors).all():
            self.logger.warning("发现无效的行为类型")
            
    def _validate_nps_data(self, df: pd.DataFrame) -> None:
        """验证NPS调研数据质量
        
        检查项目：
        1. 调研ID唯一性
        2. 评分范围有效性
        3. 调研渠道有效性
        4. 反馈文本完整性
        
        Args:
            df (pd.DataFrame): NPS数据框
        """
        # 检查调研ID唯一性
        if df['survey_id'].duplicated().any():
            self.logger.warning("发现重复的调研ID")
            
        # 检查评分范围
        invalid_scores = df[
            (df['nps_score'] < 0) | (df['nps_score'] > 10)
        ]
        if len(invalid_scores) > 0:
            self.logger.warning(f"发现{len(invalid_scores)}条无效的NPS评分")
            
        # 检查调研渠道有效性
        if not df['survey_channel'].isin(['sms', 'email', 'app']).all():
            self.logger.warning("发现无效的调研渠道")
            
        # 检查反馈文本完整性
        missing_feedback = df['feedback_text'].isnull().sum()
        if missing_feedback > 0:
            self.logger.warning(f"发现{missing_feedback}条缺失的反馈文本")
    
    def generate_all_data(self) -> Dict[str, pd.DataFrame]:
        """生成所有数据表
        
        Returns:
            Dict[str, pd.DataFrame]: 包含所有数据表的字典
        """
        self.logger.info("开始生成全部数据...")
        
        # 生成用户基础信息
        user_df = self.generate_user_base()
        
        # 生成交易数据
        transaction_df = self.generate_transactions(user_df)
        
        # 生成用户行为数据
        behavior_df = self.generate_user_behaviors(user_df)
        
        # 生成NPS调研数据
        nps_df = self.generate_nps_surveys(user_df)
        
        self.logger.info("所有数据生成完成")
        
        return {
            'user_base': user_df,
            'transaction': transaction_df,
            'user_behavior': behavior_df,
            'nps_survey': nps_df
        } 