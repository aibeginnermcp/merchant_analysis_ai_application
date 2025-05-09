"""
服饰电商特定配置文件
包含服饰电商特有的业务参数配置
"""

from .base_config import TIME_CONFIG, VOLUME_CONFIG

# 商品品类配置
CATEGORY_CONFIG = {
    'category_distribution': {
        'tops': 0.456,      # 上装
        'dresses': 0.282,   # 连衣裙
        'bottoms': 0.262    # 下装
    },
    'categories': {
        'tops': {
            'subcategories': ['t_shirt', 'shirt', 'sweater', 'coat'],
            'price_ranges': {
                't_shirt': {'min': 99, 'max': 299},
                'shirt': {'min': 199, 'max': 499},
                'sweater': {'min': 299, 'max': 699},
                'coat': {'min': 499, 'max': 1299}
            },
            'season_multiplier': {
                'spring': 1.2,
                'summer': 0.8,
                'autumn': 1.5,
                'winter': 1.3
            }
        },
        'dresses': {
            'subcategories': ['casual_dress', 'party_dress', 'work_dress'],
            'price_ranges': {
                'casual_dress': {'min': 199, 'max': 599},
                'party_dress': {'min': 399, 'max': 999},
                'work_dress': {'min': 299, 'max': 799}
            },
            'season_multiplier': {
                'spring': 1.3,
                'summer': 1.5,
                'autumn': 1.2,
                'winter': 0.8
            }
        },
        'bottoms': {
            'subcategories': ['jeans', 'skirt', 'pants'],
            'price_ranges': {
                'jeans': {'min': 299, 'max': 699},
                'skirt': {'min': 199, 'max': 499},
                'pants': {'min': 249, 'max': 599}
            },
            'season_multiplier': {
                'spring': 1.2,
                'summer': 1.0,
                'autumn': 1.4,
                'winter': 1.1
            }
        }
    }
}

# 退货配置
RETURN_CONFIG = {
    'base_return_rate': 0.201,  # 基础退货率
    'category_factors': {
        'tops': 1.0,      # 基准退货率
        'dresses': 1.2,   # 连衣裙退货率较高
        'bottoms': 1.1    # 下装退货率略高
    },
    'price_factors': {
        'low': 0.8,    # 低价商品（<200）
        'medium': 1.0,  # 中价商品（200-500）
        'high': 1.2    # 高价商品（>500）
    },
    'reason_distribution': {
        'size_issue': 0.4,    # 尺码问题
        'style_issue': 0.25,  # 款式与图片不符
        'quality_issue': 0.15, # 质量问题
        'delivery_issue': 0.1, # 物流问题
        'other': 0.1          # 其他原因
    }
}

# 用户行为配置
USER_BEHAVIOR_CONFIG = {
    'path_patterns': {
        'direct_purchase': {
            'steps': ['view_item', 'add_cart', 'checkout'],
            'probability': 0.3
        },
        'browse_purchase': {
            'steps': ['view_category', 'view_list', 'view_item', 'add_cart', 'checkout'],
            'probability': 0.4
        },
        'compare_purchase': {
            'steps': ['view_category', 'view_list', 'view_item', 'view_list', 'view_item', 'add_cart', 'checkout'],
            'probability': 0.2
        },
        'abandon': {
            'steps': ['view_category', 'view_list', 'view_item', 'add_cart'],
            'probability': 0.1
        }
    },
    'step_duration': {
        'view_category': {'min': 10, 'max': 60},
        'view_list': {'min': 20, 'max': 120},
        'view_item': {'min': 30, 'max': 180},
        'add_cart': {'min': 5, 'max': 30},
        'checkout': {'min': 60, 'max': 300}
    },
    'device_distribution': {
        'mobile': 0.707,  # 移动端占比
        'pc': 0.293       # PC端占比
    }
}

# 促销活动配置
PROMOTION_CONFIG = {
    'special_dates': {
        (11, 11): {  # 双11
            'traffic_multiplier': 3.0,
            'conversion_rate_boost': 0.4,
            'min_discount': 0.5,
            'max_discount': 0.7
        },
        (12, 12): {  # 双12
            'traffic_multiplier': 2.5,
            'conversion_rate_boost': 0.3,
            'min_discount': 0.6,
            'max_discount': 0.8
        },
        (6, 18): {   # 618
            'traffic_multiplier': 2.8,
            'conversion_rate_boost': 0.35,
            'min_discount': 0.5,
            'max_discount': 0.7
        }
    },
    'seasonal_promotion': {
        'spring': {
            'start_month': 3,
            'end_month': 5,
            'discount_range': (0.8, 0.9)
        },
        'summer': {
            'start_month': 6,
            'end_month': 8,
            'discount_range': (0.75, 0.85)
        },
        'autumn': {
            'start_month': 9,
            'end_month': 11,
            'discount_range': (0.8, 0.9)
        },
        'winter': {
            'start_month': 12,
            'end_month': 2,
            'discount_range': (0.7, 0.8)
        }
    },
    'min_discount': 0.5,
    'max_discount': 0.8
}

# 转化率配置
CONVERSION_CONFIG = {
    'base_rates': {
        'view_list_to_view_item': 0.4,    # 列表页到商品详情
        'view_item_to_add_cart': 0.3,     # 商品详情到加购
        'add_cart_to_checkout': 0.25      # 加购到支付
    },
    'user_type_factors': {
        'vip': 1.2,    # VIP用户转化率提升
        'normal': 1.0   # 普通用户基准转化率
    },
    'price_factors': {
        'low': 1.2,    # 低价商品转化率较高
        'medium': 1.0,  # 中价商品基准转化率
        'high': 0.8    # 高价商品转化率较低
    },
    'promotion_boost': {
        'special_day': 1.5,  # 特殊促销日
        'season_end': 1.3,   # 季末促销
        'normal': 1.0        # 普通日期
    }
} 