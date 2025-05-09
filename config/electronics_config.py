"""
3C数码行业特定配置文件
包含3C数码零售特有的业务参数配置
"""

from .base_config import TIME_CONFIG, VOLUME_CONFIG

# 商品品类配置
PRODUCT_CATEGORY_CONFIG = {
    'category_distribution': {
        'mobile': 0.35,      # 手机
        'computer': 0.25,    # 电脑
        'camera': 0.15,      # 相机
        'accessory': 0.25    # 配件
    },
    'categories': {
        'mobile': {
            'subcategories': ['smartphone', 'feature_phone', 'tablet'],
            'price_ranges': {
                'smartphone': {'min': 1999, 'max': 8999},
                'feature_phone': {'min': 299, 'max': 999},
                'tablet': {'min': 1299, 'max': 6999}
            },
            'brand_distribution': {
                'apple': 0.35,
                'samsung': 0.25,
                'huawei': 0.20,
                'xiaomi': 0.15,
                'others': 0.05
            }
        },
        'computer': {
            'subcategories': ['laptop', 'desktop', 'workstation'],
            'price_ranges': {
                'laptop': {'min': 3999, 'max': 15999},
                'desktop': {'min': 2999, 'max': 12999},
                'workstation': {'min': 8999, 'max': 29999}
            },
            'brand_distribution': {
                'lenovo': 0.30,
                'dell': 0.25,
                'hp': 0.20,
                'apple': 0.15,
                'others': 0.10
            }
        },
        'camera': {
            'subcategories': ['dslr', 'mirrorless', 'video_camera'],
            'price_ranges': {
                'dslr': {'min': 2999, 'max': 19999},
                'mirrorless': {'min': 3999, 'max': 24999},
                'video_camera': {'min': 1999, 'max': 9999}
            },
            'brand_distribution': {
                'canon': 0.35,
                'sony': 0.30,
                'nikon': 0.25,
                'others': 0.10
            }
        },
        'accessory': {
            'subcategories': ['headphone', 'charger', 'case', 'storage'],
            'price_ranges': {
                'headphone': {'min': 99, 'max': 2999},
                'charger': {'min': 39, 'max': 299},
                'case': {'min': 29, 'max': 399},
                'storage': {'min': 49, 'max': 1999}
            },
            'brand_distribution': {
                'anker': 0.20,
                'jbl': 0.15,
                'sandisk': 0.15,
                'belkin': 0.10,
                'others': 0.40
            }
        }
    }
}

# 渠道配置
CHANNEL_CONFIG = {
    'online': {
        'distribution': 0.65,  # 线上渠道占比
        'platforms': {
            'self_operated': 0.40,  # 自营官网/APP
            'tmall': 0.30,         # 天猫
            'jd': 0.20,           # 京东
            'others': 0.10        # 其他平台
        },
        'commission_rates': {
            'tmall': 0.05,
            'jd': 0.045,
            'others': 0.06
        }
    },
    'offline': {
        'distribution': 0.35,  # 线下渠道占比
        'store_types': {
            'flagship': 0.30,    # 旗舰店
            'experience': 0.40,  # 体验店
            'authorized': 0.30   # 授权店
        },
        'location_distribution': {
            'shopping_mall': 0.50,
            'business_district': 0.30,
            'community': 0.20
        }
    }
}

# 用户行为配置
USER_BEHAVIOR_CONFIG = {
    'purchase_patterns': {
        'planned': {
            'research_time': {'min': 7, 'max': 30},  # 天
            'comparison_count': {'min': 3, 'max': 8},
            'probability': 0.7
        },
        'impulse': {
            'research_time': {'min': 1, 'max': 3},
            'comparison_count': {'min': 1, 'max': 3},
            'probability': 0.3
        }
    },
    'research_channels': {
        'online_review': 0.35,
        'offline_experience': 0.25,
        'friend_recommendation': 0.20,
        'professional_review': 0.15,
        'social_media': 0.05
    },
    'device_preferences': {
        'mobile': 0.65,
        'pc': 0.25,
        'tablet': 0.10
    }
}

# 促销活动配置
PROMOTION_CONFIG = {
    'special_dates': {
        (6, 18): {  # 618
            'discount_range': (0.7, 0.9),
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
        'clearance_sale': {
            'discount_range': (0.5, 0.7),
            'duration': 30,
            'traffic_multiplier': 1.8
        },
        'member_exclusive': {
            'discount': 0.85,
            'duration': 7,
            'traffic_multiplier': 1.3
        }
    }
}

# 售后服务配置
AFTER_SALES_CONFIG = {
    'warranty_period': {
        'mobile': 365,      # 天
        'computer': 730,
        'camera': 545,
        'accessory': 180
    },
    'return_period': {
        'online': 7,       # 天
        'offline': 15
    },
    'service_types': {
        'repair': {
            'warranty': {'free': 0.8, 'paid': 0.2},
            'out_warranty': {'paid': 1.0}
        },
        'replacement': {
            'warranty': {'free': 0.6, 'paid': 0.4},
            'out_warranty': {'paid': 1.0}
        }
    },
    'issue_types': {
        'hardware_failure': 0.4,
        'software_issue': 0.3,
        'physical_damage': 0.2,
        'other': 0.1
    }
}

# 库存管理配置
INVENTORY_CONFIG = {
    'replenishment_cycle': {
        'hot_products': 7,    # 天
        'regular_products': 15,
        'slow_moving': 30
    },
    'safety_stock': {
        'hot_products': 30,   # 天
        'regular_products': 45,
        'slow_moving': 60
    },
    'storage_cost': {
        'mobile': 50,        # 元/件/月
        'computer': 80,
        'camera': 40,
        'accessory': 10
    }
}

# 会员体系配置
MEMBERSHIP_CONFIG = {
    'levels': {
        'bronze': {
            'spending_threshold': 0,
            'discount': 0.98,
            'point_rate': 1
        },
        'silver': {
            'spending_threshold': 5000,
            'discount': 0.95,
            'point_rate': 1.2
        },
        'gold': {
            'spending_threshold': 20000,
            'discount': 0.92,
            'point_rate': 1.5
        },
        'platinum': {
            'spending_threshold': 50000,
            'discount': 0.88,
            'point_rate': 2.0
        }
    },
    'benefits': {
        'birthday_discount': 0.85,
        'point_exchange_rate': 100,  # 100积分=1元
        'exclusive_event_access': True,
        'free_delivery': True
    }
} 