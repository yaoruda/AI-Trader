# AI-Trader 快速上手指南

## 📖 项目概述

**AI-Trader** 是一个基于大语言模型（LLM）的AI自主交易竞技平台，让多个AI模型在纳斯达克100股票池中完全自主决策、同台竞技，无需人工干预。

### 🎯 核心特点

- **🤖 完全自主决策**：AI代理100%独立分析、决策、执行，零人工干预
- **🛠️ 纯工具驱动**：基于MCP（Model Context Protocol）工具链
- **🏆 多模型竞技**：支持多个AI模型（GPT、Claude、Qwen等）同时运行
- **📊 历史回放**：可以在任意历史时间段进行回测，自动过滤未来信息
- **⏰ 灵活时间粒度**：支持日级别（daily）和小时级别（hourly）交易

---

## 🏗️ 项目架构

### 主要组件

```
AI-Trader/
├── main.py                    # 主程序入口
├── agent/                     # AI代理核心
│   └── base_agent/
│       ├── base_agent.py      # 日级别交易代理
│       └── base_agent_hour.py # 小时级别交易代理
├── agent_tools/               # MCP工具集
│   ├── tool_trade.py          # 交易工具（买入/卖出）
│   ├── tool_get_price_local.py # 价格查询工具
│   ├── tool_jina_search.py    # 市场信息搜索工具
│   ├── tool_math.py           # 数学计算工具
│   └── start_mcp_services.py  # MCP服务启动脚本
├── data/                      # 数据目录
│   ├── daily_prices_*.json    # 股票价格数据（60分钟K线）
│   ├── merged.jsonl           # 合并后的统一数据格式
│   └── agent_data/            # AI交易记录和持仓
├── configs/                   # 配置文件
│   ├── default_config.json    # 默认配置
│   ├── default_day_config.json   # 日级别配置示例
│   └── default_hour_config.json  # 小时级别配置示例
├── prompts/                   # AI提示词
└── tools/                     # 辅助工具
```

### 核心逻辑流程

1. **数据准备**：下载纳斯达克100股票的历史价格数据
2. **MCP服务启动**：启动交易、价格查询、搜索等MCP服务
3. **AI代理初始化**：创建AI代理实例，连接到LLM和MCP工具
4. **交易循环**：
   - AI代理接收当前日期/时间
   - 通过MCP工具查询价格、搜索市场信息
   - AI自主分析决策
   - 通过交易工具执行买入/卖出
   - 记录交易日志和持仓变化
5. **结果分析**：生成收益报告和性能分析

---

## 🚀 快速开始

### 📋 前置要求

- **Python 3.10+**
- **API密钥**：
  - OpenAI API Key（或其他兼容OpenAI接口的模型API）
  - Alpha Vantage API Key（用于获取股票数据）
  - Jina AI API Key（用于市场信息搜索，可选）

### 步骤 1：克隆项目并安装依赖

```bash
# 克隆项目
git clone https://github.com/HKUDS/AI-Trader.git
cd AI-Trader

# 安装依赖
pip install -r requirements.txt
```

**核心依赖**：
- `langchain` - AI应用开发框架
- `langchain-openai` - OpenAI集成
- `langchain-mcp-adapters` - MCP协议适配器
- `fastmcp` - MCP服务框架

### 步骤 2：配置环境变量

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```bash
# AI模型API配置
OPENAI_API_BASE=https://api.openai.com/v1  # 或你的代理地址
OPENAI_API_KEY=sk-your-openai-api-key

# 数据源配置
ALPHAADVANTAGE_API_KEY=your_alpha_vantage_key
JINA_API_KEY=your_jina_api_key  # 可选

# 服务端口配置（默认值，可不修改）
MATH_HTTP_PORT=8000
SEARCH_HTTP_PORT=8001
TRADE_HTTP_PORT=8002
GETPRICE_HTTP_PORT=8003

# AI代理配置
AGENT_MAX_STEP=30  # AI最大推理步数
```

**获取API密钥**：
- **OpenAI API**: https://platform.openai.com/api-keys
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key (免费)
- **Jina AI**: https://jina.ai/ (可选，用于高级搜索)

### 步骤 3：准备数据

获取纳斯达克100股票的历史价格数据：

```bash
cd data
python get_daily_price.py

# 合并数据为统一格式
python merge_jsonl.py

cd ..
```

**注意**：
- `get_daily_price.py` 会从Alpha Vantage下载所有纳斯达克100股票的60分钟K线数据
- 数据会保存为 `daily_prices_<SYMBOL>.json` 格式
- `merge_jsonl.py` 将所有数据合并为 `merged.jsonl` 供AI代理使用

### 步骤 4：启动MCP服务

在新的终端窗口中启动MCP服务：

```bash
cd agent_tools
python start_mcp_services.py
```

你应该看到类似输出：

```
🚀 Starting MCP services...
==================================================
📊 Port configuration:
  - Math: 8000
  - Search: 8001
  - TradeTools: 8002
  - LocalPrices: 8003

✅ Math service started (PID: 12345, Port: 8000)
✅ Search service started (PID: 12346, Port: 8001)
✅ TradeTools service started (PID: 12347, Port: 8002)
✅ LocalPrices service started (PID: 12348, Port: 8003)

🎉 All MCP services started!
```

**保持此终端运行**，MCP服务需要在后台持续运行。

### 步骤 5：配置并运行AI交易

编辑配置文件 `configs/default_config.json`：

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
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

**关键配置说明**：
- `agent_type`: 代理类型
  - `"BaseAgent"` - 日级别交易（每天交易一次）
  - `"BaseAgent_Hour"` - 小时级别交易（每小时交易一次）
- `date_range`: 回测时间范围
  - `init_date`: 开始日期（格式：YYYY-MM-DD）
  - `end_date`: 结束日期
- `models`: 启用的AI模型列表
  - `enabled: true` - 启用此模型
  - `basemodel` - 模型标识符（支持OpenRouter格式）
  - `signature` - 模型签名（用于区分不同模型的数据）
- `agent_config`:
  - `max_steps`: AI最大推理步数（每次交易会话）
  - `initial_cash`: 初始资金（美元）

在新的终端窗口中运行主程序：

```bash
python main.py
```

或使用自定义配置：

```bash
python main.py configs/my_config.json
```

### 步骤 6：查看结果

AI代理运行后，数据会保存在 `data/agent_data/<signature>/` 目录：

```bash
# 查看持仓记录
cat data/agent_data/gpt-4o/position/position.jsonl

# 查看交易日志
ls data/agent_data/gpt-4o/log/
```

**持仓记录示例**：
```json
{
  "date": "2025-10-01",
  "id": 1,
  "this_action": {
    "action": "buy",
    "symbol": "AAPL",
    "amount": 10
  },
  "positions": {
    "AAPL": 10,
    "CASH": 9500.0
  }
}
```

---

## ⏰ 交易时间级别说明

### 1. 日级别交易（Daily Trading）

**配置**：`"agent_type": "BaseAgent"`

- **交易频率**：每个交易日一次
- **价格基准**：使用当日开盘价进行交易
- **数据格式**：虽然原始数据是60分钟K线，但日级别代理只在每天开盘时执行一次
- **适用场景**：
  - 长期投资策略
  - 基本面分析
  - 趋势跟踪策略

**示例配置**：
```json
{
  "agent_type": "BaseAgent",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-31"
  }
}
```

### 2. 小时级别交易（Hourly Trading）

**配置**：`"agent_type": "BaseAgent_Hour"`

- **交易频率**：每小时一次（交易时段内）
- **价格基准**：使用每小时的开盘价
- **数据格式**：使用60分钟K线数据
- **时间格式**：`"2025-10-01 09:00:00"`
- **适用场景**：
  - 日内交易策略
  - 短期波动捕捉
  - 事件驱动交易

**示例配置**：
```json
{
  "agent_type": "BaseAgent_Hour",
  "date_range": {
    "init_date": "2025-10-01 09:00:00",
    "end_date": "2025-10-31 16:00:00"
  }
}
```

**数据结构**：
```json
{
  "Meta Data": {
    "2. Symbol": "AAPL",
    "4. Interval": "60min"
  },
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

## 🔌 扩展性：接入真实账户

AI-Trader项目采用**模块化MCP工具架构**，使得接入真实交易账户成为可能。以下是扩展路径：

### 当前架构

```
AI代理 → MCP工具 → 模拟交易（读写本地JSON文件）
```

### 真实交易架构

```
AI代理 → MCP工具 → 交易API/MCP → 真实券商账户
```

### 实现方案

#### 方案1：修改现有MCP工具

修改 `agent_tools/tool_trade.py`，添加真实交易接口：

```python
@mcp.tool()
def buy(symbol: str, amount: int) -> Dict[str, Any]:
    """买入股票"""
    
    # 判断是否为真实交易模式
    if get_config_value("REAL_TRADING_MODE"):
        # 调用真实交易API
        result = real_broker_api.place_order(
            symbol=symbol,
            side='buy',
            quantity=amount
        )
        # 记录到数据库
        save_real_trade_record(result)
        return result
    else:
        # 原有的模拟交易逻辑
        # ... 现有代码 ...
```

**需要实现的API**：
- `place_order()` - 下单
- `get_account_balance()` - 获取账户余额
- `get_positions()` - 获取持仓
- `cancel_order()` - 撤单

#### 方案2：创建新的MCP服务

创建一个新的MCP服务作为中间层：

```python
# agent_tools/tool_real_broker.py
from fastmcp import FastMCP
import broker_sdk  # 券商SDK

mcp = FastMCP("RealBroker")

@mcp.tool()
def place_real_order(symbol: str, side: str, quantity: int):
    """真实下单"""
    client = broker_sdk.Client(api_key=..., secret=...)
    order = client.create_order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type='market'
    )
    return order

@mcp.tool()
def get_real_positions():
    """获取真实持仓"""
    client = broker_sdk.Client(api_key=..., secret=...)
    return client.get_positions()
```

然后在配置中添加此服务：

```python
# main.py 中添加
mcp_config = {
    "real_broker": {
        "url": "http://localhost:8005/sse",
        "name": "RealBroker"
    }
}
```

#### 方案3：使用MCP作为代理

如果你已经有了交易MCP服务器，可以直接在配置中添加：

```python
# 在 BaseAgent 的 mcp_config 中添加
self.mcp_config = {
    # 原有服务...
    "broker_mcp": {
        "url": "http://your-broker-mcp-server:port/sse",
        "name": "YourBrokerMCP"
    }
}
```

### 支持的券商/交易平台

理论上可以接入任何提供API的平台：

**美股**：
- Interactive Brokers (IBKR) - 提供API
- Alpaca - 专为算法交易设计
- TD Ameritrade - 提供ThinkorSwim API
- Robinhood - 非官方API

**中国A股**：
- 东方财富 - 量化交易接口
- 同花顺 - iFinD接口
- 雪球 - 非官方API

**加密货币**：
- Binance - WebSocket API
- Coinbase - REST API
- OKX - 交易API

### 安全性考虑

⚠️ **在接入真实账户前，务必考虑**：

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
   - 遵守券商的使用条款
   - 考虑税务影响

### 推荐的扩展步骤

1. **阶段1：模拟环境测试**（当前阶段）
   - 使用本地数据完善策略
   - 验证AI决策逻辑

2. **阶段2：券商模拟账户**
   - 接入券商提供的Paper Trading API
   - 使用真实市场数据，但虚拟资金

3. **阶段3：小额真实交易**
   - 使用少量资金（如$100-$1000）
   - 严格的风控参数
   - 密切监控

4. **阶段4：逐步扩大规模**
   - 根据表现调整资金规模
   - 持续优化策略和风控

---

## 📊 数据格式说明

### 价格数据（merged.jsonl）

每行是一个股票的完整历史数据：

```json
{
  "Meta Data": {
    "2. Symbol": "AAPL",
    "3. Last Refreshed": "2025-10-31 15:00:00",
    "4. Interval": "60min"
  },
  "Time Series (60min)": {
    "2025-10-31 15:00:00": {
      "1. open": "255.88",
      "2. high": "256.50",
      "3. low": "255.00",
      "4. close": "256.00",
      "5. volume": "1234567"
    }
  }
}
```

### 持仓记录（position.jsonl）

每次交易后追加一行：

```json
{
  "date": "2025-10-01",
  "id": 1,
  "this_action": {
    "action": "buy",
    "symbol": "AAPL",
    "amount": 10
  },
  "positions": {
    "AAPL": 10,
    "MSFT": 5,
    "CASH": 9500.0
  }
}
```

### 交易日志（log.jsonl）

记录AI的完整思考过程：

```json
{
  "role": "user",
  "content": "Please analyze and update today's (2025-10-01) positions."
}
{
  "role": "assistant",
  "content": "Let me check current market conditions..."
}
{
  "role": "tool",
  "tool_name": "get_price_local",
  "content": "{\"AAPL_price\": 150.0, ...}"
}
```

---

## 🛠️ 常见问题

### Q1: MCP服务启动失败？

**检查端口占用**：
```bash
# Linux/Mac
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003

# Windows
netstat -ano | findstr :8000
```

**解决方法**：
- 修改 `.env` 中的端口配置
- 或关闭占用端口的程序

### Q2: API密钥错误？

确保 `.env` 文件中的密钥正确：
```bash
# 测试OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 测试Alpha Vantage API
curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=60min&apikey=$ALPHAADVANTAGE_API_KEY"
```

### Q3: 数据下载失败？

Alpha Vantage免费版有请求限制（5 requests/min, 500 requests/day）：
- 修改 `data/get_daily_price.py` 添加更长的延迟
- 或使用付费API密钥

### Q4: AI没有执行交易？

检查：
1. MCP服务是否正常运行
2. `max_steps` 是否足够（建议30以上）
3. 查看日志文件了解AI的决策过程

### Q5: 如何使用其他AI模型？

修改配置文件中的 `basemodel`：

```json
{
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7",
      "enabled": true
    },
    {
      "name": "deepseek",
      "basemodel": "deepseek/deepseek-chat-v3.1",
      "signature": "deepseek",
      "enabled": true
    }
  ]
}
```

如果使用OpenRouter等代理服务：
```json
{
  "openai_base_url": "https://openrouter.ai/api/v1",
  "openai_api_key": "your-openrouter-key"
}
```

---

## 📚 进阶使用

### 多模型并行竞技

在配置中启用多个模型：

```json
{
  "models": [
    {"name": "gpt-4o", "basemodel": "openai/gpt-4o", "signature": "gpt-4o", "enabled": true},
    {"name": "claude-3.7", "basemodel": "anthropic/claude-3.7-sonnet", "signature": "claude-3.7", "enabled": true},
    {"name": "qwen3-max", "basemodel": "qwen/qwen3-max", "signature": "qwen3-max", "enabled": true}
  ]
}
```

每个模型会独立运行，数据保存在各自的 `signature` 目录下。

### 自定义交易策略

继承 `BaseAgent` 创建自定义代理：

```python
# agent/custom/my_agent.py
from agent.base_agent.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 自定义初始化
    
    async def run_trading_session(self, today_date: str):
        # 自定义交易逻辑
        # 可以修改提示词、添加额外工具等
        pass
```

注册到 `main.py`：

```python
AGENT_REGISTRY = {
    "BaseAgent": {...},
    "MyCustomAgent": {
        "module": "agent.custom.my_agent",
        "class": "MyCustomAgent"
    }
}
```

### 性能分析

项目提供了性能分析工具（需要自己实现或参考示例）：

```bash
# 计算收益率、夏普比率、最大回撤等
python calculate_performance.py --signature gpt-4o
```

---

## 🎓 学习资源

- **LangChain文档**: https://python.langchain.com/
- **MCP协议**: https://github.com/modelcontextprotocol
- **Alpha Vantage API**: https://www.alphavantage.co/documentation/
- **量化交易入门**: https://www.quantstart.com/

---

## ⚖️ 免责声明

本项目仅供学习和研究使用，**不构成任何投资建议**。

- 历史回测结果不代表未来表现
- AI决策可能存在错误和偏差
- 真实交易存在本金损失风险
- 使用者需自行承担所有交易风险
- 请在充分了解风险的情况下进行任何投资决策

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/HKUDS/AI-Trader/issues
- **讨论区**: https://github.com/HKUDS/AI-Trader/discussions

---

**祝你使用愉快！🚀**
