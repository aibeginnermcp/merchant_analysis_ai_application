"""
成本穿透分析报告生成器模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class CostAnalysisReportGenerator:
    """
    成本穿透分析报告生成器
    
    负责生成：
    1. 各品类成本策略分析
    2. 成本构成分析
    3. 风险分析报告
    4. 优化建议
    """
    
    def __init__(self):
        """初始化成本分析报告生成器"""
        # 品类配置
        self.category_config = {
            '3C': {
                'logistics_rate': 5.0,  # 元/kg
                'bom_components': ['电芯', '外壳', '电路板'],
                'labor_cost_range': (8, 15),  # 元/件
                # 行业平均水平
                'industry_avg': {
                    'logistics_ratio': 25.0,  # 物流成本占比
                    'production_ratio': 55.0,  # 生产成本占比
                    'labor_ratio': 20.0,      # 人工成本占比
                    'avg_logistics_cost': 15.0,  # 平均物流成本
                    'avg_production_cost': 35.0, # 平均生产成本
                    'avg_labor_cost': 12.0,     # 平均人工成本
                },
                # 成本水位线
                'cost_threshold': {
                    'logistics': {'low': 10.0, 'high': 20.0},
                    'production': {'low': 25.0, 'high': 40.0},
                    'labor': {'low': 8.0, 'high': 15.0}
                }
            },
            '服饰': {
                'storage_rate': 80.0,  # 元/m³/月
                'labor_cost': {
                    'basic': 1.0,
                    'custom': 5.0
                },
                'industry_avg': {
                    'logistics_ratio': 8.0,
                    'production_ratio': 82.0,
                    'labor_ratio': 10.0,
                    'avg_logistics_cost': 3.0,
                    'avg_production_cost': 32.0,
                    'avg_labor_cost': 4.0,
                },
                'cost_threshold': {
                    'logistics': {'low': 2.0, 'high': 5.0},
                    'production': {'low': 25.0, 'high': 45.0},
                    'labor': {'low': 2.0, 'high': 6.0}
                }
            },
            '食品': {
                'cold_chain_rate': 0.03,  # 元/kg/km
                'spoilage_rates': {
                    7: 0.10,   # 7天内损耗率
                    30: 0.05,  # 7-30天损耗率
                    9999: 0.02 # 30天以上损耗率
                },
                'industry_avg': {
                    'logistics_ratio': 75.0,
                    'production_ratio': 18.0,
                    'labor_ratio': 7.0,
                    'avg_logistics_cost': 85.0,
                    'avg_production_cost': 18.0,
                    'avg_labor_cost': 6.0,
                },
                'cost_threshold': {
                    'logistics': {'low': 70.0, 'high': 100.0},
                    'production': {'low': 12.0, 'high': 25.0},
                    'labor': {'low': 4.0, 'high': 8.0}
                }
            },
            '家居': {
                'transport_rate': 120.0,  # 元/m³
                'material_cost': {
                    'wood': 15.0,
                    'board': 8.0
                },
                'industry_avg': {
                    'logistics_ratio': 70.0,
                    'production_ratio': 20.0,
                    'labor_ratio': 10.0,
                    'avg_logistics_cost': 120.0,
                    'avg_production_cost': 25.0,
                    'avg_labor_cost': 12.0,
                },
                'cost_threshold': {
                    'logistics': {'low': 100.0, 'high': 150.0},
                    'production': {'low': 20.0, 'high': 30.0},
                    'labor': {'low': 8.0, 'high': 15.0}
                }
            }
        }
        
        # 成本差异阈值配置
        self.threshold_config = {
            'ratio_threshold': 5.0,    # 成本占比差异阈值（百分比）
            'cost_threshold': 3.0      # 平均成本差异阈值（元/件）
        }
        
    def analyze_category_cost_strategy(self, df: pd.DataFrame, category: str) -> Dict:
        """
        分析特定品类的成本策略
        
        Args:
            df: 成本数据
            category: 品类名称
            
        Returns:
            Dict: 成本策略分析结果
        """
        category_data = df[df['category'] == category]
        
        # 计算各项成本
        total_logistics = category_data['logistics_cost'].sum()
        total_production = category_data['production_cost'].sum()
        total_labor = category_data['labor_cost'].sum()
        total_cost = total_logistics + total_production + total_labor
        
        # 计算成本占比
        cost_ratio = {
            'logistics_ratio': total_logistics / total_cost * 100,
            'production_ratio': total_production / total_cost * 100,
            'labor_ratio': total_labor / total_cost * 100
        }
        
        # 计算平均成本
        avg_costs = {
            'avg_logistics': category_data['logistics_cost'].mean(),
            'avg_production': category_data['production_cost'].mean(),
            'avg_labor': category_data['labor_cost'].mean()
        }
        
        # 获取品类特定属性
        specific_attrs = self._get_category_specific_attributes(category_data, category)
        
        # 对比行业平均水平
        industry_comparison = self._compare_with_industry_avg(category, cost_ratio, avg_costs)
        
        # 分析成本水位
        cost_level = self._analyze_cost_level(category, cost_ratio, avg_costs, industry_comparison)
        
        return {
            'cost_ratio': cost_ratio,
            'avg_costs': avg_costs,
            'specific_attrs': specific_attrs,
            'total_cost': total_cost,
            'cost_level': cost_level,
            'industry_comparison': industry_comparison
        }
    
    def _analyze_cost_level(self, category: str, cost_ratio: Dict, avg_costs: Dict, industry_comparison: Dict) -> Dict:
        """
        分析成本水位
        
        Args:
            category: 品类名称
            cost_ratio: 成本占比数据
            avg_costs: 平均成本数据
            industry_comparison: 行业对比数据
        
        Returns:
            Dict: 成本水位判断结果
        """
        levels = {}
        ratio_threshold = self.threshold_config['ratio_threshold']
        cost_threshold = self.threshold_config['cost_threshold']
        
        # 基于成本占比差异和平均成本差异综合判断
        for cost_type in ['logistics', 'production', 'labor']:
            ratio_type = f'{cost_type}_ratio'
            cost_type_full = f'avg_{cost_type}_cost'
            
            ratio_diff = abs(industry_comparison['ratio_diff'][ratio_type])
            cost_diff = abs(industry_comparison['cost_diff'][cost_type_full])
            
            if ratio_diff <= ratio_threshold and cost_diff <= cost_threshold:
                levels[cost_type] = '处于行业正常水平'
            else:
                if industry_comparison['ratio_diff'][ratio_type] > ratio_threshold or \
                   industry_comparison['cost_diff'][cost_type_full] > cost_threshold:
                    levels[cost_type] = '高于行业水平'
                else:
                    levels[cost_type] = '低于行业水平'
                    
        return levels
    
    def _compare_with_industry_avg(self, category: str, cost_ratio: Dict, avg_costs: Dict) -> Dict:
        """与行业平均水平对比"""
        industry_avg = self.category_config[category]['industry_avg']
        comparison = {
            'ratio_diff': {},
            'cost_diff': {}
        }
        
        # 计算成本占比差异
        for ratio_type in ['logistics_ratio', 'production_ratio', 'labor_ratio']:
            comparison['ratio_diff'][ratio_type] = cost_ratio[ratio_type] - industry_avg[ratio_type]
            
        # 计算平均成本差异
        for cost_type in ['avg_logistics_cost', 'avg_production_cost', 'avg_labor_cost']:
            actual_cost = avg_costs[cost_type.replace('_cost', '')]
            comparison['cost_diff'][cost_type] = actual_cost - industry_avg[cost_type]
            
        return comparison
    
    def _get_category_specific_attributes(self, df: pd.DataFrame, category: str) -> Dict:
        """获取品类特定属性"""
        attrs = {}
        
        if category == '3C':
            attrs['bom_coverage'] = df['bom_components'].notna().mean() * 100
        elif category == '服饰':
            complexity_dist = df['complexity'].value_counts(normalize=True) * 100
            attrs['complexity_distribution'] = complexity_dist.to_dict()
        elif category == '食品':
            attrs['shelf_life_stats'] = {
                'mean': df['shelf_life'].mean(),
                'min': df['shelf_life'].min(),
                'max': df['shelf_life'].max()
            }
        elif category == '家居':
            material_dist = df['material_type'].value_counts(normalize=True) * 100
            attrs['material_distribution'] = material_dist.to_dict()
            
        return attrs
    
    def analyze_risks(self, df: pd.DataFrame) -> Dict:
        """分析成本相关风险"""
        risks = {
            'supply_chain_risks': self._analyze_supply_chain_risks(df),
            'cost_structure_risks': self._analyze_cost_structure_risks(df),
            'operational_risks': self._analyze_operational_risks(df),
            'market_risks': self._analyze_market_risks(df)
        }
        return risks
    
    def _analyze_supply_chain_risks(self, df: pd.DataFrame) -> List[Dict]:
        """分析供应链风险"""
        risks = []
        
        # 3C类供应链风险
        if len(df[df['category'] == '3C']) > 0:
            risks.append({
                'category': '3C',
                'risk_type': '供应链',
                'description': '核心电子元器件供应依赖度高',
                'severity': 'high'
            })
            
        # 其他品类的供应链风险分析...
        return risks
    
    def _analyze_cost_structure_risks(self, df: pd.DataFrame) -> List[Dict]:
        """分析成本结构风险"""
        risks = []
        
        for category in df['category'].unique():
            cat_data = df[df['category'] == category]
            total_cost = cat_data['logistics_cost'].sum() + cat_data['production_cost'].sum() + cat_data['labor_cost'].sum()
            logistics_ratio = cat_data['logistics_cost'].sum() / total_cost * 100
            
            if logistics_ratio > 75:
                risks.append({
                    'category': category,
                    'risk_type': '成本结构',
                    'description': f'物流成本占比过高({logistics_ratio:.1f}%)',
                    'severity': 'high'
                })
                
        return risks
    
    def _analyze_operational_risks(self, df: pd.DataFrame) -> List[Dict]:
        """分析运营风险"""
        risks = []
        
        # 食品类运营风险
        food_data = df[df['category'] == '食品']
        if len(food_data) > 0:
            short_shelf_life = food_data['shelf_life'] < 7
            if short_shelf_life.any():
                risks.append({
                    'category': '食品',
                    'risk_type': '运营',
                    'description': '短保质期商品占比较高',
                    'severity': 'medium'
                })
                
        return risks
    
    def _analyze_market_risks(self, df: pd.DataFrame) -> List[Dict]:
        """分析市场风险"""
        risks = []
        
        # 各品类市场风险分析
        for category in df['category'].unique():
            if category == '3C':
                risks.append({
                    'category': category,
                    'risk_type': '市场',
                    'description': '产品更新换代快，库存贬值风险高',
                    'severity': 'high'
                })
                
        return risks
    
    def generate_optimization_suggestions(self, risks: Dict) -> Dict:
        """生成优化建议"""
        suggestions = {
            'short_term': [],
            'mid_long_term': [],
            'strategic': []
        }
        
        # 基于风险生成建议
        for risk_type, risk_list in risks.items():
            for risk in risk_list:
                if risk['severity'] == 'high':
                    suggestions['short_term'].append({
                        'category': risk['category'],
                        'suggestion': self._get_risk_mitigation_suggestion(risk)
                    })
                    
        # 添加通用优化建议
        suggestions['short_term'].extend([
            {'category': 'all', 'suggestion': '优化配送路径，提高物流效率'},
            {'category': 'all', 'suggestion': '加强库存周转管理'}
        ])
        
        suggestions['mid_long_term'].extend([
            {'category': 'all', 'suggestion': '建设区域仓储网络'},
            {'category': 'all', 'suggestion': '发展智能制造能力'}
        ])
        
        suggestions['strategic'].extend([
            {'category': 'all', 'suggestion': '推进供应链数字化转型'},
            {'category': 'all', 'suggestion': '建立柔性生产体系'}
        ])
        
        return suggestions
    
    def _get_risk_mitigation_suggestion(self, risk: Dict) -> str:
        """根据风险生成具体的缓解建议"""
        suggestions = {
            ('3C', '供应链'): '建立核心组件多供应商体系',
            ('食品', '运营'): '优化保质期管理流程',
            ('服饰', '成本结构'): '提高生产自动化水平',
            ('家居', '市场'): '开发模块化产品设计'
        }
        
        return suggestions.get((risk['category'], risk['risk_type']), '制定详细的风险应对方案')
    
    def generate_report(self, df: pd.DataFrame, output_path: str):
        """
        生成完整的成本穿透分析报告
        
        Args:
            df: 成本数据
            output_path: 报告输出路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'{output_path}/cost_analysis_report_{timestamp}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            # 写入报告头部
            f.write('# 成本穿透分析报告\n\n')
            f.write(f'生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
            
            # 写入成本水位判断标准说明
            f.write('## 成本水位判断标准\n\n')
            f.write('本报告采用以下标准判断成本水位：\n')
            f.write(f'1. 成本占比差异在±{self.threshold_config["ratio_threshold"]}%以内，且\n')
            f.write(f'2. 平均成本差异在±{self.threshold_config["cost_threshold"]}元/件以内\n')
            f.write('同时满足以上条件时，判定为"处于行业正常水平"，否则根据差异方向判定为"高于行业水平"或"低于行业水平"\n\n')
            
            # 写入异常成本项汇总
            abnormal_costs = self._collect_abnormal_costs(df)
            if abnormal_costs:
                f.write('## 异常成本项汇总\n\n')
                for category, items in abnormal_costs.items():
                    f.write(f'### {category}类\n')
                    for item in items:
                        f.write(f'- {item["cost_type"]}成本{item["level"]}\n')
                        f.write(f'  - 成本占比差异：{item["ratio_diff"]:+.1f}%\n')
                        f.write(f'  - 平均成本差异：{item["cost_diff"]:+.2f}元/件\n')
                f.write('\n')
            
            # 写入各品类成本策略分析
            f.write('\n## 品类成本策略分析\n\n')
            for category in df['category'].unique():
                analysis_result = self.analyze_category_cost_strategy(df, category)
                self._write_category_analysis(f, category, analysis_result)
            
            # 写入风险分析
            f.write('\n## 风险分析\n\n')
            risks = self.analyze_risks(df)
            self._write_risk_analysis(f, risks)
            
            # 写入优化建议
            f.write('\n## 优化建议\n\n')
            suggestions = self.generate_optimization_suggestions(risks)
            self._write_optimization_suggestions(f, suggestions)
            
        print(f'成本穿透分析报告已生成：{report_file}')
        
    def _write_category_analysis(self, f, category: str, analysis: Dict):
        """写入品类分析结果"""
        f.write(f'### {category}类产品成本分析\n\n')
        
        # 写入成本比例
        f.write('#### 成本构成\n')
        f.write(f'- 物流成本占比：{analysis["cost_ratio"]["logistics_ratio"]:.1f}%\n')
        f.write(f'- 生产成本占比：{analysis["cost_ratio"]["production_ratio"]:.1f}%\n')
        f.write(f'- 人工成本占比：{analysis["cost_ratio"]["labor_ratio"]:.1f}%\n\n')
        
        # 写入行业平均水平对比
        f.write('#### 行业平均水平对比\n')
        industry_avg = self.category_config[category]['industry_avg']
        f.write('成本占比对比：\n')
        for ratio_type in ['logistics_ratio', 'production_ratio', 'labor_ratio']:
            diff = analysis['industry_comparison']['ratio_diff'][ratio_type]
            ratio_name = {'logistics_ratio': '物流', 'production_ratio': '生产', 'labor_ratio': '人工'}[ratio_type]
            f.write(f'- {ratio_name}成本占比：{industry_avg[ratio_type]:.1f}% (差异：{diff:+.1f}%)\n')
        
        f.write('\n平均成本对比：\n')
        for cost_type in ['avg_logistics_cost', 'avg_production_cost', 'avg_labor_cost']:
            diff = analysis['industry_comparison']['cost_diff'][cost_type]
            cost_name = {'avg_logistics_cost': '物流', 'avg_production_cost': '生产', 'avg_labor_cost': '人工'}[cost_type]
            f.write(f'- {cost_name}平均成本：{industry_avg[cost_type]:.2f}元/件 (差异：{diff:+.2f}元/件)\n')
        f.write('\n')
        
        # 写入成本水位判断
        f.write('#### 成本水位判断\n')
        for cost_type, level in analysis['cost_level'].items():
            cost_name = {'logistics': '物流', 'production': '生产', 'labor': '人工'}[cost_type]
            f.write(f'- {cost_name}成本：{level}\n')
        f.write('\n')
        
        # 写入平均成本
        f.write('#### 平均成本\n')
        f.write(f'- 平均物流成本：{analysis["avg_costs"]["avg_logistics"]:.2f}元/件\n')
        f.write(f'- 平均生产成本：{analysis["avg_costs"]["avg_production"]:.2f}元/件\n')
        f.write(f'- 平均人工成本：{analysis["avg_costs"]["avg_labor"]:.2f}元/件\n\n')
        
        # 写入品类特定属性
        if analysis['specific_attrs']:
            f.write('#### 特定属性\n')
            for attr, value in analysis['specific_attrs'].items():
                f.write(f'- {attr}：{value}\n')
            f.write('\n')
    
    def _write_risk_analysis(self, f, risks: Dict):
        """写入风险分析结果"""
        for risk_type, risk_list in risks.items():
            f.write(f'### {risk_type}\n\n')
            for risk in risk_list:
                f.write(f'- {risk["category"]}类：{risk["description"]} (风险等级：{risk["severity"]})\n')
            f.write('\n')
    
    def _write_optimization_suggestions(self, f, suggestions: Dict):
        """写入优化建议"""
        for term, suggestion_list in suggestions.items():
            if term == 'short_term':
                f.write('### 短期优化建议\n\n')
            elif term == 'mid_long_term':
                f.write('### 中长期优化建议\n\n')
            else:
                f.write('### 战略优化建议\n\n')
                
            for suggestion in suggestion_list:
                if suggestion['category'] == 'all':
                    f.write(f'- {suggestion["suggestion"]}\n')
                else:
                    f.write(f'- {suggestion["category"]}类：{suggestion["suggestion"]}\n')
            f.write('\n')
    
    def _collect_abnormal_costs(self, df: pd.DataFrame) -> Dict:
        """收集异常成本项"""
        abnormal_costs = {}
        
        for category in df['category'].unique():
            analysis_result = self.analyze_category_cost_strategy(df, category)
            category_abnormal = []
            
            for cost_type in ['logistics', 'production', 'labor']:
                ratio_type = f'{cost_type}_ratio'
                cost_type_full = f'avg_{cost_type}_cost'
                
                if analysis_result['cost_level'][cost_type] != '处于行业正常水平':
                    category_abnormal.append({
                        'cost_type': cost_type,
                        'level': analysis_result['cost_level'][cost_type],
                        'ratio_diff': analysis_result['industry_comparison']['ratio_diff'][ratio_type],
                        'cost_diff': analysis_result['industry_comparison']['cost_diff'][cost_type_full]
                    })
            
            if category_abnormal:
                abnormal_costs[category] = category_abnormal
                
        return abnormal_costs 