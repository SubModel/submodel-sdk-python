# SubModel SDK 测试指南

## 概述

本项目使用 **pytest** 作为主要测试框架，包含了完整的测试套件来验证 SDK 的各个功能模块。

## 项目测试结构

```
tests/
├── test_auth.py          # 认证功能测试
├── test_async_client.py  # 异步客户端测试
├── test_cli.py           # 命令行界面测试
├── test_device.py        # 设备管理测试
├── test_instance.py      # 实例管理测试
├── test_retry.py         # 重试机制测试
└── test_serverless.py    # 无服务器功能测试
```

## 测试环境设置

### 1. 激活虚拟环境
```powershell
# Windows PowerShell
.\submodel-env\Scripts\Activate.ps1

# 或者直接使用完整路径
.\submodel-env\Scripts\python.exe
```

### 2. 安装测试依赖
```powershell
.\submodel-env\Scripts\python.exe -m pip install pytest pytest-asyncio pytest-cov
```

## 基本测试命令

### 1. 运行所有测试
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/
```

### 2. 运行单个测试文件
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/test_auth.py
```

### 3. 运行特定测试函数
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/test_auth.py::TestAuth::test_register
```

### 4. 运行特定测试类
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/test_auth.py::TestAuth
```

## 高级测试选项

### 1. 详细输出 (-v)
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ -v
```

### 2. 显示测试覆盖率
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ --cov=submodel
```

### 3. 生成HTML覆盖率报告
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ --cov=submodel --cov-report=html
```

### 4. 只收集测试，不运行
```powershell
.\submodel-env\Scripts\python.exe -m pytest --collect-only tests/
```

### 5. 运行失败时立即停止
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ -x
```

### 6. 重新运行上次失败的测试
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ --lf
```

### 7. 按关键字筛选测试
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ -k "auth"
```

## 异步测试

项目中的异步测试使用 `pytest-asyncio` 插件：

```python
import unittest

class TestAsyncClient(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """异步设置"""
        self.client = AsyncSubModelClient(token="test-token")
        await self.client.__aenter__()

    async def asyncTearDown(self):
        """异步清理"""
        await self.client.__aexit__(None, None, None)

    async def test_async_function(self):
        """异步测试函数"""
        result = await self.client.get("test/endpoint")
        self.assertEqual(result["code"], 20000)
```

## 模拟和测试数据

### 使用 unittest.mock 进行模拟

```python
from unittest.mock import patch, MagicMock

@patch('requests.request')
def test_api_call(self, mock_request):
    # 模拟HTTP响应
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": 20000, "data": "success"}
    mock_request.return_value = mock_response
    
    # 执行测试
    result = self.client.some_method()
    self.assertEqual(result["code"], 20000)
```

## 测试最佳实践

### 1. 测试命名约定
- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试函数: `test_*`

### 2. 测试结构
```python
class TestFeature(unittest.TestCase):
    def setUp(self):
        """每个测试前的设置"""
        pass
    
    def tearDown(self):
        """每个测试后的清理"""
        pass
    
    def test_feature_success(self):
        """测试成功场景"""
        pass
    
    def test_feature_error(self):
        """测试错误场景"""
        pass
```

### 3. 断言示例
```python
# 基本断言
self.assertEqual(actual, expected)
self.assertTrue(condition)
self.assertFalse(condition)
self.assertIsNone(value)
self.assertIsNotNone(value)

# 异常断言
with self.assertRaises(ValueError):
    some_function_that_should_raise()

# 近似值断言
self.assertAlmostEqual(3.14159, 3.14, places=2)
```

## 持续集成配置

### 创建 .github/workflows/test.yml
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=submodel --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 调试测试

### 1. 在测试中设置断点
```python
import pdb; pdb.set_trace()  # Python调试器
```

### 2. 打印调试信息
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. 运行单个测试进行调试
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/test_auth.py::TestAuth::test_register -s -v
```

## 性能测试

### 使用 pytest-benchmark
```python
def test_performance(benchmark):
    result = benchmark(expensive_function, arg1, arg2)
    assert result == expected_value
```

## 故障排除

### 常见问题及解决方案

1. **导入错误**
   ```
   确保PYTHONPATH包含项目根目录
   或者使用 pip install -e . 安装为开发包
   ```

2. **异步测试问题**
   ```
   确保安装了 pytest-asyncio
   使用 unittest.IsolatedAsyncioTestCase 作为基类
   ```

3. **模拟问题**
   ```
   检查模拟的路径是否正确
   使用 where 方法找到正确的导入路径
   ```

## 测试报告

### 生成详细的HTML报告
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ --html=report.html --self-contained-html
```

### 生成JUnit XML报告
```powershell
.\submodel-env\Scripts\python.exe -m pytest tests/ --junitxml=report.xml
```

## 总结

这个测试框架提供了：
- ✅ 全面的单元测试覆盖
- ✅ 异步代码测试支持
- ✅ HTTP请求模拟
- ✅ 代码覆盖率报告
- ✅ 易于扩展的测试结构
- ✅ CI/CD集成支持

通过遵循这些指南，您可以有效地测试和验证 SubModel SDK 的功能。
