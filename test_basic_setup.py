#!/usr/bin/env python3
"""
测试脚本 - 验证AI-Trader基本设置
Test Script - Verify AI-Trader Basic Setup

此脚本不需要API密钥，仅验证项目结构和基本功能
This script does not require API keys, only validates project structure and basic functionality
"""

import os
import sys
import json
from pathlib import Path

def check_python_version():
    """检查Python版本 / Check Python version"""
    version = sys.version_info
    print(f"🐍 Python版本 / Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 10:
        print("   ✅ Python版本符合要求 (>= 3.10) / Python version meets requirements")
        return True
    else:
        print("   ❌ Python版本过低，需要3.10或更高 / Python version too low, requires 3.10+")
        return False

def check_dependencies():
    """检查依赖包 / Check dependencies"""
    print("\n📦 检查依赖包 / Checking Dependencies:")
    
    # Mapping of import names to display names
    package_mapping = {
        'langchain': 'langchain',
        'langchain_openai': 'langchain-openai',
        'langchain_mcp_adapters': 'langchain-mcp-adapters',
        'fastmcp': 'fastmcp',
        'dotenv': 'python-dotenv'
    }
    
    all_installed = True
    for import_name, display_name in package_mapping.items():
        try:
            __import__(import_name)
            print(f"   ✅ {display_name}")
        except ImportError:
            print(f"   ❌ {display_name} 未安装 / not installed")
            all_installed = False
    
    return all_installed

def check_project_structure():
    """检查项目结构 / Check project structure"""
    print("\n📁 检查项目结构 / Checking Project Structure:")
    
    required_dirs = [
        'agent',
        'agent/base_agent',
        'agent_tools',
        'configs',
        'data',
        'prompts',
        'tools'
    ]
    
    required_files = [
        'main.py',
        'requirements.txt',
        '.env.example',
        'agent/base_agent/base_agent.py',
        'agent/base_agent/base_agent_hour.py',
        'agent_tools/start_mcp_services.py',
        'agent_tools/tool_trade.py',
        'agent_tools/tool_get_price_local.py',
        'configs/default_config.json'
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"   ✅ 目录 / Directory: {dir_path}")
        else:
            print(f"   ❌ 缺失目录 / Missing directory: {dir_path}")
            all_good = False
    
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"   ✅ 文件 / File: {file_path}")
        else:
            print(f"   ❌ 缺失文件 / Missing file: {file_path}")
            all_good = False
    
    return all_good

def check_data_availability():
    """检查数据可用性 / Check data availability"""
    print("\n📊 检查数据可用性 / Checking Data Availability:")
    
    # Check merged.jsonl
    merged_file = 'data/merged.jsonl'
    if os.path.isfile(merged_file):
        try:
            with open(merged_file, 'r') as f:
                line_count = sum(1 for _ in f)
            print(f"   ✅ {merged_file} 存在 / exists ({line_count} 股票 / stocks)")
        except Exception as e:
            print(f"   ⚠️  {merged_file} 存在但读取失败 / exists but read failed: {e}")
            return False
    else:
        print(f"   ❌ {merged_file} 不存在 / does not exist")
        print(f"      需要运行数据准备步骤 / Need to run data preparation:")
        print(f"      cd data && python get_daily_price.py && python merge_jsonl.py")
        return False
    
    # Check individual price files
    data_dir = Path('data')
    price_files = list(data_dir.glob('daily_prices_*.json'))
    if price_files:
        print(f"   ✅ 找到 / Found {len(price_files)} 个股票价格文件 / stock price files")
    else:
        print(f"   ⚠️  未找到股票价格文件 / No stock price files found")
    
    return True

def check_configs():
    """检查配置文件 / Check configuration files"""
    print("\n⚙️  检查配置文件 / Checking Configuration Files:")
    
    config_files = {
        'default_config.json': 'configs/default_config.json',
        'default_day_config.json': 'configs/default_day_config.json',
        'default_hour_config.json': 'configs/default_hour_config.json'
    }
    
    all_good = True
    for name, path in config_files.items():
        if not os.path.isfile(path):
            print(f"   ⚠️  {name} 不存在 / does not exist")
            continue
            
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            
            agent_type = config.get('agent_type', 'N/A')
            date_range = config.get('date_range', {})
            init_date = date_range.get('init_date', 'N/A')
            end_date = date_range.get('end_date', 'N/A')
            
            print(f"   ✅ {name}")
            print(f"      代理类型 / Agent Type: {agent_type}")
            print(f"      日期范围 / Date Range: {init_date} 到 / to {end_date}")
            
        except Exception as e:
            print(f"   ❌ {name} 解析失败 / parse failed: {e}")
            all_good = False
    
    return all_good

def check_env_example():
    """检查环境变量示例 / Check .env.example"""
    print("\n🔑 检查环境变量配置 / Checking Environment Configuration:")
    
    env_example = '.env.example'
    if os.path.isfile(env_example):
        print(f"   ✅ {env_example} 存在 / exists")
        with open(env_example, 'r') as f:
            lines = f.readlines()
        required_keys = ['OPENAI_API_KEY', 'ALPHAADVANTAGE_API_KEY']
        for key in required_keys:
            if any(key in line for line in lines):
                print(f"      ✅ 包含 / Contains {key}")
    else:
        print(f"   ❌ {env_example} 不存在 / does not exist")
        return False
    
    # Check if .env exists
    if os.path.isfile('.env'):
        print(f"   ✅ .env 文件已创建 / .env file created")
        print(f"      ⚠️  请确保已填写API密钥 / Please ensure API keys are filled in")
    else:
        print(f"   ⚠️  .env 文件未创建 / .env file not created")
        print(f"      运行 / Run: cp .env.example .env")
        print(f"      然后编辑 .env 填入API密钥 / Then edit .env to add API keys")
    
    return True

def test_import_modules():
    """测试导入关键模块 / Test importing key modules"""
    print("\n🧪 测试模块导入 / Testing Module Imports:")
    
    # Test module imports with validation functions
    modules_to_test = [
        ('tools.general_tools', 'get_config_value', None),
        ('tools.price_tools', 'get_open_prices', None),
        ('prompts.agent_prompt', 'all_nasdaq_100_symbols', 
         lambda x: f"包含 / Contains {len(x)} 个股票代码 / stock symbols"),
    ]
    
    all_good = True
    for test_info in modules_to_test:
        module_name, attr_name = test_info[0], test_info[1]
        validator = test_info[2] if len(test_info) > 2 else None
        
        try:
            module = __import__(module_name, fromlist=[attr_name])
            attr = getattr(module, attr_name)
            print(f"   ✅ {module_name}.{attr_name}")
            
            # Run validator if provided
            if validator and callable(validator):
                print(f"      {validator(attr)}")
                
        except Exception as e:
            print(f"   ❌ {module_name}.{attr_name}: {e}")
            all_good = False
    
    return all_good

def print_summary(results):
    """打印总结 / Print summary"""
    print("\n" + "="*60)
    print("📋 测试总结 / Test Summary")
    print("="*60)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ 通过 / PASSED" if passed else "❌ 失败 / FAILED"
        print(f"{status}: {test_name}")
    
    print("="*60)
    
    if all_passed:
        print("🎉 所有测试通过！项目设置正确。")
        print("🎉 All tests passed! Project setup is correct.")
        print("\n下一步 / Next Steps:")
        print("1. 确保 .env 文件已配置API密钥 / Ensure .env file has API keys")
        print("2. 启动MCP服务 / Start MCP services:")
        print("   cd agent_tools && python start_mcp_services.py")
        print("3. 运行AI交易 / Run AI trading:")
        print("   python main.py")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        print("⚠️  Some tests failed, please check the error messages above.")
    
    print("="*60)

def main():
    """主函数 / Main function"""
    print("="*60)
    print("🧪 AI-Trader 基本设置测试 / Basic Setup Test")
    print("="*60)
    
    results = {}
    
    # Run all checks
    results["Python版本 / Python Version"] = check_python_version()
    results["依赖包 / Dependencies"] = check_dependencies()
    results["项目结构 / Project Structure"] = check_project_structure()
    results["数据可用性 / Data Availability"] = check_data_availability()
    results["配置文件 / Configuration Files"] = check_configs()
    results["环境变量 / Environment Variables"] = check_env_example()
    results["模块导入 / Module Imports"] = test_import_modules()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
