import json
import time
import requests

# 基础配置
BASE_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "password"
# 使用模拟模式
MOCK_MODE = True

def get_token():
    """获取访问令牌"""
    if MOCK_MODE:
        # 生成模拟令牌
        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcxNzc2MTYwMCwiaWF0IjoxNzE3Njc1MjAwLCJyb2xlIjoiYWRtaW4ifQ.8kpzZKnRXKYV7GYPQRjQFZEhPJ-a4JJ6PA2qYA9JCnQ"
        mock_response = {
            "access_token": mock_token,
            "token_type": "bearer",
            "expires_in": 86400,
            "generated_at": int(time.time())
        }
        
        # 保存令牌到文件
        with open("access_token.json", "w", encoding="utf-8") as f:
            json.dump(mock_response, f, ensure_ascii=False, indent=2)
            
        print("✅ [模拟模式] 成功获取访问令牌")
        print(f"💾 令牌已保存至 access_token.json")
        print(f"🔑 令牌值: {mock_token}")
        return mock_token
    else:
        try:
            print(f"🔐 正在请求访问令牌: {BASE_URL}/api/v1/token")
            response = requests.post(
                f"{BASE_URL}/api/v1/token",
                data={"username": USERNAME, "password": PASSWORD},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                token_data["generated_at"] = int(time.time())
                
                # 保存令牌到文件
                with open("access_token.json", "w", encoding="utf-8") as f:
                    json.dump(token_data, f, ensure_ascii=False, indent=2)
                    
                access_token = token_data["access_token"]
                print("✅ 成功获取访问令牌")
                print(f"💾 令牌已保存至 access_token.json")
                print(f"🔑 令牌值: {access_token}")
                return access_token
            else:
                print(f"❌ 认证失败: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {str(e)}")
            return None

def check_api_service():
    """检查API服务状态"""
    if MOCK_MODE:
        print("✅ [模拟模式] API服务状态检查")
        print("📡 模拟服务已准备就绪")
        return True
    
    try:
        print(f"🔍 检查API服务状态: {BASE_URL}/health")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
            return True
        else:
            print(f"⚠️ API服务返回异常状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到API服务: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始服务检查和令牌获取流程...")
    
    # 1. 检查服务状态
    print("\n📋 步骤1: 检查集成分析API服务状态")
    service_available = check_api_service()
    
    if service_available or MOCK_MODE:
        # 2. 获取访问令牌
        print("\n📋 步骤2: 获取访问令牌")
        token = get_token()
        
        if token:
            print("\n✅ 流程完成! 您现在可以使用此令牌访问集成分析API")
            print(f"📊 集成分析API地址: {BASE_URL}/api/v1/integrated-analysis")
            print("🔐 请在请求头中添加: Authorization: Bearer {token}")
        else:
            print("\n❌ 无法获取访问令牌，请检查服务状态和认证信息")
    else:
        print("\n❌ API服务不可用，请先启动服务") 