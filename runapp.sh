#!/bin/bash

# 商户智能分析平台 - 自动运行脚本

echo "=========================================================="
echo "🚀 商户智能分析平台 - 自动运行脚本"
echo "=========================================================="

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p reports

# 生成访问令牌
echo "🔑 生成访问令牌..."
python get_token.py

# 调用集成分析API
echo "📊 调用集成分析API..."
python call_integrated_api.py

# 获取最新生成的报告文件
JSON_REPORT=$(ls -t integrated_analysis_response_*.json | head -1)
echo "📋 最新的分析报告: $JSON_REPORT"

# 生成HTML报告
echo "🔄 生成HTML报告..."
python report_generator.py "$JSON_REPORT"

HTML_REPORT="reports/$(basename $JSON_REPORT .json).html"

# 显示完成信息
echo "=========================================================="
echo "✅ 处理完成！"
echo "📝 JSON数据: $JSON_REPORT"
echo "📊 HTML报告: $HTML_REPORT"
echo "=========================================================="

# 打开报告
echo "🌐 打开HTML报告..."
open "$HTML_REPORT"

echo "👍 操作完成！" 