"""
智能财务哨兵系统 - 报告生成器
用于生成美观的财务合规检查报告，支持中文显示、趋势分析和多维度统计
"""

import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import numpy as np

class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.report_path = Path('reports')
        self.report_path.mkdir(parents=True, exist_ok=True)
        
    def _generate_trend_chart(self, historical_data):
        """生成风险趋势图（堆叠柱状图）"""
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # 计算总数用于计算占比
        df['total'] = df['high_risk_count'] + df['medium_risk_count'] + df['low_risk_count']
        
        # 计算占比
        df['high_risk_pct'] = df['high_risk_count'] / df['total'] * 100
        df['medium_risk_pct'] = df['medium_risk_count'] / df['total'] * 100
        df['low_risk_pct'] = df['low_risk_count'] / df['total'] * 100
        
        fig = go.Figure()
        
        # 添加堆叠柱状图
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['high_risk_pct'],
            name='高风险',
            marker_color='#ff4d4d',
            hovertemplate='日期: %{x}<br>高风险占比: %{y:.1f}%<br>数量: %{text}<extra></extra>',
            text=df['high_risk_count']
        ))
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['medium_risk_pct'],
            name='中风险',
            marker_color='#ffa64d',
            hovertemplate='日期: %{x}<br>中风险占比: %{y:.1f}%<br>数量: %{text}<extra></extra>',
            text=df['medium_risk_count']
        ))
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['low_risk_pct'],
            name='低风险',
            marker_color='#66cc66',
            hovertemplate='日期: %{x}<br>低风险占比: %{y:.1f}%<br>数量: %{text}<extra></extra>',
            text=df['low_risk_count']
        ))
        
        # 设置堆叠模式
        fig.update_layout(
            barmode='stack',
            title={
                'text': '风险趋势分析（按风险等级占比）',
                'font': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei',
                    'size': 20
                }
            },
            xaxis_title={
                'text': '日期',
                'font': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                }
            },
            yaxis_title={
                'text': '占比（%）',
                'font': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                }
            },
            xaxis={
                'tickfont': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                }
            },
            yaxis={
                'tickfont': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                },
                'range': [0, 100]
            },
            hovermode='x unified'
        )
        
        return fig
    
    def _generate_department_heatmap(self, department_data):
        """生成部门风险分布热力图"""
        # 创建数据矩阵
        departments = [d['department'] for d in department_data]
        risk_levels = ['高风险', '中风险', '低风险']
        data_matrix = np.zeros((len(departments), len(risk_levels)))
        
        for i, dept in enumerate(departments):
            data_matrix[i][0] = department_data[i]['high_risk']
            data_matrix[i][1] = department_data[i]['medium_risk']
            data_matrix[i][2] = department_data[i]['low_risk']
        
        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=data_matrix,
            x=risk_levels,
            y=departments,
            colorscale=[[0, '#66cc66'], [0.5, '#ffa64d'], [1, '#ff4d4d']],
            hoverongaps=False,
            hovertemplate='部门: %{y}<br>风险等级: %{x}<br>问题数量: %{z}<extra></extra>'
        ))
        
        # 设置图表布局
        fig.update_layout(
            title={
                'text': '部门风险分布热力图',
                'font': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei',
                    'size': 20
                }
            },
            xaxis_title={
                'text': '风险等级',
                'font': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                }
            },
            yaxis_title={
                'text': '部门',
                'font': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                }
            },
            xaxis={
                'tickfont': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                }
            },
            yaxis={
                'tickfont': {
                    'family': 'Arial, PingFang SC, Microsoft YaHei, SimHei'
                }
            }
        )
        
        return fig
    
    def generate_report(self, data):
        """生成财务合规检查报告"""
        # 生成HTML报告
        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <title>财务合规检查报告</title>
                <style>
                    body {{
                        font-family: Arial, "PingFang SC", "Microsoft YaHei", SimHei, sans-serif;
                        margin: 40px;
                        color: #333;
                    }}
                    h1 {{
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }}
                    h2 {{
                        color: #2c3e50;
                        margin-top: 30px;
                    }}
                    .report-container {{
                        max-width: 1200px;
                        margin: 0 auto;
                    }}
                    .chart-container {{
                        margin: 20px 0;
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .chart-description {{
                        margin: 10px 0;
                        padding: 15px;
                        background-color: #f8f9fa;
                        border-left: 4px solid #3498db;
                        border-radius: 3px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }}
                    th {{
                        background-color: #f5f6fa;
                    }}
                    tr:hover {{
                        background-color: #f5f5f5;
                    }}
                </style>
            </head>
            <body>
                <div class="report-container">
                    <h1>财务合规检查报告</h1>
                    <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <h2>风险趋势分析</h2>
                    <div class="chart-description">
                        <p>该图表展示了近30天内各风险等级问题的占比变化趋势：</p>
                        <ul>
                            <li>柱状图按风险等级堆叠展示，高度表示占总问题数的百分比</li>
                            <li>鼠标悬停可查看具体日期的详细数据</li>
                            <li>颜色越深表示风险等级越高</li>
                        </ul>
                    </div>
                    <div class="chart-container">
                        {self._generate_trend_chart(data['historical_data']).to_html(full_html=False)}
                    </div>
                    
                    <h2>部门风险分布</h2>
                    <div class="chart-description">
                        <p>热力图展示了各部门的风险分布情况：</p>
                        <ul>
                            <li>颜色越红表示该类风险问题数量越多</li>
                            <li>颜色越绿表示该类风险问题数量越少</li>
                            <li>鼠标悬停可查看具体部门的详细数据</li>
                        </ul>
                        <p>使用建议：</p>
                        <ul>
                            <li>重点关注深红色区域，这些是需要优先处理的问题</li>
                            <li>横向对比可了解各部门的风险分布差异</li>
                            <li>纵向对比可了解各风险等级在部门间的分布情况</li>
                        </ul>
                    </div>
                    <div class="chart-container">
                        {self._generate_department_heatmap(data['department_data']).to_html(full_html=False)}
                    </div>
                    
                    <h2>详细问题列表</h2>
                    <table>
                        <tr>
                            <th>风险等级</th>
                            <th>问题描述</th>
                            <th>涉及部门</th>
                            <th>建议措施</th>
                        </tr>
                        {''.join(f"<tr><td>{issue['risk_level']}</td><td>{issue['description']}</td><td>{issue['department']}</td><td>{issue['suggestion']}</td></tr>\\n" for issue in data['issues'])}
                    </table>
                </div>
            </body>
        </html>
        """
        
        # 保存报告
        report_file = self.report_path / f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_file.write_text(html_content, encoding='utf-8')
        
        return report_file