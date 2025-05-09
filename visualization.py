#!/usr/bin/env python3
"""
商户智能分析平台 - 可视化工具

用于将分析结果转换为直观的图表和图形表示。
支持以下可视化类型：
- 现金流趋势预测图
- 成本构成饼图
- 合规风险雷达图
- 健康状况仪表盘
"""

import json
import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

def load_analysis_data(filename):
    """
    加载分析报告JSON文件
    
    Args:
        filename: 分析报告文件路径
        
    Returns:
        dict: 分析报告数据
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ 无法加载分析报告: {str(e)}")
        sys.exit(1)

def plot_cashflow_prediction(data, output_dir='.'):
    """绘制现金流预测趋势图"""
    if 'cashflow_analysis' not in data['data']:
        print("⚠️ 缺少现金流分析数据")
        return
    
    cashflow = data['data']['cashflow_analysis']
    if 'prediction' not in cashflow:
        print("⚠️ 缺少现金流预测数据")
        return
    
    prediction = cashflow['prediction']
    
    dates = [p['date'] for p in prediction]
    values = [p['value'] for p in prediction]
    lower_bounds = [p['lower_bound'] for p in prediction]
    upper_bounds = [p['upper_bound'] for p in prediction]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, 'b-', label='预测值')
    plt.fill_between(dates, lower_bounds, upper_bounds, color='b', alpha=0.2, label='95%置信区间')
    
    plt.title('现金流预测')
    plt.xlabel('日期')
    plt.ylabel('金额')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'cashflow_prediction.png'), dpi=300)
    plt.close()
    print("✅ 现金流预测图已保存")

def plot_cost_breakdown(data, output_dir='.'):
    """绘制成本构成饼图"""
    if 'cost_analysis' not in data['data']:
        print("⚠️ 缺少成本分析数据")
        return
    
    cost = data['data']['cost_analysis']
    if 'cost_breakdown' not in cost:
        print("⚠️ 缺少成本构成数据")
        return
    
    breakdown = cost['cost_breakdown']
    
    labels = [item['category'] for item in breakdown]
    sizes = [item['percentage'] for item in breakdown]
    
    # 映射类别名称
    category_map = {
        'labor': '人力成本',
        'raw_material': '原材料',
        'utilities': '水电费',
        'rent': '租金',
        'marketing': '营销费用'
    }
    
    # 翻译类别名称
    labels = [category_map.get(label, label) for label in labels]
    
    # 自定义颜色
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
    
    # 突出显示最大的成本项
    explode = [0.1 if s == max(sizes) else 0 for s in sizes]
    
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    plt.axis('equal')  # 确保饼图是圆形的
    plt.title('成本构成分析')
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'cost_breakdown.png'), dpi=300)
    plt.close()
    print("✅ 成本构成图已保存")

def radar_factory(num_vars, frame='circle'):
    """创建雷达图工厂函数"""
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    
    class RadarAxes(PolarAxes):
        name = 'radar'
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')
            
        def fill(self, *args, **kwargs):
            return super().fill_between(theta, *args, **kwargs)
            
        def plot(self, *args, **kwargs):
            lines = super().plot(theta, *args, **kwargs)
            return lines
            
        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)
            
        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars, radius=0.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)
                
        def draw(self, renderer):
            if frame == 'circle':
                patch = Circle((0.5, 0.5), 0.5)
                patch.set_transform(self.transAxes)
                patch.set_clip_on(False)
                patch.set_edgecolor('black')
                patch.set_facecolor('white')
                patch.set_alpha(0.0)
                self.add_patch(patch)
                
            elif frame == 'polygon':
                patch = RegularPolygon((0.5, 0.5), num_vars, radius=0.5)
                patch.set_transform(self.transAxes)
                patch.set_clip_on(False)
                patch.set_edgecolor('black')
                patch.set_facecolor('white')
                patch.set_alpha(0.0)
                self.add_patch(patch)
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)
                
            super().draw(renderer)
                
    register_projection(RadarAxes)
    return theta

def plot_compliance_radar(data, output_dir='.'):
    """绘制合规风险雷达图"""
    if 'compliance_analysis' not in data['data']:
        print("⚠️ 缺少合规分析数据")
        return
    
    compliance = data['data']['compliance_analysis']
    if 'type_status' not in compliance:
        print("⚠️ 缺少合规类型状态数据")
        return
    
    type_status = compliance['type_status']
    
    # 风险状态映射为数值
    status_map = {
        'compliant': 1.0,       # 合规
        'needs_review': 0.5,    # 需要审查
        'non_compliant': 0.0    # 不合规
    }
    
    # 类型名称映射
    type_map = {
        'tax': '税务',
        'accounting': '会计',
        'licensing': '许可证',
        'labor': '劳工'
    }
    
    # 准备雷达图数据
    categories = list(type_status.keys())
    values = [status_map[type_status[cat]] for cat in categories]
    
    # 翻译类别名称
    categories = [type_map.get(cat, cat) for cat in categories]
    
    N = len(categories)
    
    # 创建雷达图
    theta = radar_factory(N, frame='polygon')
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='radar'))
    
    # 画出刻度
    ax.set_ylim(0, 1)
    ax.set_rgrids([0.25, 0.5, 0.75], ['高风险', '中等风险', '低风险'])
    
    # 绘制数据
    ax.plot(values, 'o-', linewidth=2, color='b')
    ax.fill(values, alpha=0.25, color='b')
    
    # 设置标签
    ax.set_varlabels(categories)
    
    plt.title('合规风险分析', pad=20)
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'compliance_radar.png'), dpi=300)
    plt.close()
    print("✅ 合规风险雷达图已保存")

def plot_health_gauge(data, output_dir='.'):
    """绘制健康状况仪表盘"""
    if 'summary' not in data['data']:
        print("⚠️ 缺少摘要数据")
        return
    
    summary = data['data']['summary']
    if 'health_score' not in summary:
        print("⚠️ 缺少健康评分数据")
        return
    
    health_score = summary['health_score']
    
    # 创建仪表盘图
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(polar=True))
    
    # 设置仪表盘范围
    theta = np.linspace(0, np.pi, 100)
    r = np.ones_like(theta)
    
    # 背景分区
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(0, 100)
    
    # 危险、警告和良好区域
    danger = np.linspace(0, np.pi/3, 34)
    warning = np.linspace(np.pi/3, 2*np.pi/3, 34)
    good = np.linspace(2*np.pi/3, np.pi, 34)
    
    ax.fill_between(danger, 0, 1, color='#ffcccc', alpha=0.3)
    ax.fill_between(warning, 0, 1, color='#ffffcc', alpha=0.3)
    ax.fill_between(good, 0, 1, color='#ccffcc', alpha=0.3)
    
    # 计算指针角度
    angle = np.pi * health_score / 100
    
    # 绘制指针
    ax.plot([0, angle], [0, 0.8], 'r-', lw=4)
    ax.plot([0, 0], [0, 0], 'ko', ms=10)
    
    # 设置刻度
    ax.set_rticks([])
    ax.set_xticks([0, np.pi/6, np.pi/3, np.pi/2, 2*np.pi/3, 5*np.pi/6, np.pi])
    ax.set_xticklabels(['0', '', '30', '50', '70', '', '100'])
    
    # 隐藏网格和脊柱
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.title(f'商户健康评分: {health_score}/100', y=0.1)
    
    # 添加健康状态描述
    if health_score < 30:
        status = "危险"
        color = 'red'
    elif 30 <= health_score < 70:
        status = "需要注意"
        color = 'orange'
    else:
        status = "健康"
        color = 'green'
        
    plt.figtext(0.5, 0.25, f"状态: {status}", fontsize=14, ha='center', color=color)
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(output_dir, 'health_gauge.png'), dpi=300)
    plt.close()
    print("✅ 健康评分仪表盘已保存")

def create_summary_dashboard(data, output_dir='.'):
    """创建综合分析仪表板"""
    # 创建2x2网格的图表
    fig = plt.figure(figsize=(20, 16))
    
    # 1. 健康评分仪表盘
    if 'summary' in data['data'] and 'health_score' in data['data']['summary']:
        health_score = data['data']['summary']['health_score']
        
        ax1 = fig.add_subplot(221, polar=True)
        
        # 设置仪表盘范围
        theta = np.linspace(0, np.pi, 100)
        
        # 危险、警告和良好区域
        danger = np.linspace(0, np.pi/3, 34)
        warning = np.linspace(np.pi/3, 2*np.pi/3, 34)
        good = np.linspace(2*np.pi/3, np.pi, 34)
        
        ax1.fill_between(danger, 0, 1, color='#ffcccc', alpha=0.3)
        ax1.fill_between(warning, 0, 1, color='#ffffcc', alpha=0.3)
        ax1.fill_between(good, 0, 1, color='#ccffcc', alpha=0.3)
        
        # 计算指针角度
        angle = np.pi * health_score / 100
        
        # 绘制指针
        ax1.plot([0, angle], [0, 0.8], 'r-', lw=4)
        ax1.plot([0, 0], [0, 0], 'ko', ms=10)
        
        # 设置刻度
        ax1.set_rticks([])
        ax1.set_xticks([0, np.pi/6, np.pi/3, np.pi/2, 2*np.pi/3, 5*np.pi/6, np.pi])
        ax1.set_xticklabels(['0', '', '30', '50', '70', '', '100'])
        
        # 隐藏网格和脊柱
        ax1.grid(False)
        for spine in ax1.spines.values():
            spine.set_visible(False)
        
        ax1.set_title('商户健康评分', fontsize=16)
        
        # 添加健康状态描述
        if health_score < 30:
            status = "危险"
            color = 'red'
        elif 30 <= health_score < 70:
            status = "需要注意"
            color = 'orange'
        else:
            status = "健康"
            color = 'green'
            
        ax1.text(np.pi/2, -0.15, f"{health_score}/100 ({status})", 
                 fontsize=14, ha='center', color=color, transform=ax1.transAxes)
    
    # 2. 现金流预测趋势图
    if ('cashflow_analysis' in data['data'] and 
        'prediction' in data['data']['cashflow_analysis']):
        
        prediction = data['data']['cashflow_analysis']['prediction']
        
        ax2 = fig.add_subplot(222)
        
        dates = [p['date'] for p in prediction]
        values = [p['value'] for p in prediction]
        lower_bounds = [p['lower_bound'] for p in prediction]
        upper_bounds = [p['upper_bound'] for p in prediction]
        
        ax2.plot(dates, values, 'b-', label='预测值')
        ax2.fill_between(dates, lower_bounds, upper_bounds, color='b', alpha=0.2, label='95%置信区间')
        
        ax2.set_title('现金流预测', fontsize=16)
        ax2.set_xlabel('日期')
        ax2.set_ylabel('金额')
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend()
    
    # 3. 成本构成饼图
    if ('cost_analysis' in data['data'] and 
        'cost_breakdown' in data['data']['cost_analysis']):
        
        breakdown = data['data']['cost_analysis']['cost_breakdown']
        
        ax3 = fig.add_subplot(223)
        
        labels = [item['category'] for item in breakdown]
        sizes = [item['percentage'] for item in breakdown]
        
        # 映射类别名称
        category_map = {
            'labor': '人力成本',
            'raw_material': '原材料',
            'utilities': '水电费',
            'rent': '租金',
            'marketing': '营销费用'
        }
        
        # 翻译类别名称
        labels = [category_map.get(label, label) for label in labels]
        
        # 自定义颜色
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
        
        # 突出显示最大的成本项
        explode = [0.1 if s == max(sizes) else 0 for s in sizes]
        
        ax3.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax3.axis('equal')  # 确保饼图是圆形的
        ax3.set_title('成本构成分析', fontsize=16)
    
    # 4. 合规风险雷达图
    if ('compliance_analysis' in data['data'] and 
        'type_status' in data['data']['compliance_analysis']):
        
        type_status = data['data']['compliance_analysis']['type_status']
        
        # 风险状态映射为数值
        status_map = {
            'compliant': 1.0,       # 合规
            'needs_review': 0.5,    # 需要审查
            'non_compliant': 0.0    # 不合规
        }
        
        # 类型名称映射
        type_map = {
            'tax': '税务',
            'accounting': '会计',
            'licensing': '许可证',
            'labor': '劳工'
        }
        
        # 准备雷达图数据
        categories = list(type_status.keys())
        values = [status_map[type_status[cat]] for cat in categories]
        
        # 翻译类别名称
        categories = [type_map.get(cat, cat) for cat in categories]
        
        N = len(categories)
        
        # 创建雷达图
        theta = radar_factory(N, frame='polygon')
        
        ax4 = fig.add_subplot(224, projection='radar')
        
        # 画出刻度
        ax4.set_ylim(0, 1)
        ax4.set_rgrids([0.25, 0.5, 0.75], ['高风险', '中等风险', '低风险'])
        
        # 绘制数据
        ax4.plot(values, 'o-', linewidth=2, color='b')
        ax4.fill(values, alpha=0.25, color='b')
        
        # 设置标签
        ax4.set_varlabels(categories)
        
        ax4.set_title('合规风险分析', fontsize=16)
    
    # 添加主标题
    merchant_id = data['data']['merchant_id']
    report_date = datetime.now().strftime('%Y-%m-%d')
    plt.suptitle(f'商户 {merchant_id} 经营分析报告 ({report_date})', fontsize=20, y=0.98)
    
    # 添加脚注
    plt.figtext(0.5, 0.01, '由商户智能分析平台生成', fontsize=10, ha='center', 
               style='italic', bbox={'facecolor': 'lightgrey', 'alpha': 0.5, 'pad': 5})
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    plt.savefig(os.path.join(output_dir, 'analysis_dashboard.png'), dpi=300)
    plt.close()
    print("✅ 综合分析仪表板已保存")

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python visualization.py <分析报告JSON文件> [输出目录]")
        sys.exit(1)
    
    # 获取文件路径和输出目录
    report_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else '.'
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"加载分析报告: {report_file}")
    data = load_analysis_data(report_file)
    
    # 绘制各种图表
    print("\n开始生成可视化图表...")
    
    plot_cashflow_prediction(data, output_dir)
    plot_cost_breakdown(data, output_dir)
    plot_compliance_radar(data, output_dir)
    plot_health_gauge(data, output_dir)
    create_summary_dashboard(data, output_dir)
    
    print(f"\n✅ 所有图表已保存到: {output_dir}")
    print(f"1. 现金流预测图: {os.path.join(output_dir, 'cashflow_prediction.png')}")
    print(f"2. 成本构成图: {os.path.join(output_dir, 'cost_breakdown.png')}")
    print(f"3. 合规风险雷达图: {os.path.join(output_dir, 'compliance_radar.png')}")
    print(f"4. 健康评分仪表盘: {os.path.join(output_dir, 'health_gauge.png')}")
    print(f"5. 综合分析仪表板: {os.path.join(output_dir, 'analysis_dashboard.png')}")

if __name__ == '__main__':
    main() 