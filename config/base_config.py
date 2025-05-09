"""
基础配置文件
包含所有模拟数据生成器通用的配置参数
"""

# 时间配置
TIME_CONFIG = {
    'start_date': '2023-01-01',
    'end_date': '2023-12-31',
    'peak_hours': {
        'lunch': {'start': '11:30', 'end': '13:30'},
        'dinner': {'start': '18:00', 'end': '20:00'}
    },
    'weekday_weight': 1.0,
    'weekend_weight': 1.5,
    'holiday_weight': 2.0
}

# 数据量配置
VOLUME_CONFIG = {
    'min_users': 5000,
    'max_users': 10000,
    'avg_orders_per_user': {
        'min': 3,
        'max': 12
    }
}

# 用户属性配置
USER_ATTRIBUTES = {
    'age_groups': ['18-24', '25-34', '35-44', '45-54', '55+'],
    'age_distribution': [0.15, 0.35, 0.25, 0.15, 0.1],
    'gender_distribution': {
        'male': 0.48,
        'female': 0.52
    },
    'city_tiers': ['一线城市', '二线城市', '三线城市', '其他'],
    'city_distribution': {
        '一线城市': 0.3,
        '二线城市': 0.4,
        '三线城市': 0.2,
        '其他': 0.1
    }
}

# 支付方式配置
PAYMENT_METHODS = {
    'offline': {
        'cash': 0.2,
        'card': 0.3,
        'mobile_pay': 0.5
    },
    'online': {
        'alipay': 0.4,
        'wechat': 0.5,
        'other': 0.1
    }
}

# 数据质量控制配置
QUALITY_CONTROL = {
    'missing_rate': 0.03,      # 允许的缺失值比例
    'anomaly_rate': 0.05,      # 允许的异常值比例
    'validation_rules': {
        'min_age': 18,
        'max_age': 80,
        'min_amount': 50,
        'max_amount': 5000,
        'max_daily_purchases': 5
    }
}

# 时间分布配置
TIME_DISTRIBUTION = {
    'weekday_weights': {  # 工作日权重
        0: 0.8,  # 周一
        1: 0.9,
        2: 1.0,
        3: 1.0,
        4: 1.1,
        5: 1.5,  # 周六
        6: 1.3   # 周日
    },
    'hour_weights': {  # 小时权重
        '00-06': 0.1,
        '06-09': 0.5,
        '09-12': 1.2,
        '12-14': 0.8,
        '14-17': 1.0,
        '17-20': 1.5,
        '20-22': 1.3,
        '22-24': 0.6
    }
}

# 节假日配置
HOLIDAY_CONFIG = {
    'chinese_new_year': {'month': 2, 'days': 7, 'traffic_multiplier': 0.2},  # 春节期间流量下降
    'national_day': {'month': 10, 'days': 7, 'traffic_multiplier': 3.0},
    'singles_day': {'month': 11, 'days': 1, 'traffic_multiplier': 5.0},  # 双11
    'new_year': {'month': 1, 'days': 1, 'traffic_multiplier': 1.5}
}

# NPS配置
NPS_CONFIG = {
    'score_distribution': {
        'promoters': 0.4,     # 9-10分
        'passives': 0.4,      # 7-8分
        'detractors': 0.2     # 0-6分
    },
    'feedback_probability': 0.3,  # 填写反馈的概率
    'response_delay': {
        'min': 1,             # 最小延迟（小时）
        'max': 48             # 最大延迟（小时）
    }
}

# 会员等级配置
MEMBERSHIP_CONFIG = {
    'levels': {
        'bronze': {
            'min_points': 0,
            'max_points': 1000,
            'discount': 0.95
        },
        'silver': {
            'min_points': 1001,
            'max_points': 3000,
            'discount': 0.90
        },
        'gold': {
            'min_points': 3001,
            'max_points': 10000,
            'discount': 0.85
        },
        'platinum': {
            'min_points': 10001,
            'max_points': float('inf'),
            'discount': 0.80
        }
    },
    'points_rules': {
        'spend_ratio': 1,      # 每消费1元获得的积分
        'bonus_points': {
            'birthday': 500,   # 生日奖励
            'holiday': 200,    # 节假日奖励
            'review': 50       # 评价奖励
        },
        'expiration': 365      # 积分有效期（天）
    }
}

# 数据验证规则
VALIDATION_RULES = {
    'user_base': {
        'required_fields': ['user_id', 'register_time', 'user_type'],
        'unique_fields': ['user_id'],
        'value_ranges': {
            'user_type': ['normal', 'vip'],
            'age_group': USER_ATTRIBUTES['age_groups'],
            'gender': list(USER_ATTRIBUTES['gender_distribution'].keys()),
            'city_tier': USER_ATTRIBUTES['city_tiers']
        }
    },
    'transaction': {
        'required_fields': ['transaction_id', 'user_id', 'transaction_time', 'amount'],
        'unique_fields': ['transaction_id'],
        'value_ranges': {
            'payment_method': list(PAYMENT_METHODS['online'].keys()) + list(PAYMENT_METHODS['offline'].keys()),
            'quantity': {'min': 1, 'max': 100},
            'amount': {'min': 0, 'max': 100000}
        }
    }
} 