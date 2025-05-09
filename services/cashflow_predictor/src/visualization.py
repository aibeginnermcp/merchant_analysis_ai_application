"""
可视化模块 - 负责生成预测结果图表和报告
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import json
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import os
import platform

# 配置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 使用系统自带的Arial Unicode MS字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CashFlowVisualizer:
    """
    现金流可视化器类，用于生成预测结果的可视化图表和PDF报告
    """
    
    def __init__(self, config: dict):
        """
        初始化可视化器
        
        Args:
            config: 配置字典，包含可视化参数
        """
        self.config = config
        self.style = {
            'figure.figsize': (12, 6),
            'axes.grid': True,
            'grid.alpha': 0.3,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'lines.linewidth': 2
        }
        
        # 设置matplotlib样式
        plt.style.use('default')  # 使用默认样式
        sns.set_style("whitegrid")  # 使用seaborn的网格样式
        
        # 应用自定义样式
        for key, value in self.style.items():
            plt.rcParams[key] = value
        
        self.output_dir = config.get('output_dir', 'reports')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置中文字体
        if platform.system() == 'Darwin':  # macOS
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'PingFang HK']
            self.chinese_font = "Arial Unicode MS"
            self.font_path = "/System/Library/Fonts/PingFang.ttc"  # 使用系统自带的PingFang字体
        else:  # Windows 或其他系统
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            self.chinese_font = "SimHei"
            self.font_path = "C:\\Windows\\Fonts\\simhei.ttf"
            
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
    def plot_time_series(self,
                        data: pd.Series,
                        title: str,
                        y_label: str = "金额",
                        figsize: Tuple[int, int] = (12, 6)) -> Figure:
        """
        绘制时间序列图
        
        Args:
            data: 时间序列数据
            title: 图表标题
            y_label: y轴标签
            figsize: 图表大小
            
        Returns:
            matplotlib图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(data.index, data.values, label='实际值')
        
        # 设置标题和标签
        ax.set_title(title, fontsize=14, pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        
        # 设置x轴日期格式
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 自动调整布局
        plt.tight_layout()
        
        return fig
        
    def plot_prediction(self,
                       historical_data: pd.Series,
                       predictions: pd.Series,
                       confidence_intervals: Optional[pd.DataFrame] = None,
                       title: str = "现金流预测结果",
                       figsize: Tuple[int, int] = (12, 6)) -> Figure:
        """
        绘制预测结果图
        
        Args:
            historical_data: 历史数据
            predictions: 预测结果
            confidence_intervals: 预测置信区间
            title: 图表标题
            figsize: 图表大小
            
        Returns:
            matplotlib图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制历史数据
        ax.plot(historical_data.index, historical_data.values,
                label='历史数据', color='blue')
        
        # 绘制预测结果
        ax.plot(predictions.index, predictions.values,
                label='预测值', color='red', linestyle='--')
        
        # 如果有置信区间，添加置信区间
        if confidence_intervals is not None:
            ax.fill_between(predictions.index,
                          confidence_intervals.iloc[:, 0],
                          confidence_intervals.iloc[:, 1],
                          color='red', alpha=0.2,
                          label='95%置信区间')
        
        # 设置标题和标签
        ax.set_title(title, fontsize=14, pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('金额', fontsize=12)
        
        # 设置x轴日期格式
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # 添加图例
        ax.legend()
        
        # 自动调整布局
        plt.tight_layout()
        
        return fig
        
    def plot_residuals(self, residuals: pd.Series, figsize: Tuple[int, int] = (12, 8)) -> Figure:
        """
        绘制残差分析图
        
        Args:
            residuals: 残差数据
            figsize: 图表大小
            
        Returns:
            matplotlib图表对象
        """
        from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
        from scipy import stats
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 残差时间序列图
        ax1.plot(residuals.index, residuals.values)
        ax1.set_title('残差时间序列')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('残差')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # 残差直方图
        sns.histplot(residuals.values, kde=True, ax=ax2)
        ax2.set_title('残差分布')
        ax2.set_xlabel('残差')
        ax2.set_ylabel('频数')
        
        # Q-Q图
        stats.probplot(residuals.values, dist="norm", plot=ax3)
        ax3.set_title('Q-Q图')
        
        # 残差自相关图
        plot_acf(residuals.values, lags=min(40, len(residuals)-1), ax=ax4)
        ax4.set_title('残差自相关图')
        
        plt.tight_layout()
        return fig
        
    def generate_report(self,
                       historical_data: pd.Series,
                       predictions: pd.Series,
                       confidence_intervals: pd.DataFrame,
                       metrics: Dict[str, float],
                       output_path: str):
        """
        生成PDF分析报告
        
        Args:
            historical_data: 历史数据
            predictions: 预测结果
            confidence_intervals: 预测置信区间
            metrics: 模型评估指标
            output_path: 输出文件路径
        """
        class PDF(FPDF):
            def __init__(self, font_path):
                super().__init__()
                self.font_path = font_path
                self.add_font('custom', '', font_path, uni=True)
                
            def header(self):
                self.set_font('custom', '', 15)
                self.cell(0, 10, '现金流预测分析报告', 0, 1, 'C')
                self.ln(10)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('custom', '', 8)
                self.cell(0, 10, f'第 {self.page_no()} 页', 0, 0, 'C')
                
        # 创建PDF对象
        pdf = PDF(self.font_path)
        pdf.add_page()
        
        # 添加报告生成时间
        pdf.set_font('custom', '', 10)
        pdf.cell(0, 10, f'报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1)
        pdf.ln(5)
        
        # 添加数据概览
        pdf.set_font('custom', '', 12)
        pdf.cell(0, 10, '1. 数据概览', 0, 1)
        pdf.set_font('custom', '', 10)
        
        # 确保日期格式正确
        start_date = pd.to_datetime(historical_data.index[0]).strftime("%Y-%m-%d")
        end_date = pd.to_datetime(historical_data.index[-1]).strftime("%Y-%m-%d")
        pred_start = pd.to_datetime(predictions.index[0]).strftime("%Y-%m-%d")
        pred_end = pd.to_datetime(predictions.index[-1]).strftime("%Y-%m-%d")
        
        pdf.cell(0, 10, f'历史数据时间范围：{start_date} 至 {end_date}', 0, 1)
        pdf.cell(0, 10, f'预测时间范围：{pred_start} 至 {pred_end}', 0, 1)
        pdf.ln(5)
        
        # 添加预测结果图
        pdf.set_font('custom', '', 12)
        pdf.cell(0, 10, '2. 预测结果', 0, 1)
        
        # 生成并保存预测图
        fig_pred = self.plot_prediction(historical_data, predictions, confidence_intervals)
        pred_img_path = 'temp_prediction.png'
        fig_pred.savefig(pred_img_path, dpi=300, bbox_inches='tight')
        plt.close(fig_pred)
        
        # 添加预测图到PDF
        pdf.image(pred_img_path, x=10, w=190)
        pdf.ln(5)
        
        # 添加模型评估指标
        pdf.set_font('custom', '', 12)
        pdf.cell(0, 10, '3. 模型评估指标', 0, 1)
        pdf.set_font('custom', '', 10)
        metrics_names = {
            'mae': '平均绝对误差(MAE)',
            'rmse': '均方根误差(RMSE)',
            'mape': '平均绝对百分比误差(MAPE)'
        }
        for metric_name, value in metrics.items():
            display_name = metrics_names.get(metric_name.lower(), metric_name)
            if 'mape' in metric_name.lower():
                pdf.cell(0, 10, f'{display_name}: {value:.2f}%', 0, 1)
            else:
                pdf.cell(0, 10, f'{display_name}: ¥{value:.2f}', 0, 1)
        pdf.ln(5)
        
        # 添加风险分析
        pdf.set_font('custom', '', 12)
        pdf.cell(0, 10, '4. 风险分析', 0, 1)
        pdf.set_font('custom', '', 10)
        
        # 计算基本风险指标
        below_zero = predictions[predictions < 0]
        if len(below_zero) > 0:
            pdf.cell(0, 10, f'预测期内可能出现资金缺口的天数：{len(below_zero)}天', 0, 1)
            pdf.cell(0, 10, f'最大资金缺口：¥{below_zero.min():.2f}', 0, 1)
        else:
            pdf.cell(0, 10, '预测期内现金流状况良好，无资金缺口风险', 0, 1)
            
        # 添加置信区间解释
        pdf.ln(5)
        pdf.set_font('custom', '', 12)
        pdf.cell(0, 10, '5. 如何解读预测结果', 0, 1)
        pdf.set_font('custom', '', 10)
        pdf.multi_cell(0, 10, '预测图中的红色虚线表示预测值，浅红色区域表示95%置信区间。这意味着实际值有95%的概率落在该区间内。置信区间越窄，预测越精确；越宽，不确定性越大。建议重点关注置信区间的下限，这代表了最坏情况下的现金流状况。', 0, 'L')
        
        # 添加决策建议
        pdf.ln(5)
        pdf.set_font('custom', '', 12)
        pdf.cell(0, 10, '6. 决策建议', 0, 1)
        pdf.set_font('custom', '', 10)
        
        # 根据MAPE值判断预测可靠性
        if metrics['mape'] < 10:
            reliability = '高'
        elif metrics['mape'] < 20:
            reliability = '中等'
        else:
            reliability = '低'
            
        pdf.multi_cell(0, 10, f'预测可靠性：{reliability}\n' + 
                      f'建议持有现金储备：¥{abs(below_zero.min()) if len(below_zero) > 0 else predictions.min():.2f}\n' +
                      '短期资金管理建议：\n' +
                      '1. 重点关注预测期内现金流低谷期\n' +
                      '2. 提前规划融资需求\n' +
                      '3. 适当调整收付款政策\n' +
                      '4. 定期监控实际现金流与预测的偏差', 0, 'L')
            
        # 保存PDF
        output_path = os.path.join(self.output_dir, output_path)
        pdf.output(output_path)
        
        # 清理临时文件
        os.remove(pred_img_path)
        
        logger.info(f"报告已生成并保存至 {output_path}")
        
    def save_plots(self, figures: Dict[str, Figure], output_dir: str):
        """
        保存图表
        
        Args:
            figures: 图表字典，键为图表名称，值为Figure对象
            output_dir: 输出目录
        """
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存每个图表
        for name, fig in figures.items():
            file_path = output_path / f"{name}.png"
            fig.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            logger.info(f"图表已保存至 {file_path}")
            
    def plot_seasonal_decompose(self, data: pd.Series, figsize: Tuple[int, int] = (12, 10)) -> Figure:
        """
        绘制时间序列分解图
        
        Args:
            data: 时间序列数据
            figsize: 图表大小
            
        Returns:
            matplotlib图表对象
        """
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        # 执行时间序列分解
        decomposition = seasonal_decompose(data, period=30)  # 假设月度季节性
        
        # 创建图表
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=figsize)
        
        # 原始数据
        ax1.plot(data.index, data.values)
        ax1.set_title('原始时间序列')
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # 趋势
        ax2.plot(data.index, decomposition.trend)
        ax2.set_title('趋势')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # 季节性
        ax3.plot(data.index, decomposition.seasonal)
        ax3.set_title('季节性')
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # 残差
        ax4.plot(data.index, decomposition.resid)
        ax4.set_title('残差')
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # 调整布局
        plt.tight_layout()
        
        return fig 