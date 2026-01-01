# 居民用电分析和节能建议智能体系统

> 基于深度学习的智能用电行为分析与个性化节能建议系统

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.8.0-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📖 项目简介

本项目是一个面向居民的智能用电分析与节能建议系统，通过现代AI技术分析家庭用电行为，自动生成可视化报告并提供个性化节能建议。系统结合传统统计分析、深度学习模型（LSTM + Autoencoder）和大语言模型（LLM Agent），为用户提供全方位的用电分析和智能化交互体验。

### 核心价值

- **实用性**：帮助居民理解用电行为，降低电费支出
- **技术性**：从零训练神经网络，展示完整ML工程能力
- **创新性**：结合深度学习与LLM Agent，提供智能化交互体验
- **完整性**：端到端全栈系统，包含数据处理、模型训练、Web应用

## ✨ 功能特性

### 核心功能

- **数据导入与预处理**：支持CSV/Excel格式的用电数据导入，自动处理缺失值和异常值
- **基础统计分析**：总用电量、日均用电量、峰谷平时段分析、用电趋势分析
- **负荷模式识别**：基于深度学习的用电行为模式分类（早出晚归型、居家办公型、夜猫子型等）
- **可视化报告生成**：交互式图表展示（负荷曲线、峰谷比例、趋势分析）+ PDF/Excel导出
- **节能建议生成**：基于LLM的个性化、上下文相关的节能建议
- **仪表盘展示**：集中展示所有分析结果的Web界面
- **异常用电告警**：实时检测异常用电并发送邮件通知

### 高级特性

- **深度学习行为分析**：
  - LSTM行为模式分类器（准确率 ≥ 85%）
  - Autoencoder异常检测器（无监督学习）
- **LLM智能问答Agent**：
  - 支持多种LLM后端（OpenAI/Anthropic/Ollama）
  - 对话式节能建议和用电咨询
- **模拟数据生成器**：用于系统测试和演示的电表数据模拟

## 🛠️ 技术栈

### 后端

- **Web框架**：Robyn 0.72.2+（高性能异步Python框架）
- **深度学习**：PyTorch 2.8.0 + CUDA 12.9
- **数据处理**：Pandas 2.3.3+, NumPy 2.3.5+
- **可视化**：Matplotlib 3.10.8+, Seaborn 0.13.2+, Pyecharts 2.0.9+
- **LLM集成**：LangChain 1.2.0+, OpenAI 2.14.0+, Anthropic 0.75.0+, Ollama 0.6.1+
- **任务调度**：APScheduler 3.11.2+
- **文档处理**：python-docx 1.2.0+, openpyxl 3.1.5+, WeasyPrint 67.0+
- **机器学习**：scikit-learn 1.8.0+
- **包管理**：uv

### 前端

- **框架**：React 18.3.1 + TypeScript 5.9.3 + Vite 5.4.21
- **UI框架**：Ant Design 6.1.2
- **图表库**：ECharts 6.0.0 + echarts-for-react 3.0.5
- **HTTP客户端**：Axios 1.13.2

### 深度学习模型

- **行为分类**：LSTM（长短期记忆网络）
- **异常检测**：Autoencoder（自编码器）
- **训练环境**：RTX 3050 Laptop

## 🚀 快速开始

### 环境要求

- Python 3.13+
- CUDA 12.9（可选，用于GPU加速）
- Node.js 18+（前端开发）

### 安装步骤

1. **克隆仓库**

```bash
git clone <repository-url>
cd graduation_project
```

2. **安装Python依赖**

```bash
# 使用 uv 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. **验证CUDA环境**（可选）

```bash
python backend/tests/test_cuda.py
```

4. **安装前端依赖**（待实现）

```bash
cd frontend
npm install
```

### 运行项目

**后端服务**（待实现）

```bash
python backend/app/main.py
```

**前端开发服务器**（待实现）

```bash
cd frontend
npm run dev
```

## 📁 项目结构

```
graduation_project/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── routes/         # API路由
│   │   ├── agent/          # LLM Agent逻辑
│   │   │   └── providers/  # LLM后端集成
│   │   ├── models/         # 深度学习模型
│   │   │   └── weights/    # 模型权重
│   │   ├── knowledge/      # Agent知识库
│   │   └── utils/          # 工具函数
│   ├── configs/            # 配置文件
│   ├── scripts/            # 开发脚本
│   │   └── analysis/       # 数据分析脚本
│   └── tests/              # 测试文件
├── data/                   # 数据目录
│   ├── raw/               # 原始数据（gitignored）
│   └── analysis/          # 分析结果（gitignored）
├── doc/                    # 项目文档
│   ├── chinese_project.md # 详细需求文档
│   ├── 任务书.docx        # 任务书
│   └── 开题报告.docx      # 开题报告
├── frontend/              # 前端代码（待创建）
├── pyproject.toml         # Python项目配置
├── uv.lock               # uv依赖锁文件
├── CLAUDE.md             # Claude Code开发指南
└── README.md             # 本文件
```

## 🎯 性能指标

根据项目任务书要求：

| 指标 | 目标 |
|------|------|
| 模型精度 | 行为分类准确率 ≥ 85% |
| API响应时间 | ≤ 3秒 |
| 模型推理时间 | ≤ 2秒 |
| 并发支持 | 支持多用户并发访问 |
| 运行环境 | RTX 3050 Laptop稳定运行 |

## 🗺️ 开发路线图

### 阶段1：设计与规划（2025.12 - 2026.1）

- [x] 开题报告
- [ ] 概要设计
- [ ] 详细设计

### 阶段2：核心功能开发（2026.1 - 2026.2）

- [ ] 数据预处理模块
- [ ] 统计分析模块
- [ ] 可视化模块
- [ ] 基础系统实现（Robyn + React）

### 阶段3：深度学习模型开发（2026.2 - 2026.3）

- [ ] 数据集准备（UK-DALE/REFIT）
- [ ] LSTM行为分类器
- [ ] Autoencoder异常检测器
- [ ] 模型训练与优化

### 阶段4：LLM Agent集成（2026.3）

- [ ] LLM后端集成（OpenAI/Anthropic/Ollama）
- [ ] Agent逻辑实现
- [ ] 问答界面开发

### 阶段5：优化与测试（2026.3 - 2026.4）

- [ ] 性能优化
- [ ] 系统测试
- [ ] 论文撰写

## 📚 开发文档

- **详细需求文档**：`/doc/chinese_project.md`
- **开发指南**：`CLAUDE.md`
- **API文档**：待完善
- **模型文档**：待完善

## 🤝 贡献指南

本项目为毕业设计项目，暂不接受外部贡献。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 👤 作者

毕业设计项目

## 🙏 致谢

- 感谢导师的指导
- 感谢开源社区提供的工具和框架
- 数据集来源：UK-DALE, REFIT, Pecan Street

---

**注意**：本项目目前处于早期开发阶段，部分功能尚未实现。详细的开发计划和技术细节请参考 `/doc/chinese_project.md`。
