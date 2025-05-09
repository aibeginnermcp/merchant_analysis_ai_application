"""
美妆个护行业特定配置文件
包含美妆个护零售特有的业务参数配置
"""

from .base_config import TIME_CONFIG, VOLUME_CONFIG

# 商品品类配置
PRODUCT_CATEGORY_CONFIG = {
    'category_distribution': {
        'skincare': 0.35,     # 护肤
        'makeup': 0.25,       # 彩妆
        'perfume': 0.15,      # 香水
        'personal_care': 0.25 # 个人护理
    },
    'categories': {
        'skincare': {
            'subcategories': ['cleanser', 'toner', 'serum', 'cream', 'mask'],
            'price_ranges': {
                'cleanser': {'min': 99, 'max': 399},
                'toner': {'min': 129, 'max': 499},
                'serum': {'min': 199, 'max': 1299},
                'cream': {'min': 159, 'max': 999},
                'mask': {'min': 15, 'max': 199}
            },
            'brand_distribution': {
                'luxury': 0.25,
                'high_end': 0.35,
                'mass_market': 0.30,
                'others': 0.10
            }
        },
        'makeup': {
            'subcategories': ['foundation', 'lipstick', 'eye_shadow', 'mascara', 'blush'],
            'price_ranges': {
                'foundation': {'min': 159, 'max': 599},
                'lipstick': {'min': 129, 'max': 399},
                'eye_shadow': {'min': 199, 'max': 699},
                'mascara': {'min': 99, 'max': 299},
                'blush': {'min': 129, 'max': 399}
            },
            'brand_distribution': {
                'luxury': 0.30,
                'high_end': 0.40,
                'mass_market': 0.25,
                'others': 0.05
            }
        },
        'perfume': {
            'subcategories': ['eau_de_parfum', 'eau_de_toilette', 'body_mist'],
            'price_ranges': {
                'eau_de_parfum': {'min': 399, 'max': 1499},
                'eau_de_toilette': {'min': 299, 'max': 999},
                'body_mist': {'min': 99, 'max': 299}
            },
            'brand_distribution': {
                'luxury': 0.45,
                'high_end': 0.35,
                'mass_market': 0.15,
                'others': 0.05
            }
        },
        'personal_care': {
            'subcategories': ['shampoo', 'body_wash', 'lotion', 'sunscreen', 'hand_cream'],
            'price_ranges': {
                'shampoo': {'min': 59, 'max': 299},
                'body_wash': {'min': 49, 'max': 199},
                'lotion': {'min': 79, 'max': 399},
                'sunscreen': {'min': 99, 'max': 299},
                'hand_cream': {'min': 29, 'max': 159}
            },
            'brand_distribution': {
                'luxury': 0.15,
                'high_end': 0.30,
                'mass_market': 0.45,
                'others': 0.10
            }
        }
    }
}

# 用户画像配置
USER_PROFILE_CONFIG = {
    'skin_types': {
        'distribution': {
            'dry': 0.25,
            'oily': 0.30,
            'combination': 0.35,
            'sensitive': 0.10
        },
        'product_preference': {
            'dry': ['cream', 'serum', 'mask'],
            'oily': ['toner', 'cleanser', 'mask'],
            'combination': ['serum', 'toner', 'cream'],
            'sensitive': ['cream', 'cleanser', 'sunscreen']
        }
    },
    'makeup_styles': {
        'distribution': {
            'natural': 0.40,
            'trendy': 0.30,
            'dramatic': 0.15,
            'minimal': 0.15
        },
        'product_preference': {
            'natural': ['foundation', 'lipstick', 'blush'],
            'trendy': ['eye_shadow', 'lipstick', 'mascara'],
            'dramatic': ['eye_shadow', 'mascara', 'foundation'],
            'minimal': ['lipstick', 'mascara', 'blush']
        }
    },
    'fragrance_preferences': {
        'distribution': {
            'floral': 0.35,
            'fresh': 0.25,
            'woody': 0.20,
            'oriental': 0.20
        }
    },
    'purchase_behavior': {
        'frequency': {
            'high': 0.20,    # 每月2-3次
            'medium': 0.50,  # 每月1次
            'low': 0.30     # 每2-3个月1次
        },
        'price_sensitivity': {
            'high': 0.30,    # 价格敏感
            'medium': 0.50,  # 适中
            'low': 0.20     # 不敏感
        }
    }
}

# 渠道配置
CHANNEL_CONFIG = {
    'online': {
        'distribution': 0.70,  # 线上渠道占比
        'platforms': {
            'self_operated': 0.30,  # 自营官网/APP
            'tmall': 0.35,         # 天猫
            'jd': 0.20,           # 京东
            'others': 0.15        # 其他平台
        },
        'commission_rates': {
            'tmall': 0.05,
            'jd': 0.045,
            'others': 0.06
        }
    },
    'offline': {
        'distribution': 0.30,  # 线下渠道占比
        'store_types': {
            'department': 0.40,   # 百货专柜
            'specialty': 0.35,    # 专营店
            'drugstore': 0.25     # 药妆店
        },
        'location_distribution': {
            'shopping_mall': 0.60,
            'business_district': 0.25,
            'community': 0.15
        }
    }
}

# 促销活动配置
PROMOTION_CONFIG = {
    'special_dates': {
        (3, 8): {  # 妇女节
            'discount_range': (0.8, 0.9),
            'traffic_multiplier': 2.0,
            'conversion_rate_boost': 0.2
        },
        (6, 18): {  # 618
            'discount_range': (0.7, 0.85),
            'traffic_multiplier': 3.0,
            'conversion_rate_boost': 0.3
        },
        (11, 11): {  # 双11
            'discount_range': (0.6, 0.8),
            'traffic_multiplier': 4.0,
            'conversion_rate_boost': 0.4
        },
        (12, 12): {  # 双12
            'discount_range': (0.7, 0.85),
            'traffic_multiplier': 2.5,
            'conversion_rate_boost': 0.25
        }
    },
    'regular_promotion': {
        'new_product_launch': {
            'discount': 0.9,
            'duration': 15,  # 天
            'traffic_multiplier': 1.5
        },
        'seasonal_sale': {
            'discount_range': (0.7, 0.85),
            'duration': 30,
            'traffic_multiplier': 1.8
        },
        'member_exclusive': {
            'discount': 0.85,
            'duration': 7,
            'traffic_multiplier': 1.3
        }
    },
    'bundle_deals': {
        'skincare_set': {
            'discount': 0.8,
            'required_items': 3
        },
        'makeup_set': {
            'discount': 0.85,
            'required_items': 3
        }
    }
}

# 用户行为配置
USER_BEHAVIOR_CONFIG = {
    'browsing_patterns': {
        'quick_purchase': {
            'duration': {'min': 5, 'max': 15},  # 分钟
            'page_views': {'min': 2, 'max': 5},
            'probability': 0.3
        },
        'research_based': {
            'duration': {'min': 20, 'max': 45},
            'page_views': {'min': 6, 'max': 15},
            'probability': 0.5
        },
        'extensive_research': {
            'duration': {'min': 45, 'max': 90},
            'page_views': {'min': 15, 'max': 30},
            'probability': 0.2
        }
    },
    'purchase_triggers': {
        'replenishment': 0.4,    # 补货
        'new_product': 0.25,     # 新品尝试
        'promotion': 0.20,       # 促销活动
        'recommendation': 0.15   # 推荐购买
    }
}

# 库存管理配置
INVENTORY_CONFIG = {
    'replenishment_cycle': {
        'high_turnover': 7,     # 天（畅销品）
        'medium_turnover': 15,   # 天（常规品）
        'low_turnover': 30      # 天（低频品）
    },
    'safety_stock': {
        'high_turnover': 21,    # 天
        'medium_turnover': 30,   # 天
        'low_turnover': 45      # 天
    },
    'shelf_life': {
        'skincare': 730,        # 天（2年）
        'makeup': 545,          # 天（1.5年）
        'perfume': 1095,        # 天（3年）
        'personal_care': 730    # 天（2年）
    }
}

# 会员体系配置
MEMBERSHIP_CONFIG = {
    'levels': {
        'bronze': {
            'spending_threshold': 0,
            'discount': 0.98,
            'point_rate': 1,
            'birthday_gift': True
        },
        'silver': {
            'spending_threshold': 3000,
            'discount': 0.95,
            'point_rate': 1.2,
            'birthday_gift': True,
            'seasonal_gift': True
        },
        'gold': {
            'spending_threshold': 10000,
            'discount': 0.92,
            'point_rate': 1.5,
            'birthday_gift': True,
            'seasonal_gift': True,
            'exclusive_event': True
        },
        'platinum': {
            'spending_threshold': 30000,
            'discount': 0.88,
            'point_rate': 2.0,
            'birthday_gift': True,
            'seasonal_gift': True,
            'exclusive_event': True,
            'vip_service': True
        }
    },
    'points_system': {
        'exchange_rate': 100,  # 100积分=1元
        'expiration': 365,    # 积分有效期（天）
        'minimum_exchange': 1000  # 最低兑换积分
    }
} 