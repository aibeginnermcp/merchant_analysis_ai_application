#!/usr/bin/env python3
"""
商户智能分析平台 - 文本报告生成器

从分析结果JSON生成HTML格式的经营分析报告。
可以通过命令行运行，将分析结果转换为美观的HTML报告。
"""

import json
import os
import sys
from datetime import datetime

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

def generate_html_report(data, output_file):
    """
    生成HTML格式的经营分析报告
    
    Args:
        data: 分析报告数据
        output_file: 输出文件路径
    """
    # 提取基本信息
    merchant_id = data['data']['merchant_id']
    report_id = data['data']['report_id']
    time_range = data['data']['time_range']
    
    # 获取摘要信息
    summary = data['data']['summary']
    health_score = summary['health_score']
    revenue_trend = summary['revenue_trend']
    cost_efficiency = summary['cost_efficiency']
    compliance_status = summary['compliance_status']
    cash_position = summary['cash_position']
    
    # 趋势映射为中文
    trend_map = {
        'increasing': '上升',
        'decreasing': '下降',
        'stable': '稳定',
        'fluctuating': '波动'
    }
    
    # 效率映射为中文
    efficiency_map = {
        'high': '高',
        'moderate': '中等',
        'low': '低'
    }
    
    # 状态映射为中文
    status_map = {
        'compliant': '合规',
        'needs_review': '需要审查',
        'non_compliant': '不合规',
        'healthy': '健康',
        'at_risk': '风险',
        'critical': '危急'
    }
    
    # 现金流预测数据
    cashflow_prediction = data['data']['cashflow_analysis']['prediction']
    cashflow_metrics = data['data']['cashflow_analysis']['metrics']
    
    # 成本分析数据
    cost_breakdown = data['data']['cost_analysis']['cost_breakdown']
    total_cost = data['data']['cost_analysis']['total_cost']
    
    # 成本类别映射为中文
    cost_category_map = {
        'labor': '人力成本',
        'raw_material': '原材料',
        'utilities': '水电费',
        'rent': '租金',
        'marketing': '营销费用'
    }
    
    # 合规分析数据
    compliance_analysis = data['data']['compliance_analysis']
    
    # 综合洞察
    insights = data['data']['integrated_insights']
    
    # 开始生成HTML
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>商户 {merchant_id} 经营分析报告</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        header {{
            background-color: #3c3cb4;
            color: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 5px;
        }}
        h1, h2, h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        header h1 {{
            color: white;
            margin: 0;
        }}
        .report-meta {{
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            color: rgba(255,255,255,0.9);
            font-size: 14px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 20px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .highlight {{
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3c3cb4;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
        }}
        .score-container {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            color: #3c3cb4;
        }}
        .score-label {{
            font-size: 14px;
            color: #666;
        }}
        .insight-card {{
            background-color: #fff;
            border-left: 4px solid #3c3cb4;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .positive {{
            border-left-color: #28a745;
        }}
        .negative {{
            border-left-color: #dc3545;
        }}
        .attention_needed {{
            border-left-color: #ffc107;
        }}
        .insight-title {{
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }}
        .insight-category {{
            background-color: #eee;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            color: #666;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #888;
            font-size: 14px;
        }}
        .footer a {{
            color: #3c3cb4;
            text-decoration: none;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            grid-gap: 15px;
            margin: 20px 0;
        }}
        .metric-box {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #3c3cb4;
            margin-bottom: 5px;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        .status-compliant {{
            background-color: #28a745;
        }}
        .status-needs_review {{
            background-color: #ffc107;
            color: #212529;
        }}
        .status-non_compliant {{
            background-color: #dc3545;
        }}
        .data-source-section {{
            background-color: #f5f7fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border: 1px solid #e2e8f0;
        }}
        .data-source-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #3c3cb4;
        }}
        .data-source-link {{
            display: inline-block;
            margin-top: 10px;
            color: #3c3cb4;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>商户经营分析报告</h1>
            <div class="report-meta">
                <div>商户ID: {merchant_id}</div>
                <div>报告ID: {report_id}</div>
                <div>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
            </div>
        </header>
        
        <div class="section">
            <h2>运营状况概览</h2>
            <div class="score-container">
                <div class="score">{health_score}</div>
                <div class="score-label">商户健康评分 (满分100)</div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-value">{trend_map.get(revenue_trend, revenue_trend)}</div>
                    <div class="metric-label">收入趋势</div>
                </div>
                
                <div class="metric-box">
                    <div class="metric-value">{efficiency_map.get(cost_efficiency, cost_efficiency)}</div>
                    <div class="metric-label">成本效率</div>
                </div>
                
                <div class="metric-box">
                    <div class="metric-value">{status_map.get(compliance_status, compliance_status)}</div>
                    <div class="metric-label">合规状态</div>
                </div>
                
                <div class="metric-box">
                    <div class="metric-value">{status_map.get(cash_position, cash_position)}</div>
                    <div class="metric-label">现金状况</div>
                </div>
            </div>
            
            <div class="highlight">
                <p>分析周期: {time_range['start_date']} 至 {time_range['end_date']}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>关键洞察</h2>
"""
    
    # 添加洞察卡片
    for insight in insights:
        category = insight['category']
        trend = insight['trend']
        insight_text = insight['insight']
        recommendation = insight['recommendation']
        
        # 映射类别到中文
        category_map = {
            'profitability': '盈利能力',
            'risk_management': '风险管理',
            'operational_efficiency': '运营效率',
            'growth': '增长',
            'customer': '客户',
            'market': '市场'
        }
        
        # 趋势对应的样式类
        trend_class = trend
        
        # 类别的中文名称
        category_zh = category_map.get(category, category)
        
        html += f"""
            <div class="insight-card {trend_class}">
                <div class="insight-title">
                    <span>{category_zh}</span>
                    <span class="insight-category">{trend}</span>
                </div>
                <p><strong>洞察:</strong> {insight_text}</p>
                <p><strong>建议:</strong> {recommendation}</p>
            </div>
"""
    
    html += """
        </div>
        
        <div class="section">
            <h2>现金流分析</h2>
"""
    
    # 现金流预测表格
    html += """
            <h3>未来现金流预测</h3>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>预测值</th>
                        <th>下限 (95%置信区间)</th>
                        <th>上限 (95%置信区间)</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # 只显示前5天的预测数据
    for pred in cashflow_prediction[:5]:
        html += f"""
                    <tr>
                        <td>{pred['date']}</td>
                        <td>{pred['value']:.2f}</td>
                        <td>{pred['lower_bound']:.2f}</td>
                        <td>{pred['upper_bound']:.2f}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
            
            <h3>预测模型指标</h3>
            <div class="metrics-grid">
"""
    
    # 添加预测模型指标
    for metric, value in cashflow_metrics.items():
        if metric == 'parameters':
            continue
            
        if metric == 'model_type':
            html += f"""
                <div class="metric-box">
                    <div class="metric-value">{value.upper()}</div>
                    <div class="metric-label">模型类型</div>
                </div>
"""
        else:
            html += f"""
                <div class="metric-box">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{metric.upper()}</div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>成本分析</h2>
            <div class="highlight">
                <p>总成本: <strong>¥ {:.2f}</strong></p>
            </div>
            
            <h3>成本构成</h3>
            <table>
                <thead>
                    <tr>
                        <th>类别</th>
                        <th>金额 (¥)</th>
                        <th>占比</th>
                    </tr>
                </thead>
                <tbody>
""".format(total_cost)
    
    # 成本构成表格
    for item in cost_breakdown:
        category = item['category']
        amount = item['amount']
        percentage = item['percentage']
        
        # 中文类别名称
        category_zh = cost_category_map.get(category, category)
        
        html += f"""
                    <tr>
                        <td>{category_zh}</td>
                        <td>{amount:.2f}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>合规分析</h2>
            <div class="highlight">
                <p>合规风险评分: <strong>{:.1f}</strong> (低风险区间: 0-30, 中等风险区间: 30-60, 高风险区间: 60-100)</p>
            </div>
            
            <h3>合规状态</h3>
            <table>
                <thead>
                    <tr>
                        <th>合规类别</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
""".format(compliance_analysis['risk_score'])
    
    # 合规状态表格
    for category, status in compliance_analysis['type_status'].items():
        # 类别的中文名称
        if category == 'tax':
            category_zh = '税务'
        elif category == 'accounting':
            category_zh = '会计'
        elif category == 'licensing':
            category_zh = '许可证'
        elif category == 'labor':
            category_zh = '劳工'
        else:
            category_zh = category
            
        # 状态的中文名称
        status_zh = status_map.get(status, status)
            
        html += f"""
                    <tr>
                        <td>{category_zh}</td>
                        <td><span class="status-badge status-{status}">{status_zh}</span></td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>数据参考</h2>
            <div class="data-source-section">
                <div class="data-source-title">行业模拟数据参考</div>
                <p>本分析报告使用了智能商户经营分析报表数据生成器提供的行业模拟数据，包括：</p>
                <ul>
                    <li>用户基础信息数据</li>
                    <li>交易流水数据</li>
                    <li>用户行为日志数据</li>
                    <li>NPS调研数据</li>
                    <li>成本数据</li>
                </ul>
                <p>这些数据基于不同行业特性生成，包括线上电商、线下零售等业态，可用于测试和验证分析结果。</p>
                <p>支持的商户类型：线上大型服饰电商、线上小型3C店铺、线下中型餐饮店、线下大型游乐场</p>
                <a href="../../data/merchant_sample/industry_data.json" class="data-source-link">查看完整的行业模拟数据 →</a>
            </div>
        </div>
        
        <div class="footer">
            <p>本报告由商户智能分析平台自动生成，数据更新截至 {}</p>
            <p><a href="../../services/data_simulator/DATA_README.md" target="_blank">查看数据来源说明</a></p>
            <p>&copy; 2023-{} 商户智能分析平台</p>
        </div>
    </div>
</body>
</html>
""".format(
    datetime.now().strftime('%Y-%m-%d %H:%M'),
    datetime.now().year
)
    
    # 写入HTML文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML报告已生成: {output_file}")

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python report_generator.py <分析报告JSON文件> [输出文件路径]")
        sys.exit(1)
    
    # 获取文件路径
    report_file = sys.argv[1]
    
    # 输出文件路径，默认为reports目录下的HTML文件
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # 提取文件名，替换扩展名为.html
        base_name = os.path.basename(report_file).replace('.json', '')
        output_file = f"reports/{base_name}.html"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"加载分析报告: {report_file}")
    data = load_analysis_data(report_file)
    
    print("生成HTML报告...")
    generate_html_report(data, output_file)

if __name__ == '__main__':
    main() 