#!/usr/bin/env python3
"""配置管理CLI工具"""
import os
import sys
import json
import click
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.shared.config_manager import config_manager
from services.shared.config_validator import config_validator

@click.group()
def cli():
    """商户智能经营分析平台配置管理工具"""
    pass

@cli.command()
@click.argument("service_name")
def show(service_name: str):
    """显示服务配置
    
    Args:
        service_name: 服务名称
    """
    try:
        if service_name == "global":
            config = config_manager.get_global_config()
        else:
            config = config_manager.get_service_config(service_name)
            
        click.echo(json.dumps(config, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("service_name")
@click.argument("config_file", type=click.Path(exists=True))
def update(service_name: str, config_file: str):
    """更新服务配置
    
    Args:
        service_name: 服务名称
        config_file: 配置文件路径
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            updates = json.load(f)
            
        if service_name == "global":
            config_manager.update_global_config(updates)
        else:
            config_manager.update_service_config(service_name, updates)
            
        click.echo(f"成功更新 {service_name} 配置")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("service_name", required=False)
def validate(service_name: Optional[str] = None):
    """验证服务配置
    
    Args:
        service_name: 服务名称（可选）
    """
    try:
        if service_name:
            if service_name == "global":
                config = config_manager.get_global_config()
                errors = config_validator.validate_config_dependencies(config)
            else:
                config = config_manager.get_service_config(service_name)
                errors = config_validator.validate_service_config(service_name, config)
                
            if errors:
                click.echo(f"{service_name} 配置验证失败:")
                for error in errors:
                    click.echo(f"- {error}")
                sys.exit(1)
            else:
                click.echo(f"{service_name} 配置验证通过")
        else:
            results = config_validator.validate_all_configs()
            if results:
                click.echo("配置验证失败:")
                for service, errors in results.items():
                    click.echo(f"\n{service}:")
                    for error in errors:
                        click.echo(f"- {error}")
                sys.exit(1)
            else:
                click.echo("所有配置验证通过")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("service_name")
def reload(service_name: str):
    """重新加载服务配置
    
    Args:
        service_name: 服务名称
    """
    try:
        if service_name == "all":
            config_manager.reload_config()
            click.echo("已重新加载所有配置")
        else:
            config_manager.reload_config(service_name)
            click.echo(f"已重新加载 {service_name} 配置")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

@cli.command()
def init():
    """初始化配置目录"""
    try:
        # 创建配置目录
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # 创建示例配置文件
        example_config = {
            "SERVICE_NAME": "example-service",
            "SERVICE_HOST": "0.0.0.0",
            "SERVICE_PORT": 8000,
            "MONGODB_URI": "mongodb://localhost:27017",
            "REDIS_URI": "redis://localhost:6379"
        }
        
        with open(config_dir / "example.yml", "w", encoding="utf-8") as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
            
        click.echo("配置目录初始化完成")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

@cli.command()
def env():
    """显示环境变量覆盖值"""
    try:
        overrides = config_manager.get_environment_overrides()
        if overrides:
            click.echo("环境变量覆盖值:")
            for key, value in overrides.items():
                click.echo(f"{key}={value}")
        else:
            click.echo("没有环境变量覆盖值")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

@cli.command()
def apply_env():
    """应用环境变量覆盖值"""
    try:
        config_manager.apply_environment_overrides()
        click.echo("已应用环境变量覆盖值")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli() 