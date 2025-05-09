#!/usr/bin/env python3
"""
商户智能经营分析平台初始化脚本

用于设置项目环境，包括：
- 创建必要的目录结构
- 初始化数据库
- 创建消息队列
- 设置监控
"""

import os
import sys
from pathlib import Path
import subprocess
import logging

import pymongo
import redis
import pika

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_structure():
    """创建项目目录结构"""
    directories = [
        'services/merchant_bi_shared',
        'services/cashflow_prediction',
        'services/cost_analysis',
        'services/compliance_check',
        'services/data_simulation',
        'tests/unit',
        'tests/integration',
        'docs/api',
        'docs/architecture',
        'config/development',
        'config/production'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f'Created directory: {directory}')
        
def setup_mongodb():
    """初始化MongoDB数据库"""
    try:
        # 连接MongoDB
        client = pymongo.MongoClient(
            os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        )
        
        # 创建数据库
        db = client['merchant_bi']
        
        # 创建集合
        collections = [
            'merchants',
            'cashflow_predictions',
            'cost_analysis',
            'compliance_records',
            'simulation_data'
        ]
        
        for collection in collections:
            if collection not in db.list_collection_names():
                db.create_collection(collection)
                logger.info(f'Created collection: {collection}')
                
        # 创建索引
        db.merchants.create_index('merchant_id', unique=True)
        db.cashflow_predictions.create_index([
            ('merchant_id', pymongo.ASCENDING),
            ('prediction_date', pymongo.DESCENDING)
        ])
        db.cost_analysis.create_index([
            ('merchant_id', pymongo.ASCENDING),
            ('analysis_date', pymongo.DESCENDING)
        ])
        db.compliance_records.create_index([
            ('merchant_id', pymongo.ASCENDING),
            ('check_date', pymongo.DESCENDING)
        ])
        
        logger.info('MongoDB setup completed')
        
    except Exception as e:
        logger.error(f'Failed to setup MongoDB: {str(e)}')
        sys.exit(1)
        
def setup_redis():
    """初始化Redis"""
    try:
        # 连接Redis
        client = redis.from_url(
            os.getenv('REDIS_URI', 'redis://localhost:6379')
        )
        
        # 测试连接
        client.ping()
        
        logger.info('Redis setup completed')
        
    except Exception as e:
        logger.error(f'Failed to setup Redis: {str(e)}')
        sys.exit(1)
        
def setup_rabbitmq():
    """初始化RabbitMQ"""
    try:
        # 连接RabbitMQ
        connection = pika.BlockingConnection(
            pika.URLParameters(
                os.getenv('RABBITMQ_URI', 'amqp://guest:guest@localhost:5672/')
            )
        )
        channel = connection.channel()
        
        # 声明交换机
        exchanges = [
            'merchant_bi.cashflow.events',
            'merchant_bi.cost.events',
            'merchant_bi.compliance.events',
            'merchant_bi.simulation.events'
        ]
        
        for exchange in exchanges:
            channel.exchange_declare(
                exchange=exchange,
                exchange_type='topic',
                durable=True
            )
            logger.info(f'Created exchange: {exchange}')
            
        # 声明死信交换机
        channel.exchange_declare(
            exchange='merchant_bi.dlx',
            exchange_type='direct',
            durable=True
        )
        
        connection.close()
        logger.info('RabbitMQ setup completed')
        
    except Exception as e:
        logger.error(f'Failed to setup RabbitMQ: {str(e)}')
        sys.exit(1)
        
def setup_monitoring():
    """设置监控"""
    try:
        # 创建Prometheus配置
        prometheus_config = '''
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'merchant_bi'
    static_configs:
      - targets: ['localhost:8000']
    '''
        
        with open('config/prometheus.yml', 'w') as f:
            f.write(prometheus_config)
            
        logger.info('Created Prometheus configuration')
        
        # 创建Grafana仪表板
        grafana_dashboard = '''
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [],
  "schemaVersion": 27,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "商户智能经营分析平台监控",
  "uid": "merchant_bi",
  "version": 0
}
'''
        
        with open('config/grafana-dashboard.json', 'w') as f:
            f.write(grafana_dashboard)
            
        logger.info('Created Grafana dashboard')
        
    except Exception as e:
        logger.error(f'Failed to setup monitoring: {str(e)}')
        sys.exit(1)
        
def install_dependencies():
    """安装项目依赖"""
    try:
        subprocess.run(
            ['pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        logger.info('Installed dependencies')
        
    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to install dependencies: {str(e)}')
        sys.exit(1)
        
def main():
    """主函数"""
    logger.info('Starting project setup...')
    
    # 创建目录结构
    create_directory_structure()
    
    # 安装依赖
    install_dependencies()
    
    # 设置数据库
    setup_mongodb()
    setup_redis()
    setup_rabbitmq()
    
    # 设置监控
    setup_monitoring()
    
    logger.info('Project setup completed successfully')
    
if __name__ == '__main__':
    main() 