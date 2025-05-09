#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成行业模拟数据样本
"""
import json
import os
from datetime import datetime

def generate_industry_sample_data():
    """生成行业样本数据并保存为JSON文件"""
    # 创建目录
    os.makedirs('data/merchant_sample', exist_ok=True)
    
    # 准备数据
    data = {
        'restaurant': {
            'users': 5000,
            'transactions': 12500,
            'menu_items': 45,
            'average_order': 125.8,
            'peak_hours': ['11:30-13:30', '18:00-20:30'],
            'popular_dishes': ['红烧肉', '鱼香肉丝', '宫保鸡丁'],
            'customer_distribution': {
                '18-25岁': 0.15,
                '26-35岁': 0.40,
                '36-45岁': 0.25,
                '46-60岁': 0.15,
                '60岁以上': 0.05
            }
        },
        'ecommerce': {
            'users': 8200,
            'products': 1200,
            'orders': 25000,
            'average_order': 210.5,
            'return_rate': 0.18,
            'popular_categories': ['服装', '电子产品', '家居用品'],
            'traffic_sources': {
                '搜索引擎': 0.45,
                '社交媒体': 0.30,
                '直接访问': 0.15,
                '邮件营销': 0.10
            }
        },
        'retail': {
            'users': 7500,
            'products': 3500,
            'transactions': 18000,
            'average_basket': 158.75,
            'store_locations': 5,
            'popular_times': ['周末', '节假日'],
            'payment_methods': {
                '支付宝': 0.35,
                '微信支付': 0.40,
                '银行卡': 0.20,
                '现金': 0.05
            }
        },
        'service': {
            'users': 4200,
            'appointments': 9800,
            'services': 55,
            'average_cost': 320.0,
            'booking_channels': {
                '在线': 0.65,
                '电话': 0.25,
                '现场': 0.10
            }
        }
    }
    
    # 行业成本占比数据
    cost_breakdown = {
        'restaurant': {
            'labor': 0.35,
            'raw_material': 0.40,
            'rent': 0.15,
            'utilities': 0.05,
            'marketing': 0.05
        },
        'ecommerce': {
            'product_cost': 0.65,
            'logistics': 0.15,
            'platform': 0.10,
            'marketing': 0.08,
            'customer_service': 0.02
        },
        'retail': {
            'inventory': 0.60,
            'labor': 0.20,
            'rent': 0.12,
            'utilities': 0.04,
            'marketing': 0.04
        },
        'service': {
            'labor': 0.55,
            'rent': 0.20,
            'equipment': 0.15,
            'marketing': 0.05,
            'utilities': 0.05
        }
    }
    
    # 将成本数据添加到主数据中
    for industry in data:
        data[industry]['cost_breakdown'] = cost_breakdown[industry]
    
    # 添加元数据
    metadata = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_period': '2023-01-01 至 2023-03-31',
        'data_source': '智能商户经营分析平台数据模拟器',
        'version': '1.0.0'
    }
    
    final_data = {
        'metadata': metadata,
        'industries': data
    }
    
    # 保存为JSON文件
    file_path = 'data/merchant_sample/industry_data.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 行业数据样本已生成: {file_path}")
    
    # 创建指向DATA_README的链接
    link_path = 'data/merchant_sample/data_schema.md'
    with open(link_path, 'w', encoding='utf-8') as f:
        f.write("# 行业数据说明\n\n")
        f.write("详细的数据结构和说明请参考：\n\n")
        f.write("[数据说明文档](../../services/data_simulator/DATA_README.md)\n")
    
    print(f"✅ 数据说明文档链接已创建: {link_path}")

if __name__ == "__main__":
    generate_industry_sample_data() 