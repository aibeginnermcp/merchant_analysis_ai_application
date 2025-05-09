"""
生成少量样本数据的测试脚本
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
from faker import Faker
from config.base_config import PAYMENT_METHODS, USER_ATTRIBUTES
from config.fashion_ecommerce_config import CATEGORY_CONFIG, RETURN_CONFIG
from src.generators.fashion_ecommerce_generator import FashionEcommerceGenerator

class SampleFashionGenerator(FashionEcommerceGenerator):
    def __init__(self, sample_size=100):
        super().__init__()
        self.user_count = sample_size  # 覆盖父类的随机用户数
        
    def generate_transactions(self, user_df: pd.DataFrame) -> pd.DataFrame:
        """重写交易生成方法，每个用户只生成1-2条记录"""
        transactions = []
        for _, user in user_df.iterrows():
            # 每个用户生成1-2条交易记录
            for _ in range(np.random.randint(1, 3)):
                transaction_time = self.faker.date_time_between(
                    start_date=user['register_time'],
                    end_date=self.end_date
                )
                
                category = np.random.choice(
                    list(CATEGORY_CONFIG['category_distribution'].keys()),
                    p=list(CATEGORY_CONFIG['category_distribution'].values())
                )
                subcategory = np.random.choice(
                    CATEGORY_CONFIG['categories'][category]['subcategories']
                )
                
                price_range = CATEGORY_CONFIG['categories'][category]['price_ranges'][subcategory]
                amount = np.random.uniform(price_range['min'], price_range['max'])
                
                season = self._get_season(transaction_time)
                season_multiplier = CATEGORY_CONFIG['categories'][category]['season_multiplier'][season]
                amount *= season_multiplier
                
                if self._is_promotion_period(transaction_time):
                    discount = np.random.uniform(0.5, 0.8)
                    amount *= discount
                
                transaction = {
                    'transaction_id': f't_{uuid.uuid4().hex[:8]}',
                    'user_id': user['user_id'],
                    'transaction_time': transaction_time,
                    'amount': round(amount, 2),
                    'payment_method': np.random.choice(
                        PAYMENT_METHODS['methods'],
                        p=PAYMENT_METHODS['distribution']
                    ),
                    'category': category,
                    'subcategory': subcategory,
                    'quantity': np.random.randint(1, 4),
                    'is_refunded': np.random.random() < RETURN_CONFIG['base_return_rate']
                }
                transactions.append(transaction)
        
        return pd.DataFrame(transactions)

def create_output_dirs():
    """创建输出目录"""
    dirs = ['output/sample', 'reports/sample']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

def analyze_user_base(df: pd.DataFrame) -> str:
    """分析用户基础信息"""
    analysis = []
    analysis.append("\n=== 用户画像分析 ===")
    
    # 用户类型分布
    vip_rate = (df['user_type'] == 'vip').mean() * 100
    analysis.append(f"VIP用户占比: {vip_rate:.1f}%")
    
    # 性别分布
    gender_dist = df['gender'].value_counts(normalize=True) * 100
    analysis.append("\n性别分布:")
    for gender, pct in gender_dist.items():
        analysis.append(f"- {gender}: {pct:.1f}%")
    
    # 年龄段分布
    age_dist = df['age_group'].value_counts(normalize=True) * 100
    analysis.append("\n年龄段分布:")
    for age, pct in age_dist.items():
        analysis.append(f"- {age}: {pct:.1f}%")
    
    # 城市等级分布
    city_dist = df['city_tier'].value_counts(normalize=True) * 100
    analysis.append("\n城市等级分布:")
    for city, pct in city_dist.items():
        analysis.append(f"- {city}: {pct:.1f}%")
    
    # 注册时间分布
    earliest_reg = df['register_time'].min()
    latest_reg = df['register_time'].max()
    analysis.append(f"\n注册时间范围: {earliest_reg.strftime('%Y-%m-%d')} 至 {latest_reg.strftime('%Y-%m-%d')}")
    
    return "\n".join(analysis)

def analyze_transactions(df: pd.DataFrame) -> str:
    """分析交易数据"""
    analysis = []
    analysis.append("\n=== 交易数据分析 ===")
    
    # 基础交易指标
    analysis.append(f"总交易额: ¥{df['amount'].sum():.2f}")
    analysis.append(f"平均客单价: ¥{df['amount'].mean():.2f}")
    analysis.append(f"最高订单金额: ¥{df['amount'].max():.2f}")
    analysis.append(f"最低订单金额: ¥{df['amount'].min():.2f}")
    
    # 退货分析
    refund_rate = df['is_refunded'].mean() * 100
    analysis.append(f"退货率: {refund_rate:.1f}%")
    
    # 品类分析
    analysis.append("\n品类销售分布:")
    category_dist = df['category'].value_counts(normalize=True) * 100
    for cat, pct in category_dist.items():
        analysis.append(f"- {cat}: {pct:.1f}%")
    
    # 子品类Top5
    analysis.append("\n热销子品类Top5:")
    subcategory_dist = df['subcategory'].value_counts().head()
    for subcat, count in subcategory_dist.items():
        analysis.append(f"- {subcat}: {count}件")
    
    # 支付方式分析
    analysis.append("\n支付方式分布:")
    payment_dist = df['payment_method'].value_counts(normalize=True) * 100
    for method, pct in payment_dist.items():
        analysis.append(f"- {method}: {pct:.1f}%")
    
    return "\n".join(analysis)

def analyze_user_behaviors(df: pd.DataFrame) -> str:
    """分析用户行为数据"""
    analysis = []
    analysis.append("\n=== 用户行为分析 ===")
    
    # 行为类型分布
    behavior_dist = df['behavior_type'].value_counts(normalize=True) * 100
    analysis.append("用户行为分布:")
    for behavior, pct in behavior_dist.items():
        analysis.append(f"- {behavior}: {pct:.1f}%")
    
    # 设备使用分布
    device_dist = df['device_type'].value_counts(normalize=True) * 100
    analysis.append("\n设备使用分布:")
    for device, pct in device_dist.items():
        analysis.append(f"- {device}: {pct:.1f}%")
    
    # 停留时间分析
    analysis.append(f"\n平均停留时间: {df['stay_time'].mean():.0f}秒")
    analysis.append(f"最长停留时间: {df['stay_time'].max()}秒")
    
    # 行为路径分析
    analysis.append("\n典型行为路径:")
    analysis.append("- 浏览商品 -> 加入购物车 -> 结账")
    analysis.append("- 分类页 -> 商品列表 -> 商品详情 -> 加入购物车")
    
    return "\n".join(analysis)

def analyze_nps_surveys(df: pd.DataFrame) -> str:
    """分析NPS调研数据"""
    analysis = []
    analysis.append("\n=== NPS调研分析 ===")
    
    # NPS评分分布
    promoters = (df['nps_score'] >= 9).mean() * 100
    passives = ((df['nps_score'] >= 7) & (df['nps_score'] <= 8)).mean() * 100
    detractors = (df['nps_score'] <= 6).mean() * 100
    nps = promoters - detractors
    
    analysis.append(f"NPS得分: {nps:.1f}")
    analysis.append(f"推荐者占比: {promoters:.1f}%")
    analysis.append(f"中立者占比: {passives:.1f}%")
    analysis.append(f"批评者占比: {detractors:.1f}%")
    
    # 评分分布
    score_dist = df['nps_score'].value_counts(normalize=True) * 100
    analysis.append("\n评分分布:")
    for score in sorted(score_dist.index):
        analysis.append(f"- {score}分: {score_dist[score]:.1f}%")
    
    # 调研渠道分布
    channel_dist = df['survey_channel'].value_counts(normalize=True) * 100
    analysis.append("\n调研渠道分布:")
    for channel, pct in channel_dist.items():
        analysis.append(f"- {channel}: {pct:.1f}%")
    
    return "\n".join(analysis)

def save_sample_data(data_dict: dict):
    """保存样本数据并生成分析报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存数据并生成分析报告
    for table_name, df in data_dict.items():
        # 保存CSV文件
        filename = f'output/sample/fashion_ecommerce_{table_name}_sample_{timestamp}.csv'
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"\n=== {table_name} 样本数据 ===")
        print(df.head())
        print(f"\n数据已保存到: {filename}")
        
        # 根据表名调用相应的分析函数
        if table_name == 'user_base':
            print(analyze_user_base(df))
        elif table_name == 'transaction':
            print(analyze_transactions(df))
        elif table_name == 'user_behavior':
            print(analyze_user_behaviors(df))
        elif table_name == 'nps_survey':
            print(analyze_nps_surveys(df))

if __name__ == "__main__":
    print("=== 生成服饰电商样本数据 ===")
    
    # 创建输出目录
    create_output_dirs()
    
    # 生成样本数据
    generator = SampleFashionGenerator(sample_size=100)
    sample_data = generator.generate_all_data()
    
    # 保存并分析数据
    save_sample_data(sample_data) 