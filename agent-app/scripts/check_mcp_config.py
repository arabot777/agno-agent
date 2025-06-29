#!/usr/bin/env python3
"""
MCP配置检查脚本

用于验证WaveSpeed MCP的配置是否正确设置。

使用方法:
python scripts/check_mcp_config.py
"""

import os
import sys
from pathlib import Path


def check_environment_variables():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    required_vars = {
        "WAVESPEED_API_KEY": "WaveSpeed API密钥",
    }
    
    optional_vars = {
        "WAVESPEED_API_HOST": "WaveSpeed API主机",
        "WAVESPEED_API_RESOURCE_MODE": "资源模式",
    }
    
    all_good = True
    
    # 检查必需变量
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # 隐藏密钥的大部分内容
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✅ {var}: {masked_value} ({desc})")
        else:
            print(f"  ❌ {var}: 未设置 ({desc})")
            all_good = False
    
    # 检查可选变量
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value} ({desc})")
        else:
            print(f"  ⚠️  {var}: 未设置 ({desc}) - 可选")
    
    return all_good


def check_config_files():
    """检查配置文件"""
    print("\n📁 检查配置文件...")
    
    config_files = [
        ("example.env", "环境变量模板"),
        ("mcp_config.json", "MCP服务器配置"),
        ("workspace/example_secrets/dev_app_secrets.yml", "开发环境密钥模板"),
    ]
    
    for file_path, desc in config_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"  ✅ {file_path}: 存在 ({desc})")
        else:
            print(f"  ❌ {file_path}: 不存在 ({desc})")

def check_mcp_package():
    """检查MCP包安装"""
    print("\n📦 检查MCP包安装...")
    
    try:
        import mcp
        print(f"  ✅ mcp: 已安装 (版本: {mcp.__version__ if hasattr(mcp, '__version__') else '未知'})")
    except ImportError:
        print("  ❌ mcp: 未安装")
        return False
    
    try:
        # 尝试导入wavespeed-mcp
        import subprocess
        result = subprocess.run(["wavespeed-mcp", "--help"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ wavespeed-mcp: 命令可用")
        else:
            print("  ❌ wavespeed-mcp: 命令不可用")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ wavespeed-mcp: 命令不可用")
        return False
    
    return True

def provide_setup_instructions():
    """提供设置说明"""
    print("\n💡 设置说明:")
    print("=" * 50)
    
    print("\n1. 设置环境变量:")
    print("   export WAVESPEED_API_KEY='your_api_key_here'")
    
    print("\n2. 或创建 .env 文件:")
    print("   cp example.env .env")
    print("   # 然后编辑 .env 文件并设置真实的API密钥")
    
    print("\n3. 安装MCP包:")
    print("   pip install mcp wavespeed-mcp")
    
    print("\n4. 测试配置:")
    print("   python examples/simple_mcp_test.py")

def main():
    """主函数"""
    print("🧪 WaveSpeed MCP配置检查")
    print("=" * 50)
    
    # 检查当前目录
    if not Path("agents").exists():
        print("❌ 错误：请在项目根目录运行此脚本")
        sys.exit(1)
    
    env_ok = check_environment_variables()
    check_config_files()
    pkg_ok = check_mcp_package()
    
    print("\n" + "=" * 50)
    
    if env_ok and pkg_ok:
        print("🎉 配置检查通过！MCP应该可以正常工作。")
        print("\n📋 下一步:")
        print("   python examples/simple_mcp_test.py")
    else:
        print("⚠️  配置不完整，请按照说明设置。")
        provide_setup_instructions()

if __name__ == "__main__":
    main() 