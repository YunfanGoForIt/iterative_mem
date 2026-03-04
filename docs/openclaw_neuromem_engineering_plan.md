# OpenClaw NeuroMem：完整可实施工程方案（v1.0）

## 1. 项目目标与成功标准

### 1.1 愿景
构建一个面向 OpenClaw 的 **仿生 Agent 记忆插件**，让记忆系统从“检索外挂”升级为“可塑、可巩固、可遗忘、可解释”的动态系统。

### 1.2 非目标（首期不做）
- 不追求全脑模拟或生物学严格复刻。
- 不替代 OpenClaw 主推理引擎，仅做可插拔 memory substrate。
- 不做高度定制 UI 平台，首期以 CLI + API + 轻量可视化为主。

### 1.3 量化成功指标（MVP 上线后 4 周）
- 长程偏好保持任务：命中率 >= 85%。
- 冲突信息修正任务：旧错误记忆覆盖率 >= 70%。
- 跨会话一致性：关键事实一致率 >= 90%。
- 记忆污染防护：注入攻击落入长期记忆比例 <= 5%。
- 延迟预算：p95 检索 + 更新 < 120ms（不含 LLM 生成）。

---

## 2. 第一性原理设计：从“存文本”到“更新连接”

### 2.1 核心抽象
- **Engram（记忆痕迹）**：节点，包含事件语义、上下文、置信度、时间戳、来源。
- **Synapse（突触连接）**：边，表示两个 engram 之间的关联强度（可塑权重）。
- **Activation（激活）**：当前任务触发的节点激活强度。
- **Plasticity（可塑性）**：通过共激活与时间差更新边权。
- **Consolidation（巩固）**：短时痕迹转长期结构。
- **Reconsolidation（再巩固）**：被召回的记忆允许修订。
- **Forgetting（遗忘）**：衰减、竞争抑制与容量剪枝。

### 2.2 设计原则
1. 写入是结构更新，不是 append-only 文档。
2. 召回会改变记忆，记忆并非只读。
3. 遗忘是一级能力，不是数据丢失。
4. 任何记忆决策必须可解释（trace path）。
5. 算法先可控后智能：先规则可塑，再逐步引入学习策略。

---

## 3. 系统架构

## 3.1 组件图（逻辑）
1. **Event Encoder**：将对话/工具输出编码为 engram 候选。
2. **Salience Gate**：显著性评分（任务奖励、用户纠错、异常信号）。
3. **Short-Term Buffer (STB)**：短时记忆缓冲。
4. **Engram Graph Store**：持久图存储（节点/边/时间序列）。
5. **Plasticity Engine**：Hebbian + STDP 边权更新。
6. **Replay & Consolidation Worker**：离线重放巩固。
7. **Recall Router**：按任务状态激活子图并检索上下文。
8. **Safety Guard**：记忆污染过滤（注入、防幻觉标签）。
9. **Explainability Layer**：输出召回路径和权重变化。

### 3.2 数据流
- 在线路径：
  - Input event -> encode -> salience gate -> STB -> (条件满足) graph update -> recall result。
- 离线路径：
  - replay queue -> consolidation -> pruning -> metrics snapshot。

### 3.3 技术选型（建议）
- 语言：Python 3.11。
- 存储：
  - 首期：SQLite + NetworkX（低门槛）。
  - 进阶：DuckDB / Postgres + 图索引层。
- Embedding：可插拔（OpenAI / local models），但仅作为辅助特征，不作为唯一记忆机制。
- 任务队列：APScheduler 或 Celery（按部署复杂度选择）。

---

## 4. 核心算法设计（MVP 可落地）

### 4.1 编码与显著性
- 事件对象：
  - `content`, `speaker`, `task_id`, `timestamp`, `tool_trace`, `feedback_signal`。
- 显著性 `S`（0~1）：
  - 由 novelty、user_correction、task_reward、error_signal 加权得到。
- 写入规则：
  - `S < θ_low`: 仅缓存，不入长期图。
  - `θ_low <= S < θ_high`: 入图但低初始权重。
  - `S >= θ_high`: 高优先级巩固队列。

### 4.2 可塑性更新（简化 STDP）
- 节点 i、j 共激活时：
  - `Δw_ij = α * a_i * a_j * exp(-|Δt|/τ) - β * interference_penalty`
- 权重裁剪：`w_ij = clip(w_ij + Δw_ij, w_min, w_max)`。
- 引入抗污染惩罚项：低可信来源、多次冲突未验证 -> penalty 增大。

### 4.3 巩固与重放
- 周期性从 STB 抽样 replay batch：
  - 优先级：高 S + 高频被召回 + 最近纠错相关。
- 巩固操作：
  1) 合并近似节点（同义/同实体）。
  2) 增强关键路径边权。
  3) 生成压缩摘要节点（schema memory）。

### 4.4 再巩固
- 被召回节点进入 `labile` 状态（短暂可塑窗口）。
- 若新证据冲突：
  - 降低旧节点置信度。
  - 建立 contradiction edge。
  - 若冲突被确认，执行覆盖或并存策略（按 domain policy）。

### 4.5 遗忘策略
- 时间衰减：`w <- w * exp(-λ * Δt)`。
- 容量预算：超预算时按 `(low salience, low recall, low trust)` 优先剪枝。
- 干扰抑制：高冲突低证据节点进行休眠（不删除，可恢复）。

---

## 5. OpenClaw 插件接口设计

### 5.1 API（建议）
- `on_event(event: Event) -> None`
- `retrieve_context(query: QueryContext) -> MemoryContext`
- `post_response_update(turn: TurnResult) -> None`
- `run_maintenance(now: datetime) -> MaintenanceReport`

### 5.2 与主 Agent 回路集成点
1. 用户输入后：先 `retrieve_context` 注入提示词。
2. 模型输出后：`post_response_update` 写入反馈信号。
3. 工具调用后：tool trace 作为高价值事件写入。
4. 定时任务：`run_maintenance` 执行巩固与遗忘。

### 5.3 输出可解释字段
- `selected_memories`: 命中节点 ID 列表。
- `activation_paths`: 触发路径（节点-边-节点）。
- `why_selected`: salience/recall/trust 打分。
- `suppressed_memories`: 被抑制原因（冲突、低可信、过旧）。

---

## 6. 工程实施计划（8 周）

### Phase 0（第 1 周）：项目地基
- 初始化仓库、模块边界、配置系统、日志与指标。
- 定义数据模型与序列化协议。
- 产出：可运行空插件 + 示例集成。

### Phase 1（第 2-3 周）：核心在线路径
- 完成 encoder、salience gate、graph store、recall router。
- 支持最小可用记忆写入/检索闭环。
- 产出：MVP Demo（跨会话偏好记忆）。

### Phase 2（第 4-5 周）：可塑性与巩固
- 实装 plasticity engine、replay worker、reconsolidation。
- 增加冲突处理与置信更新策略。
- 产出：冲突修正 Demo + 指标仪表盘。

### Phase 3（第 6-7 周）：遗忘与安全
- 完成 forgetting/pruning、污染防护、来源可信度体系。
- 对抗测试：prompt injection memory poisoning。
- 产出：安全基线报告。

### Phase 4（第 8 周）：开源发布与增长包
- 文档、案例、性能基准、可视化 time-lapse。
- 发布路线：技术文章、对比报告、社区 AMA。

---

## 7. 仓库结构建议

```text
openclaw-neuromem/
  openclaw_memory/
    core/
      engram_graph.py
      plasticity.py
      consolidation.py
      forgetting.py
      recall.py
    adapters/
      openclaw_plugin.py
    safety/
      poisoning_guard.py
    explain/
      trace.py
    storage/
      sqlite_store.py
    schemas/
      event.py
      memory.py
  tests/
    test_plasticity.py
    test_recall.py
    test_reconsolidation.py
    test_forgetting.py
    test_poisoning_guard.py
  benchmarks/
    run_eval.py
    tasks/*.yaml
  examples/
    chat_demo.py
    conflict_repair_demo.py
    timelapse_demo.py
  docs/
    architecture.md
    neuro_to_system.md
    eval_protocol.md
  README.md
```

---

## 8. 评测与验收

### 8.1 任务集
1. 长期偏好：用户 20 轮前提到的偏好是否稳定召回。
2. 冲突修正：先写错后纠正，系统是否更新为新事实。
3. 干扰鲁棒：大量无关上下文下关键记忆召回率。
4. 污染防护：恶意指令是否进入长期记忆。

### 8.2 指标
- Recall@k / MRR（召回质量）
- Conflict Resolution Rate（冲突修复率）
- Memory Pollution Rate（污染率）
- Context Utility Score（记忆对任务成功的提升）
- Latency/CPU/Storage 成本

### 8.3 自动化门禁（CI）
- 单元测试覆盖 >= 80%。
- 核心基准回归阈值：下降 >5% 阻断合并。
- 安全测试必须全绿（污染率不超阈值）。

---

## 9. 风险清单与应对

1. **复杂度过高**：仿生机制过多导致交付慢。
   - 应对：MVP 只保留 5 个机制（编码、可塑、召回、再巩固、遗忘）。
2. **评估不客观**：只看主观体验。
   - 应对：标准任务集 + 自动化 benchmark。
3. **记忆污染**：错误信息进入长期图。
   - 应对：来源可信度 + 延迟巩固 + 人类反馈优先级。
4. **性能瓶颈**：图规模增长导致延迟上升。
   - 应对：分层存储、冷记忆归档、近邻子图检索。

---

## 10. 3 天冲击 1k Star 的发布策略（务实版）

### Day 1：可跑与可看
- 发布 `chat_demo + timelapse_demo`。
- README 首页三图：结构图、对比图、时间演化图。
- 提供一键运行命令（含 mock 数据）。

### Day 2：可比较
- 发布“向量记忆 vs NeuroMem”基准报告。
- 开源失败案例（冲突、污染、遗忘失效）及修复日志。

### Day 3：可传播
- 发布技术长文 + 15 条短帖素材（多平台）。
- 发起 community challenge（谁能设计更难记忆任务）。

> 关键结论：Star 增长主要来自“差异化叙事 + 可复现实验 + 可视化传播”，不只是代码量。

---

## 11. 立即执行清单（本周可开始）

1. 定义 `Event/Engram/Synapse` 数据模型与 JSON schema。
2. 完成 `openclaw_plugin` 3 个钩子与空实现。
3. 实装最小图存储 + 简化可塑性更新。
4. 写 4 个基准任务 YAML 与评测脚本。
5. 交付第一个可解释 trace 输出。
6. 录制 90 秒演示视频并发布。

---

## 12. 你可以直接分配给团队的角色

- **Memory Algorithms（1 人）**：plasticity/consolidation/forgetting。
- **Infra & Storage（1 人）**：store、队列、性能优化。
- **Agent Integration（1 人）**：OpenClaw 适配、接口稳定性。
- **Eval & Security（1 人）**：benchmark、污染防护、CI 门禁。
- **DevRel（1 人兼职）**：文档、案例、发布节奏。

---

## 13. 版本里程碑定义

- `v0.1`：可写可读，具备短时记忆与基本检索。
- `v0.2`：可塑性更新 + 巩固 worker。
- `v0.3`：再巩固 + 冲突修正。
- `v0.4`：遗忘 + 污染防护 + 指标看板。
- `v1.0`：稳定 API、完整文档、对比基准、可视化传播包。

