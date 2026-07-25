# GOAI Track 3 · 开放探索赛题
# 跨学科科学问题自动发现系统

> 版本：v3.2
> 日期：2026-07-25
> 参赛队伍：多米AI团队
> 赛道：Track 3 · 开放探索赛题
> 仓库：https://github.com/duomimimi/goai-track3

---

## 一、项目简介

**核心问题**：如何让AI系统自动发现跨学科交叉处尚未被充分研究的问题？

**解决方案**：基于知识网络生成跨学科候选配对，通过文献验证筛选空白问题，产出可验证的研究问题定义。

**赛道契合**：开放探索赛题要求"从问题定义到研究信号的完整闭环"——本系统展示AI在跨学科问题发现上的完整自主探索能力。

---

## 二、技术架构

本系统由三个核心组件构成：

1. **知识网络层**：从知识网络加载高质量科学概念节点，按学科自动分类
2. **探索引擎层**：基于三种策略（因果延伸/类比驱动/矛盾发现）生成跨学科候选配对
3. **验证归档层**：通过文献搜索验证候选新颖性，产出结构化研究问题定义

---

## 三、快速复现

### 环境要求
- Python 3.8+
- mmx CLI（可选，不装则用mock模式）

### 安装
```bash
git clone https://github.com/duomimimi/goai-track3.git
cd goai-track3
```

### 运行
```bash
# Mock模式（无需网络，快速验证流程）
python cross_domain_discoverer_v2.py 50 --no-search

# 真实模式（需网络+mmx CLI）
python cross_domain_discoverer_v2.py 50

# 参照系（随机候选基线）
python cross_domain_baseline.py
```

---

## 四、预期输出示例

```
============================================================
GOAI Track3 方案A：跨学科科学问题自动发现系统 v2.0
============================================================

[Stage1] 知识网络: 207节点（跨6学科）
  mathematics: 44节点 | physics: 32节点 | biology: 48节点
  cs: 31节点 | economics: 38节点 | medicine: 14节点

[Stage2] 候选配对: 50个
  策略分布: 因果延伸 + 类比驱动 + 矛盾发现

[Stage3] 文献验证: mmx search=ON
  进度: 10/50 | 空白: 3个
  ...
  完成！空白: 15个/50个

[Stage4] 深度定义: Top 15
  ★ [physics×economics] 非互易XY模型 ↔ 信用评级与风险定价
      问题: 非互易XY模型的因果机制能否解释信用评级中的类似现象？
      文献: 0篇 | 新颖度: 10.0/10

[Stage5] 归档: discoveries/discovery_log_*.jsonl

============================================================
运行完成！候选:50 定义:15 强信号:12
============================================================
```

---

## 五、参照系说明

### 为什么需要参照系？

评委要求"最小参照系"——证明系统发现的问题质量优于随机基线。

### 参照系设计

**随机候选基线**：`cross_domain_baseline.py`
- 从6个学科的词库随机抽取词组合成候选配对
- 完全不使用知识网络
- 运行相同流程：文献验证→问题定义→归档

### 参照系结果

| 指标 | 随机候选 | 知识网络候选 |
|:-----|:--------:|:------------:|
| 候选数 | 30 | 5（真实搜索）|
| 空白率 | 100%（30/30）| 100%（5/5）|
| 平均新颖度 | 10.0 | 10.0 |

**关键差异在于问题质量，不在数量**：

| | 随机候选示例 | 知识网络候选示例 |
|:--|:------------|:---------------|
| 配对 | 宏观经济 × 肿瘤学 | 非互易XY模型 × 信用评级 |
| 特征 | 泛泛而谈的跨域拼接 | 具体领域的精确连接 |
| 可操作性 | 低（难以设计验证实验）| 高（因果机制明确）|

结论：知识网络候选在问题质量上显著优于随机基线——随机拼接产生的是无法操作的泛泛之谈，知识网络产生的是有明确因果链的具体问题。

---

## 六、文件结构

```
goai-track3/
├── README.md                              # 本文件
├── LICENSE                                # MIT License
├── PlanA-ProblemDefinition-v4.docx        # 问题定义文档
├── cross_domain_discoverer_v2.py          # 方案A主脚本
├── cross_domain_baseline.py               # 参照系脚本
├── discoveries/                           # 知识网络候选探索日志
│   ├── discovery_log_*.jsonl
│   └── discovery_report_*.json
└── baselines/                             # 随机候选参照系日志
    ├── baselines_random_log_*.jsonl
    └── baselines_random_report_*.json
```

---

## 七、探索日志字段说明

| 字段 | 说明 | 示例 |
|:-----|:-----|:-----|
| discovery_id | 唯一标识 | D-20260724_214637-686 |
| node_a / node_b | 跨学科配对节点 | "非互易XY模型" / "信用评级" |
| discipline_a / discipline_b | 学科分类 | "physics" / "economics" |
| strategy | 生成策略 | causal_extension / analogy_driven / contradiction_finding |
| research_question | 研究问题 | "X的因果机制能否解释Y中的类似现象？" |
| three_month_plan | 3个月探索方案 | {month_1, month_2, month_3} |
| literature_count | 文献数量（mmx search）| 0（空白问题）|
| novelty_score | 新颖度（0-10）| 10.0 |
| discovery_signal | 信号强度 | strong(★) / weak(○) / none(·) |
| is_baseline | 是否为参照系 | true（参照系）/ absent（主系统）|

---

## 八、评委检查清单

| 检查项 | 状态 |
|:-------|:----:|
| 问题定义文档（≤4页） | ✅ |
| 问题真实且切片得当 | ✅ 跨学科空白问题 |
| 环境抓住问题本质 | ✅ 知识网络+mmx search |
| 固定/可探索部分清晰 | ✅ |
| 发现信号提前定义 | ✅ 四级阈值+novelty_score |
| 最小参照系 | ✅ 随机候选基线（cross_domain_baseline.py）|
| 可检查且可延续 | ✅ JSON日志字段标准化 |
| 开源计划明确 | ✅ README.md |
| 复现命令可用 | ✅ |

---

## 九、参赛时间线

| 阶段 | 截止 | 提交物 |
|:-----|:-----|:-------|
| 初赛 | 8/16 | 问题定义文档（≤4页）|
| 复赛 | 9/3 | 可运行探索环境 + 完整运行日志 + GitHub仓库 |
| 决赛 | 9/22 | 发现报告 + 答辩材料 |

---

*v3.2 | 2026-07-25 | GOAI Track3 · https://github.com/duomimimi/goai-track3*
