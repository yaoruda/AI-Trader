# AI-Trader 项目分析总结 / Project Analysis Summary

## 📊 项目概况 / Project Overview

**AI-Trader** 是一个基于大语言模型（LLM）的自主交易竞技平台，让多个AI模型在纳斯达克100股票池中完全自主决策、同台竞技。

**AI-Trader** is an autonomous trading competition platform based on Large Language Models (LLMs), enabling multiple AI models to compete in trading NASDAQ 100 stocks with complete autonomy.

---

## 🏗️ 项目架构解析 / Architecture Analysis

### 核心组件 / Core Components

1. **AI代理层 / AI Agent Layer**
   - `agent/base_agent/base_agent.py` - 日级别交易代理（每天交易一次）
   - `agent/base_agent/base_agent_hour.py` - 小时级别交易代理（每小时交易一次）

2. **MCP工具层 / MCP Tool Layer**
   - `agent_tools/tool_trade.py` - 交易执行工具（买入/卖出）
   - `agent_tools/tool_get_price_local.py` - 价格查询工具
   - `agent_tools/tool_jina_search.py` - 市场信息搜索工具
   - `agent_tools/tool_math.py` - 数学计算工具
   - `agent_tools/start_mcp_services.py` - MCP服务启动管理

3. **数据层 / Data Layer**
   - `data/daily_prices_*.json` - 股票价格数据（60分钟K线）
   - `data/merged.jsonl` - 合并后的统一数据格式
   - `data/agent_data/<signature>/` - 各AI代理的交易记录和持仓

4. **配置层 / Configuration Layer**
   - `configs/default_config.json` - 默认配置
   - `configs/default_day_config.json` - 日级别配置示例
   - `configs/default_hour_config.json` - 小时级别配置示例

### 技术栈 / Technology Stack

- **LangChain** - AI应用开发框架
- **MCP (Model Context Protocol)** - 工具协议标准
- **FastMCP** - MCP服务实现框架
- **Python 3.10+** - 编程语言

---

## ⏰ 交易时间级别说明 / Trading Timeframe Explanation

### 1. 日级别交易 / Daily Trading

**配置**: `"agent_type": "BaseAgent"`

**特点**:
- ✅ 交易频率：每个交易日一次
- ✅ 价格基准：当日开盘价
- ✅ 适用场景：长期投资策略、基本面分析

**数据来源**: 虽然原始数据是60分钟K线，但日级别代理每天只在开盘时执行一次交易决策。

**配置示例**:
```json
{
  "agent_type": "BaseAgent",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-31"
  }
}
```

### 2. 小时级别交易 / Hourly Trading

**配置**: `"agent_type": "BaseAgent_Hour"`

**特点**:
- ✅ 交易频率：每小时一次（交易时段内）
- ✅ 价格基准：每小时开盘价
- ✅ 适用场景：日内交易、短期波动捕捉

**数据来源**: 直接使用60分钟K线数据，每小时都可能触发交易决策。

**配置示例**:
```json
{
  "agent_type": "BaseAgent_Hour",
  "date_range": {
    "init_date": "2025-10-01 09:00:00",
    "end_date": "2025-10-31 16:00:00"
  }
}
```

**数据格式**:
```json
{
  "Time Series (60min)": {
    "2025-10-01 09:00:00": {
      "1. open": "150.00",
      "2. high": "151.00",
      "3. low": "149.50",
      "4. close": "150.75",
      "5. volume": "1234567"
    }
  }
}
```

---

## 🔌 真实账户接入扩展性 / Real Account Integration Extensibility

### 当前架构

```
AI代理 → MCP工具 → 模拟交易（本地JSON文件）
```

### 扩展路径

AI-Trader的MCP架构使得接入真实交易账户成为可能：

```
AI代理 → MCP工具 → 交易API/MCP → 真实券商账户
```

### 实现方案

#### 方案1：修改现有工具

在 `agent_tools/tool_trade.py` 中添加真实交易接口：

```python
@mcp.tool()
def buy(symbol: str, amount: int) -> Dict[str, Any]:
    if get_config_value("REAL_TRADING_MODE"):
        # 调用真实交易API
        result = real_broker_api.place_order(...)
        return result
    else:
        # 原有模拟交易逻辑
        ...
```

#### 方案2：创建新的MCP服务

创建 `agent_tools/tool_real_broker.py`：

```python
from fastmcp import FastMCP
import broker_sdk

mcp = FastMCP("RealBroker")

@mcp.tool()
def place_real_order(symbol: str, side: str, quantity: int):
    client = broker_sdk.Client(api_key=..., secret=...)
    return client.create_order(...)
```

然后在MCP配置中添加此服务。

#### 方案3：使用现有MCP服务

如果你已经有了交易MCP服务器（如券商提供的MCP接口），可直接在配置中添加：

```python
self.mcp_config = {
    "broker_mcp": {
        "url": "http://your-broker-mcp-server:port/sse",
        "name": "YourBrokerMCP"
    }
}
```

### 支持的券商平台 / Supported Brokers

**理论上可接入任何提供API的平台**:

- **美股**: Interactive Brokers, Alpaca, TD Ameritrade, Robinhood
- **中国A股**: 东方财富、同花顺、雪球
- **加密货币**: Binance, Coinbase, OKX

### 安全性建议 / Security Recommendations

⚠️ **在接入真实账户前必须考虑**:

1. **风险控制**
   - 设置单笔交易限额
   - 设置日总交易限额
   - 实现紧急停止机制

2. **API密钥安全**
   - 使用环境变量存储
   - 限制API权限（只读、只交易、不提现）
   - 定期轮换密钥

3. **测试充分**
   - 先在模拟账户测试
   - 使用小额资金试运行
   - 监控所有交易行为

4. **合规性**
   - 确认当地法规允许算法交易
   - 遵守券商使用条款
   - 考虑税务影响

### 推荐扩展步骤

1. **阶段1：模拟环境测试**（✅ 当前阶段）
   - 使用本地数据完善策略
   - 验证AI决策逻辑

2. **阶段2：券商模拟账户**
   - 接入券商Paper Trading API
   - 使用真实市场数据，虚拟资金

3. **阶段3：小额真实交易**
   - 使用少量资金（$100-$1000）
   - 严格风控参数
   - 密切监控

4. **阶段4：逐步扩大规模**
   - 根据表现调整资金规模
   - 持续优化策略和风控

---

## 🎯 主要逻辑流程 / Main Logic Flow

### 1. 初始化阶段 / Initialization Phase

```
1. 加载配置文件 (configs/*.json)
2. 初始化AI代理 (BaseAgent/BaseAgent_Hour)
3. 连接MCP服务 (Trading, Price, Search, Math)
4. 连接LLM模型 (OpenAI/Claude/etc.)
```

### 2. 交易循环 / Trading Loop

```
对于每个交易日期/时间:
  1. 更新系统提示词（包含当前日期）
  2. AI代理接收用户查询："Please analyze and update today's positions"
  3. AI调用MCP工具：
     - get_price_local(): 查询股票价格
     - get_information(): 搜索市场新闻
     - 其他分析工具
  4. AI基于工具返回结果进行推理
  5. AI决定是否交易：
     - buy(symbol, amount): 买入股票
     - sell(symbol, amount): 卖出股票
  6. 记录交易日志和持仓变化
  7. 检查停止信号或达到最大步数
```

### 3. 数据记录 / Data Recording

**持仓记录** (`position.jsonl`):
```json
{
  "date": "2025-10-01",
  "id": 1,
  "this_action": {"action": "buy", "symbol": "AAPL", "amount": 10},
  "positions": {"AAPL": 10, "CASH": 9500.0}
}
```

**交易日志** (`log/<date>/log.jsonl`):
```json
{"role": "user", "content": "Please analyze..."}
{"role": "assistant", "content": "AI reasoning..."}
{"role": "tool", "tool_name": "get_price_local", "content": "..."}
```

---

## 📝 新增文档说明 / New Documentation

### 1. QUICKSTART_CN.md

**详细的中文快速上手指南**，包含：

- ✅ 项目架构详解
- ✅ 安装步骤详解
- ✅ 交易时间级别对比（日级别 vs 小时级别）
- ✅ 真实账户接入指南
- ✅ 数据格式说明
- ✅ 常见问题解答
- ✅ 进阶使用技巧

**适用人群**：
- 🎯 刚接触这个项目的新用户
- 🎯 想了解如何运行基础预测的用户
- 🎯 计划扩展到真实交易的用户

### 2. test_basic_setup.py

**项目设置验证脚本**，检查：

- ✅ Python版本是否符合要求（>= 3.10）
- ✅ 依赖包是否正确安装
- ✅ 项目结构是否完整
- ✅ 数据文件是否存在
- ✅ 配置文件是否有效
- ✅ 环境变量配置
- ✅ 核心模块导入测试

**使用方法**:
```bash
python test_basic_setup.py
```

输出示例：
```
🧪 AI-Trader 基本设置测试 / Basic Setup Test
============================================================
✅ 通过 / PASSED: Python版本 / Python Version
✅ 通过 / PASSED: 依赖包 / Dependencies
✅ 通过 / PASSED: 项目结构 / Project Structure
...
🎉 所有测试通过！项目设置正确。
```

---

## 🚀 快速运行指南 / Quick Run Guide

### 最基础的预测运行 / Running Basic Predictions

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   python test_basic_setup.py  # 验证安装
   ```

2. **配置API密钥**
   ```bash
   cp .env.example .env
   # 编辑 .env，至少填入 OPENAI_API_KEY
   ```

3. **数据已准备好**（当前仓库已包含）
   - ✅ `data/merged.jsonl` - 101支股票的60分钟K线数据
   - ✅ `data/daily_prices_*.json` - 各股票独立数据文件

4. **启动MCP服务**
   ```bash
   cd agent_tools
   python start_mcp_services.py
   ```
   保持此终端运行

5. **运行AI交易**（新终端）
   ```bash
   python main.py
   # 或使用自定义配置
   python main.py configs/default_day_config.json
   ```

6. **查看结果**
   ```bash
   # 持仓记录
   cat data/agent_data/gpt-5/position/position.jsonl
   
   # 交易日志
   ls data/agent_data/gpt-5/log/
   ```

---

## 📊 配置说明 / Configuration Guide

### 日级别交易配置 / Daily Trading Config

```json
{
  "agent_type": "BaseAgent",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-21"
  },
  "models": [
    {
      "name": "gpt-4o",
      "basemodel": "openai/gpt-4o",
      "signature": "gpt-4o",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "initial_cash": 10000.0
  }
}
```

### 小时级别交易配置 / Hourly Trading Config

```json
{
  "agent_type": "BaseAgent_Hour",
  "date_range": {
    "init_date": "2025-10-23 14:00:00",
    "end_date": "2025-10-27 19:00:00"
  },
  "models": [
    {
      "name": "gpt-4o",
      "basemodel": "openai/gpt-4o",
      "signature": "gpt-4o-hour",
      "enabled": true
    }
  ]
}
```

---

## 🎓 关键概念解释 / Key Concepts

### MCP (Model Context Protocol)

MCP是一个标准化协议，允许AI模型通过统一接口调用各种工具：

- **工具定义**: 使用 `@mcp.tool()` 装饰器定义
- **工具服务**: 通过HTTP服务暴露（FastMCP）
- **工具调用**: AI模型通过LangChain调用MCP工具

### Agent（代理）

AI代理是整个系统的核心决策单元：

- **输入**: 当前日期、市场数据、持仓信息
- **处理**: 通过LLM推理和MCP工具调用
- **输出**: 交易决策（买入/卖出/持有）

### Signature（签名）

每个AI模型的唯一标识符，用于：

- 区分不同模型的数据存储
- 独立记录各模型的交易历史
- 支持多模型并行运行

---

## 💡 后续可能的扩展方向 / Possible Extensions

1. **多市场支持**
   - A股市场
   - 加密货币
   - 外汇市场

2. **高级策略**
   - 技术分析指标
   - 量化因子模型
   - 风险管理策略

3. **实时交易**
   - WebSocket实时数据
   - 毫秒级别交易
   - 高频交易支持

4. **性能优化**
   - 并行化处理
   - 缓存机制
   - 数据库存储

5. **可视化增强**
   - 实时交易监控
   - 策略回测对比
   - 收益曲线分析

---

## ⚖️ 免责声明 / Disclaimer

本项目及文档仅供学习和研究使用，不构成任何投资建议。

This project and documentation are for educational and research purposes only and do not constitute investment advice.

---

## 📞 获取帮助 / Getting Help

- **GitHub Issues**: https://github.com/HKUDS/AI-Trader/issues
- **详细指南**: [QUICKSTART_CN.md](QUICKSTART_CN.md)
- **项目README**: [README_CN.md](README_CN.md)

---

**文档创建时间**: 2025-11-03
**适用版本**: AI-Trader 当前版本
