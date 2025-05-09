import requests
import json
import time
from datetime import datetime

# 基础配置
BASE_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "password"
# 添加模拟模式标志
MOCK_MODE = True  # 设置为True使用模拟数据

def get_token():
    """获取访问令牌"""
    if MOCK_MODE:
        print("✅ [模拟模式] 成功获取访问令牌")
        return "mock_token_123456789"
        
    response = requests.post(
        f"{BASE_URL}/api/v1/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✅ 成功获取访问令牌")
        return access_token
    else:
        print(f"❌ 认证失败: {response.text}")
        return None

def get_mock_response():
    """返回模拟的API响应数据"""
    return {
        "request_id": "req_202mno",
        "status": "success",
        "data": {
            "merchant_id": "m123456",
            "report_id": "rpt_xyz123",
            "time_range": {
                "start_date": "2023-01-01",
                "end_date": "2023-03-31"
            },
            "summary": {
                "health_score": 78.5,
                "revenue_trend": "increasing",
                "cost_efficiency": "moderate",
                "compliance_status": "needs_review",
                "cash_position": "healthy"
            },
            "cashflow_analysis": {
                "prediction": [
                    {"date": "2023-04-01", "value": 4520.25, "lower_bound": 4125.75, "upper_bound": 4915.50},
                    {"date": "2023-04-02", "value": 4615.10, "lower_bound": 4210.30, "upper_bound": 5019.90},
                    {"date": "2023-04-03", "value": 4580.75, "lower_bound": 4180.50, "upper_bound": 4980.25},
                    {"date": "2023-04-04", "value": 4625.50, "lower_bound": 4225.25, "upper_bound": 5025.75},
                    {"date": "2023-04-05", "value": 4720.80, "lower_bound": 4320.40, "upper_bound": 5120.95}
                ],
                "metrics": {
                    "mape": 4.5,
                    "rmse": 215.3,
                    "model_type": "arima",
                    "parameters": {"p": 2, "d": 1, "q": 2}
                }
            },
            "cost_analysis": {
                "total_cost": 152635.80,
                "cost_breakdown": [
                    {"category": "labor", "amount": 58623.45, "percentage": 38.4},
                    {"category": "raw_material", "amount": 42523.75, "percentage": 27.9},
                    {"category": "utilities", "amount": 12458.90, "percentage": 8.2},
                    {"category": "rent", "amount": 24000.00, "percentage": 15.7},
                    {"category": "marketing", "amount": 15029.70, "percentage": 9.8}
                ]
            },
            "compliance_analysis": {
                "overall_status": "needs_review",
                "type_status": {
                    "tax": "compliant",
                    "accounting": "needs_review",
                    "licensing": "non_compliant",
                    "labor": "compliant"
                },
                "risk_score": 42.5
            },
            "integrated_insights": [
                {
                    "category": "profitability",
                    "trend": "positive",
                    "insight": "收入增长率(8.5%)超过成本增长率(4.2%),利润率改善",
                    "recommendation": "继续当前的成本控制措施,同时进一步扩大高利润率产品线"
                },
                {
                    "category": "risk_management",
                    "trend": "attention_needed",
                    "insight": "合规风险(许可证过期)可能影响未来现金流",
                    "recommendation": "优先解决许可证合规问题,以避免潜在罚款和业务中断"
                },
                {
                    "category": "operational_efficiency",
                    "trend": "negative",
                    "insight": "人力成本占比高于行业平均(38.4% vs 32.0%)",
                    "recommendation": "审查工作流程,考虑优化人员配置或投资自动化技术"
                }
            ]
        }
    }

def test_integrated_analysis(access_token):
    """测试集成分析API"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "merchant_id": "m123456",
        "time_range": {
            "start_date": "2023-01-01",
            "end_date": "2023-03-31"
        },
        "analysis_types": ["cashflow", "cost", "compliance"],
        "parameters": {
            "prediction_days": 30,
            "confidence_level": 0.95,
            "analysis_depth": "detailed"
        }
    }
    
    print(f"📊 请求集成分析API: {BASE_URL}/api/v1/integrated-analysis")
    print(f"📝 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    start_time = time.time()
    
    if MOCK_MODE:
        # 模拟网络延迟
        time.sleep(1.2)
        response_status = 200
        result = get_mock_response()
    else:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/integrated-analysis",
                headers=headers,
                json=data,
                timeout=10  # 添加超时设置
            )
            response_status = response.status_code
            if response_status == 200:
                result = response.json()
            else:
                result = {"error": response.text}
        except requests.exceptions.RequestException as e:
            response_status = 500
            result = {"error": str(e)}
    
    duration = time.time() - start_time
    
    print(f"⏱️ API响应时间: {duration:.2f}秒")
    print(f"🔢 状态码: {response_status}")
    
    if response_status == 200:
        if MOCK_MODE:
            print("✅ [模拟模式] API调用成功!")
        else:
            print("✅ API调用成功!")
        
        # 保存完整响应
        filename = f"integrated_analysis_response_{int(time.time())}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 完整响应已保存至 {filename}")
        
        # 输出综合分析报告概要
        if "data" in result:
            report_data = result["data"]
            print("\n📋 综合分析报告摘要:")
            print(f"商户ID: {report_data['merchant_id']}")
            print(f"报告ID: {report_data['report_id']}")
            print(f"分析时间范围: {report_data['time_range']['start_date']} 至 {report_data['time_range']['end_date']}")
            
            if "summary" in report_data:
                summary = report_data["summary"]
                print("\n📊 商户健康状况摘要:")
                print(f"健康评分: {summary['health_score']}/100")
                print(f"收入趋势: {summary['revenue_trend']}")
                print(f"成本效率: {summary['cost_efficiency']}")
                print(f"合规状态: {summary['compliance_status']}")
                print(f"现金状况: {summary['cash_position']}")
            
            # 显示关键洞察
            if "integrated_insights" in report_data:
                print("\n💡 关键洞察:")
                for i, insight in enumerate(report_data['integrated_insights'], 1):
                    print(f"{i}. [{insight['category']}] {insight['trend']}")
                    print(f"   洞察: {insight['insight']}")
                    print(f"   建议: {insight['recommendation']}")
            
            # 打印现金流预测数据（简化版，不使用可视化）
            if "cashflow_analysis" in report_data and "prediction" in report_data["cashflow_analysis"]:
                print("\n📈 现金流预测数据:")
                predictions = report_data["cashflow_analysis"]["prediction"]
                # 只打印前5条记录
                for i, pred in enumerate(predictions[:5]):
                    print(f"   {pred['date']}: {pred['value']:.2f} [区间: {pred['lower_bound']:.2f} - {pred['upper_bound']:.2f}]")
                if len(predictions) > 5:
                    print(f"   ... 共 {len(predictions)} 条预测数据")
                
                # 打印预测指标
                if "metrics" in report_data["cashflow_analysis"]:
                    metrics = report_data["cashflow_analysis"]["metrics"]
                    print("\n📊 预测模型指标:")
                    print(f"   模型类型: {metrics.get('model_type', 'N/A')}")
                    print(f"   MAPE: {metrics.get('mape', 'N/A')}")
                    print(f"   RMSE: {metrics.get('rmse', 'N/A')}")
        else:
            print("\n⚠️ 响应格式异常，未找到data字段")
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ API调用失败: {json.dumps(result, indent=2, ensure_ascii=False)}")

def main():
    """主函数"""
    print("🚀 开始测试集成分析API...")
    if MOCK_MODE:
        print("⚠️ 当前为模拟模式，将使用模拟数据进行测试")
    
    access_token = get_token()
    if access_token:
        test_integrated_analysis(access_token)
    else:
        print("❌ 无法获取访问令牌，测试终止")

if __name__ == "__main__":
    main() 