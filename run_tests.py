#!/usr/bin/env python3
"""
SubModel SDK 测试运行脚本
使用此脚本可以运行各种类型的测试并生成报告
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """运行命令并打印结果"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"命令: {command}")
    print("-" * 60)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("📋 输出:")
        print(result.stdout)
    
    if result.stderr:
        print("⚠️ 错误/警告:")
        print(result.stderr)
    
    print(f"📊 退出代码: {result.returncode}")
    return result.returncode == 0

def main():
    """主函数"""
    # 确保在正确的目录中
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Python可执行文件路径
    python_cmd = r"python"
    
    print("🚀 SubModel SDK 测试套件")
    print("=" * 60)
    
    # 1. 检查pytest版本
    run_command(f"{python_cmd} -m pytest --version", "检查pytest版本")
    
    # 2. 收集所有测试
    run_command(f"{python_cmd} -m pytest --collect-only -q", "收集所有测试")
    
    # 3. 运行单个测试文件
    run_command(f"{python_cmd} -m pytest tests/test_auth.py -v", "运行认证测试")
    
    # 4. 运行异步测试
    run_command(f"{python_cmd} -m pytest tests/test_async_client.py -v", "运行异步客户端测试")
    
    # 5. 运行所有测试（简化输出）
    run_command(f"{python_cmd} -m pytest tests/ --tb=line", "运行所有测试（简化输出）")
    
    # 6. 生成覆盖率报告
    run_command(f"{python_cmd} -m pytest tests/ --cov=submodel --cov-report=term", "生成代码覆盖率报告")
    
    # 7. 运行特定标记的测试（如果配置了标记）
    run_command(f"{python_cmd} -m pytest tests/ -k auth", "运行包含'auth'的测试")
    
    print("\n🎉 测试完成！")
    print("=" * 60)
    print("📝 测试结果总结:")
    print("- 查看上面的输出了解每个测试的结果")
    print("- 红色 FAILED 表示测试失败")
    print("- 绿色 PASSED 表示测试通过")
    print("- 黄色 SKIPPED 表示测试被跳过")
    print("- 覆盖率报告显示了代码的测试覆盖程度")

if __name__ == "__main__":
    main()
