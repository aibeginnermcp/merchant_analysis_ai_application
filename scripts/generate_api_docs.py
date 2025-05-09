#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API文档生成工具

自动从微服务中提取API接口信息，生成统一的OpenAPI 3.0格式文档。
支持合并多个服务的API文档，生成综合性API参考手册。

使用方法:
    python generate_api_docs.py [选项]

选项:
    --output-dir    输出目录，默认为docs/api
    --format        输出格式，支持json/yaml/markdown/html，默认为markdown
    --services      要处理的服务列表，默认为所有服务
    --template      自定义模板文件路径
"""

import os
import sys
import json
import yaml
import logging
import argparse
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from urllib.parse import urlparse

# 尝试导入FastAPI相关库
try:
    from fastapi import FastAPI
    from fastapi.openapi.utils import get_openapi
except ImportError:
    print("警告: 未找到FastAPI库，请先安装: pip install fastapi")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api-doc-generator")

# 服务基本信息配置
SERVICE_INFO = {
    "api_gateway": {
        "title": "API网关服务",
        "description": "统一API网关，处理认证、授权、请求路由和API版本管理",
        "port": 8000,
        "module_path": "services.api_gateway.src.main:app"
    },
    "cashflow_predictor": {
        "title": "现金流预测服务",
        "description": "基于时间序列分析的现金流预测服务，提供多种预测模型",
        "port": 8002,
        "module_path": "services.cashflow_predictor.src.main:app"
    },
    "cost_analyzer": {
        "title": "成本穿透分析服务",
        "description": "多维度成本结构分析服务，支持成本归因与优化建议",
        "port": 8001,
        "module_path": "services.cost_analyzer.src.main:app"
    },
    "compliance_checker": {
        "title": "财务合规检查服务",
        "description": "自动检查财务数据合规性，提供风险预警与合规建议",
        "port": 8003,
        "module_path": "services.compliance_checker.src.main:app"
    },
    "data_simulator": {
        "title": "数据模拟服务",
        "description": "生成各行业模拟商户数据，用于测试和开发",
        "port": 8004,
        "module_path": "services.data_simulator.src.main:app"
    }
}

# Markdown文档模板
MARKDOWN_TEMPLATE = """# {title}

{description}

## 基本信息

- **服务名称**: {service_name}
- **基础URL**: {base_url}
- **版本**: {version}

## 认证方式

所有API请求需要在请求头中包含有效的JWT令牌:

```
Authorization: Bearer <token>
```

## API接口列表

{endpoints}

## 数据模型

{models}

## 状态码说明

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 错误响应格式

```json
{
  "code": "ERROR_CODE",
  "message": "错误描述信息",
  "details": {
    // 详细错误信息
  }
}
```
"""

class ApiDocGenerator:
    """API文档生成器类"""
    
    def __init__(
        self,
        output_dir: str = "docs/api",
        output_format: str = "markdown",
        service_list: Optional[List[str]] = None,
        template_file: Optional[str] = None
    ):
        """
        初始化API文档生成器
        
        Args:
            output_dir: 输出目录
            output_format: 输出格式 (json, yaml, markdown, html)
            service_list: 要处理的服务列表，为None则处理所有服务
            template_file: 自定义模板文件路径
        """
        self.output_dir = Path(output_dir)
        self.output_format = output_format
        self.service_list = service_list or list(SERVICE_INFO.keys())
        self.template_file = template_file
        self.api_specs: Dict[str, Dict] = {}
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载自定义模板
        self.template = MARKDOWN_TEMPLATE
        if template_file and os.path.exists(template_file):
            with open(template_file, "r", encoding="utf-8") as f:
                self.template = f.read()
        
        logger.info(f"文档生成器初始化完成，将生成{len(self.service_list)}个服务的API文档")
        
    def load_app_from_module(self, module_path: str) -> Optional[FastAPI]:
        """
        从模块路径加载FastAPI应用实例
        
        Args:
            module_path: 模块路径，格式为 "package.module:variable"
            
        Returns:
            FastAPI应用实例或None
        """
        try:
            # 解析模块路径
            module_str, var_str = module_path.split(":", 1)
            
            # 尝试导入模块
            spec = importlib.util.find_spec(module_str)
            if spec is None:
                logger.error(f"找不到模块: {module_str}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取FastAPI应用实例
            app = getattr(module, var_str, None)
            if not isinstance(app, FastAPI):
                logger.error(f"{module_str}:{var_str} 不是FastAPI实例")
                return None
                
            return app
            
        except Exception as e:
            logger.error(f"加载模块时出错: {e}")
            return None

    def _generate_openapi_spec(self, app: FastAPI, service_name: str) -> Dict[str, Any]:
        """
        从FastAPI应用生成OpenAPI规范
        
        Args:
            app: FastAPI应用实例
            service_name: 服务名称
            
        Returns:
            OpenAPI规范字典
        """
        service_info = SERVICE_INFO.get(service_name, {})
        
        # 设置标题和描述
        title = service_info.get("title", f"{service_name} API")
        description = service_info.get("description", f"{service_name} API文档")
        
        # 生成OpenAPI规范
        openapi_schema = get_openapi(
            title=title,
            description=description,
            version="1.0.0",
            routes=app.routes
        )
        
        # 添加服务器信息
        port = service_info.get("port", 8000)
        openapi_schema["servers"] = [
            {"url": f"http://localhost:{port}", "description": "本地开发环境"},
            {"url": f"https://{service_name}.example.com", "description": "生产环境"}
        ]
        
        # 添加安全配置
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        
        openapi_schema["security"] = [{"bearerAuth": []}]
        
        return openapi_schema

    def generate_api_docs(self) -> bool:
        """
        生成所有服务的API文档
        
        Returns:
            是否成功生成文档
        """
        logger.info("开始生成API文档")
        
        for service_name in self.service_list:
            # 检查服务是否存在
            if service_name not in SERVICE_INFO:
                logger.warning(f"未找到服务配置: {service_name}，跳过此服务")
                continue
                
            logger.info(f"处理服务: {service_name}")
            
            # 加载FastAPI应用
            module_path = SERVICE_INFO[service_name]["module_path"]
            app = self.load_app_from_module(module_path)
            
            if app is None:
                logger.error(f"无法加载服务应用: {service_name}")
                continue
                
            # 生成OpenAPI规范
            openapi_spec = self._generate_openapi_spec(app, service_name)
            self.api_specs[service_name] = openapi_spec
            
            # 保存API规范
            self._save_api_spec(service_name, openapi_spec)
        
        # 合并所有API文档
        if len(self.api_specs) > 0:
            self._generate_merged_api_docs()
            return True
        else:
            logger.error("未能生成任何API文档")
            return False

    def _save_api_spec(self, service_name: str, openapi_spec: Dict[str, Any]) -> None:
        """
        保存API规范文档
        
        Args:
            service_name: 服务名称
            openapi_spec: OpenAPI规范字典
        """
        # 保存JSON格式
        json_path = self.output_dir / f"{service_name}_openapi.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
            
        logger.info(f"已保存JSON格式API文档: {json_path}")
        
        # 保存YAML格式
        yaml_path = self.output_dir / f"{service_name}_openapi.yaml"
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(openapi_spec, f, sort_keys=False, default_flow_style=False)
            
        logger.info(f"已保存YAML格式API文档: {yaml_path}")
        
        # 生成Markdown文档
        if self.output_format in ["markdown", "md", "all"]:
            self._generate_markdown_doc(service_name, openapi_spec)

    def _format_endpoint_docs(self, paths_dict: Dict) -> str:
        """
        格式化API接口文档为Markdown格式
        
        Args:
            paths_dict: OpenAPI paths对象
            
        Returns:
            格式化后的Markdown文本
        """
        result = []
        
        for path, methods in paths_dict.items():
            for method, operation in methods.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    method_upper = method.upper()
                    summary = operation.get("summary", "未命名接口")
                    description = operation.get("description", "")
                    
                    result.append(f"### {summary}\n")
                    result.append(f"**路径**: `{path}`\n")
                    result.append(f"**方法**: `{method_upper}`\n")
                    
                    if description:
                        result.append(f"**描述**: {description}\n")
                    
                    # 请求参数
                    params = operation.get("parameters", [])
                    if params:
                        result.append("#### 请求参数\n")
                        result.append("| 名称 | 位置 | 类型 | 必填 | 描述 |")
                        result.append("|------|------|------|------|------|")
                        
                        for param in params:
                            name = param.get("name", "")
                            location = param.get("in", "")
                            required = "是" if param.get("required", False) else "否"
                            schema_type = param.get("schema", {}).get("type", "object")
                            description = param.get("description", "")
                            
                            result.append(f"| {name} | {location} | {schema_type} | {required} | {description} |")
                        
                        result.append("")
                    
                    # 请求体
                    request_body = operation.get("requestBody", {})
                    if request_body:
                        result.append("#### 请求体\n")
                        content = request_body.get("content", {})
                        
                        for content_type, content_schema in content.items():
                            result.append(f"**类型**: `{content_type}`\n")
                            schema = content_schema.get("schema", {})
                            schema_ref = schema.get("$ref", "")
                            
                            if schema_ref:
                                # 从引用中提取模型名称
                                model_name = schema_ref.split("/")[-1]
                                result.append(f"**模型**: [{model_name}](#model-{model_name.lower()})\n")
                            else:
                                result.append("**结构**:\n")
                                result.append("```json")
                                result.append(json.dumps(schema, ensure_ascii=False, indent=2))
                                result.append("```\n")
                    
                    # 响应
                    responses = operation.get("responses", {})
                    if responses:
                        result.append("#### 响应\n")
                        
                        for status_code, response in responses.items():
                            result.append(f"**状态码**: `{status_code}`\n")
                            description = response.get("description", "")
                            if description:
                                result.append(f"**描述**: {description}\n")
                            
                            content = response.get("content", {})
                            for content_type, content_schema in content.items():
                                result.append(f"**类型**: `{content_type}`\n")
                                schema = content_schema.get("schema", {})
                                schema_ref = schema.get("$ref", "")
                                
                                if schema_ref:
                                    # 从引用中提取模型名称
                                    model_name = schema_ref.split("/")[-1]
                                    result.append(f"**模型**: [{model_name}](#model-{model_name.lower()})\n")
                                else:
                                    result.append("**结构**:\n")
                                    result.append("```json")
                                    result.append(json.dumps(schema, ensure_ascii=False, indent=2))
                                    result.append("```\n")
                    
                    # 示例
                    result.append("#### 示例\n")
                    result.append("```bash")
                    
                    if method_upper == "GET":
                        result.append(f"curl -X {method_upper} \\")
                        result.append("  -H \"Authorization: Bearer YOUR_TOKEN\" \\")
                        result.append(f"  \"http://localhost:8000{path}\"")
                    else:
                        result.append(f"curl -X {method_upper} \\")
                        result.append("  -H \"Content-Type: application/json\" \\")
                        result.append("  -H \"Authorization: Bearer YOUR_TOKEN\" \\")
                        result.append("  -d '{\"key\": \"value\"}' \\")
                        result.append(f"  \"http://localhost:8000{path}\"")
                    
                    result.append("```\n")
                    
                    result.append("---\n")
        
        return "\n".join(result)

    def _format_models_docs(self, components_dict: Dict) -> str:
        """
        格式化数据模型文档为Markdown格式
        
        Args:
            components_dict: OpenAPI components对象
            
        Returns:
            格式化后的Markdown文本
        """
        result = []
        schemas = components_dict.get("schemas", {})
        
        for model_name, schema in schemas.items():
            result.append(f"### <a id=\"model-{model_name.lower()}\"></a>{model_name}\n")
            
            description = schema.get("description", "")
            if description:
                result.append(f"{description}\n")
            
            # 属性表格
            properties = schema.get("properties", {})
            if properties:
                result.append("| 属性 | 类型 | 必填 | 描述 |")
                result.append("|------|------|------|------|")
                
                required_props = schema.get("required", [])
                
                for prop_name, prop_schema in properties.items():
                    prop_type = prop_schema.get("type", "object")
                    is_required = "是" if prop_name in required_props else "否"
                    description = prop_schema.get("description", "")
                    
                    result.append(f"| {prop_name} | {prop_type} | {is_required} | {description} |")
                
                result.append("")
            
            # 示例数据
            result.append("**示例**:\n")
            result.append("```json")
            
            example = {}
            for prop_name, prop_schema in properties.items():
                if prop_schema.get("type") == "string":
                    example[prop_name] = prop_schema.get("example", "string")
                elif prop_schema.get("type") == "number":
                    example[prop_name] = prop_schema.get("example", 0)
                elif prop_schema.get("type") == "integer":
                    example[prop_name] = prop_schema.get("example", 0)
                elif prop_schema.get("type") == "boolean":
                    example[prop_name] = prop_schema.get("example", False)
                elif prop_schema.get("type") == "array":
                    example[prop_name] = []
                else:
                    example[prop_name] = {}
            
            result.append(json.dumps(example, ensure_ascii=False, indent=2))
            result.append("```\n")
        
        return "\n".join(result)

    def _generate_markdown_doc(self, service_name: str, openapi_spec: Dict[str, Any]) -> None:
        """
        生成Markdown格式的API文档
        
        Args:
            service_name: 服务名称
            openapi_spec: OpenAPI规范字典
        """
        service_info = SERVICE_INFO.get(service_name, {})
        port = service_info.get("port", 8000)
        
        # 格式化接口文档
        endpoints_docs = self._format_endpoint_docs(openapi_spec.get("paths", {}))
        
        # 格式化数据模型文档
        models_docs = self._format_models_docs(openapi_spec.get("components", {}))
        
        # 填充模板
        markdown_content = self.template.format(
            title=openapi_spec.get("info", {}).get("title", f"{service_name} API"),
            description=openapi_spec.get("info", {}).get("description", ""),
            service_name=service_name,
            base_url=f"http://localhost:{port}",
            version=openapi_spec.get("info", {}).get("version", "1.0.0"),
            endpoints=endpoints_docs,
            models=models_docs
        )
        
        # 保存Markdown文档
        md_path = self.output_dir / f"{service_name}_api.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        logger.info(f"已保存Markdown格式API文档: {md_path}")

    def _generate_merged_api_docs(self) -> None:
        """生成合并后的API文档"""
        logger.info("生成合并的API文档")
        
        # 合并OpenAPI规范
        merged_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "智能商户经营分析报表生成器 API",
                "description": "集成所有微服务API的统一接口文档",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "本地开发环境"},
                {"url": "https://api.merchant-analytics.example.com", "description": "生产环境"}
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"bearerAuth": []}]
        }
        
        # 合并路径和组件
        for service_name, spec in self.api_specs.items():
            # 给路径添加服务前缀
            prefix = f"/{service_name}"
            
            for path, methods in spec.get("paths", {}).items():
                new_path = prefix + path if not path.startswith(prefix) else path
                merged_spec["paths"][new_path] = methods
            
            # 合并组件
            for schema_name, schema in spec.get("components", {}).get("schemas", {}).items():
                new_schema_name = f"{service_name.capitalize()}{schema_name}"
                merged_spec["components"]["schemas"][new_schema_name] = schema
                
                # 更新引用
                self._update_refs(merged_spec["paths"], f"#/components/schemas/{schema_name}", 
                                f"#/components/schemas/{new_schema_name}")
        
        # 保存合并后的OpenAPI规范
        merged_json_path = self.output_dir / "openapi.json"
        with open(merged_json_path, "w", encoding="utf-8") as f:
            json.dump(merged_spec, f, ensure_ascii=False, indent=2)
            
        merged_yaml_path = self.output_dir / "openapi.yaml"
        with open(merged_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(merged_spec, f, sort_keys=False, default_flow_style=False)
            
        logger.info(f"已保存合并后的OpenAPI规范: {merged_json_path}, {merged_yaml_path}")
        
        # 生成合并后的Markdown文档
        if self.output_format in ["markdown", "md", "all"]:
            # 格式化接口文档
            endpoints_docs = self._format_endpoint_docs(merged_spec.get("paths", {}))
            
            # 格式化数据模型文档
            models_docs = self._format_models_docs(merged_spec.get("components", {}))
            
            # 填充模板
            markdown_content = self.template.format(
                title="智能商户经营分析报表生成器 API",
                description="集成所有微服务API的统一接口文档",
                service_name="merchant-analytics",
                base_url="http://localhost:8000",
                version="1.0.0",
                endpoints=endpoints_docs,
                models=models_docs
            )
            
            # 保存合并后的Markdown文档
            merged_md_path = self.output_dir / "merchant_analytics_api.md"
            with open(merged_md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            logger.info(f"已保存合并后的Markdown文档: {merged_md_path}")
    
    def _update_refs(self, obj: Any, old_ref: str, new_ref: str) -> None:
        """
        递归更新对象中的引用
        
        Args:
            obj: 要更新的对象
            old_ref: 原引用
            new_ref: 新引用
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "$ref" and value == old_ref:
                    obj[key] = new_ref
                else:
                    self._update_refs(value, old_ref, new_ref)
        elif isinstance(obj, list):
            for item in obj:
                self._update_refs(item, old_ref, new_ref)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="API文档生成工具")
    
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="docs/api",
        help="输出目录，默认为docs/api"
    )
    
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["json", "yaml", "markdown", "md", "html", "all"],
        default="markdown",
        help="输出格式，默认为markdown"
    )
    
    parser.add_argument(
        "--services",
        dest="services",
        nargs="+",
        help="要处理的服务列表，默认为所有服务"
    )
    
    parser.add_argument(
        "--template",
        dest="template",
        help="自定义Markdown模板文件路径"
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    generator = ApiDocGenerator(
        output_dir=args.output_dir,
        output_format=args.output_format,
        service_list=args.services,
        template_file=args.template
    )
    
    success = generator.generate_api_docs()
    
    if success:
        logger.info("API文档生成成功")
        return 0
    else:
        logger.error("API文档生成失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 