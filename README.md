# Balance Management System

三方服务费用余额和用量管理系统

---

## 📋 项目信息

| 项目 | 值 |
|------|-----|
| 名称 | balance-manager |
| 版本 | 1.0.0 |
| 创建日期 | 2026-03-10 |
| 状态 | ✅ Complete |

---

## 🎯 目标

实现一个 Python 系统，用于管理多个 AI/ML 平台的余额和用量：

1. **自动查询** - API 可用的平台自动查询余额
2. **手动录入** - 无 API 的平台支持手动录入
3. **统一视图** - 所有平台余额汇总展示
4. **告警通知** - 余额低于阈值时告警

---

## 📁 目录结构

```
balance-manager/
├── config.yaml           # 项目配置
├── requirements/         # 需求文档
│   └── prds/            # PRD 文档
├── specs/               # 设计文档
├── src/                 # 源代码
│   ├── core/            # 核心模块
│   ├── providers/       # 平台 Provider
│   ├── storage/         # 存储后端
│   ├── cli/             # 命令行界面
│   └── config/          # 配置管理
├── tests/               # 测试代码
├── docs/                # 文档
└── logs/                # 日志
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
balance-manager init
# 编辑 ~/.balance_manager/config.yaml 添加 API Key
```

### 3. 查询余额

```bash
# 查询所有平台
balance-manager check

# 查询指定平台
balance-manager check --platform openrouter

# 查看汇总
balance-manager summary
```

---

## 📊 工作流状态

| 阶段 | 状态 | 负责人 | 完成时间 |
|------|------|--------|----------|
| PRD 审查 | ✅ Complete | PM | 2026-03-10 |
| 技术设计 | ✅ Complete | Architect | 2026-03-10 |
| 代码实现 | ✅ Complete | Coder | 2026-03-11 |
| 代码审查 | ✅ Complete | Reviewer | 2026-03-11 |

---

## 📝 需求列表

| ID | 需求名称 | 优先级 | 状态 | PRD |
|----|----------|--------|------|-----|
| REQ-001 | 三方服务余额管理系统 | High | ✅ Complete | [PRD](../../shared-memory/requirements.md) |

---

## 🛠️ 技术栈

- **语言**: Python 3.6+
- **CLI**: Click
- **配置**: PyYAML
- **HTTP**: Requests
- **测试**: Pytest

---

## 📦 支持平台

| # | 平台 | 查询方式 | 状态 |
|---|------|----------|------|
| 1 | OpenRouter | API | ✅ |
| 2 | MiniMax (海螺 AI) | API | ✅ |
| 3 | Volcengine (火山方舟) | API | ✅ |
| 4 | BFL (Kontext) | API | ✅ |
| 5 | Aliyun (悠船) | 手动 | ✅ |
| 6 | Kling AI (可灵) | 手动 | ✅ |
| 7 | PixVerse | 手动 | ✅ |
| 8 | MiracleVision (美图) | 手动 | ✅ |

---

## 🧪 测试结果

```
==================================================
       BALANCE SYSTEM TEST SUITE
==================================================
Results: 12 passed, 0 failed out of 12 tests
==================================================
```

---

## 📖 相关文档

- [设计文档](docs/design.md)
- [使用指南](docs/usage.md)

---

## 📞 联系方式

- **项目主页**: https://github.com/openclaw/balance-manager
- **Issues**: https://github.com/openclaw/balance-manager/issues

---

*此项目由 OpenClaw Multi-Agent Framework 驱动*
