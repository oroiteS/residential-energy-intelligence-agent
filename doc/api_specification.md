# 住宅能源代理系统 API 规范（版本 1.0）

# 住宅能源智能代理系统 - API 规范

**版本**：1.0

**后端框架**：Robyn 0.72.2+

**基础 URL**：`/api/v1`

---

## 1. API 架构

### 1.1 约定规范

|       |                                                        |
| ----- | ------------------------------------------------------ |
| 项目    | 规范说明                                                   |
| 数据格式  | JSON（`application/json`）                               |
| 文件上传  | `multipart/form-data`                                  |
| 时间格式  | ISO 8601 UTC（`YYYY-MM-DDTHH:mm:ssZ`）                   |
| ID 格式 | 前缀字符串（例如：`ds_`、`job_`、`stat_`）                         |
| 分页方式  | 基于游标：`?limit=50&cursor=...`                            |
| 筛选条件  | 时间范围：`?from=...&to=...`                                |
| 排序规则  | `?sort=created_at:desc`（降序）/ `asc`（升序）                 |
| 国际化   | `Accept-Language` 请求头 或 `?lang=zh-CN`（中文）/ `en-US`（英文） |

### 1.2 响应格式

**成功响应**：

```JSON
{  "status": "success",  "data": { ... }, // 业务数据  "meta": {    "next_cursor": "cursor_xyz", // 下一页游标（分页时返回）    "has_more": true // 是否还有更多数据  }}
```

**错误响应**：

```JSON
{  "status": "error",  "error": {    "code": "VALIDATION_ERROR", // 错误码    "message": "时间戳格式无效", // 错误描述    "details": { "field": "from", "reason": "需符合 ISO 8601 格式" } // 详细信息  },  "request_id": "req_abc123" // 请求唯一标识（用于问题排查）}
```

### 1.3 HTTP 状态码

|     |                      |
| --- | -------------------- |
| 状态码 | 用途                   |
| 200 | 操作成功                 |
| 201 | 资源创建成功               |
| 202 | 异步任务已接收（等待执行）        |
| 400 | 请求参数错误 / 数据验证失败      |
| 404 | 资源不存在                |
| 422 | 无法处理的实体（参数格式正确但逻辑无效） |
| 429 | 请求频率限制（过于频繁）         |
| 500 | 服务器内部错误              |

### 1.4 错误码

|                         |                                 |
| ----------------------- | ------------------------------- |
| 错误码                     | 描述                              |
| `VALIDATION_ERROR`      | 请求参数验证失败                        |
| `RESOURCE_NOT_FOUND`    | 资源不存在                           |
| `FILE_FORMAT_ERROR`     | 不支持的文件格式（仅支持 CSV/Excel）         |
| `FILE_TOO_LARGE`        | 文件大小超出限制（最大 50MB）               |
| `PROCESSING_ERROR`      | 数据处理失败（如清洗、转换异常）                |
| `MODEL_INFERENCE_ERROR` | 模型推理失败（如 LSTM、Autoencoder 模型）   |
| `LLM_API_ERROR`         | 大语言模型接口调用失败（如 OpenAI/Anthropic） |
| `SMTP_ERROR`            | 邮件发送失败（告警通知）                    |
| `JOB_CANCELED`          | 任务已被取消                          |

---

## 2. 接口详情

### 2.1 任务管理（异步任务轮询）

耗时操作（如数据预处理、模型推理）会返回 `job_id`，通过该接口查询任务状态。

#### GET `/jobs/{job_id}`

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "job_abc123",    "type": "preprocess", // 任务类型（预处理/统计分析/模型推理等）    "status": "running", // 任务状态    "progress": 0.45, // 进度（0-1）    "started_at": "2026-01-01T12:00:00Z", // 开始时间    "finished_at": null, // 结束时间（未完成时为 null）    "result_id": null, // 结果 ID（完成后返回，用于查询具体结果）    "error": null // 错误信息（失败时返回）  }}
```

**任务状态说明**：`queued`（排队中）| `running`（执行中）| `succeeded`（成功）| `failed`（失败）| `canceled`（已取消）

**失败时错误格式**：

```JSON
{  "error": {    "code": "PROCESSING_ERROR",    "message": "CSV 文件解析失败",    "details": {"line": 42, "reason": "时间戳格式无效"}  }}
```

#### POST `/jobs/{job_id}/cancel`

取消正在执行或排队中的任务。

**响应示例**：

```JSON
{  "status": "success",  "data": {"canceled": true}}
```

---

### 2.2 数据集管理（数据存储与预处理）

#### GET `/datasets`

获取所有数据集列表（分页）。

**查询参数**：

|        |        |                                                   |
| ------ | ------ | ------------------------------------------------- |
| 参数     | 类型     | 描述                                                |
| limit  | int    | 每页最大数量（默认 20，最大 100）                              |
| cursor | string | 分页游标（上一页返回的 `next_cursor`）                        |
| status | string | 按状态筛选（`uploaded`/`preprocessing`/`ready`/`error`） |

**响应示例**：

```JSON
{  "status": "success",  "data": {    "items": [      {"id": "ds_abc123", "name": "家庭2026年第一季度用电", "status": "ready", "created_at": "2026-01-01T12:00:00Z"}    ]  },  "meta": {"next_cursor": "cursor_123", "has_more": true}}
```

#### POST `/datasets`

上传包含用电数据的 CSV/Excel 文件。

**请求格式**：`multipart/form-data`

**请求字段**：

|                  |        |      |                                       |
| ---------------- | ------ | ---- | ------------------------------------- |
| 字段               | 类型     | 是否必填 | 描述                                    |
| file             | binary | 是    | CSV 或 Excel 文件（最大 50MB）               |
| name             | string | 否    | 数据集名称（默认自动生成，如 `dataset_20260101`）    |
| timestamp_column | string | 否    | 时间戳列名（默认自动识别，如 `time`/`timestamp`）    |
| value_column     | string | 否    | 用电值列名（默认自动识别，如 `consumption`/`value`） |
| timezone         | string | 否    | 时区（默认 `Asia/Shanghai`，支持 IANA 时区格式）   |
| unit             | string | 否    | 单位（默认 `kWh`，支持 `Wh`/`kWh`/`MWh`）      |

**响应示例（201）**：

```JSON
{  "status": "success",  "data": {    "id": "ds_abc123",    "name": "家庭2026年第一季度用电",    "source_type": "csv", // 文件类型    "status": "uploaded", // 状态（已上传）    "row_count": 0, // 行数（预处理后更新）    "created_at": "2026-01-01T12:00:00Z"  }}
```

#### POST `/datasets/{dataset_id}/preprocess`

触发数据集预处理（数据清洗、归一化、时间对齐）。

**请求体**：

```JSON
{  "missing_value_strategy": "interpolate", // 缺失值处理策略  "outlier_strategy": "clip", // 异常值处理策略  "resample": "1h", // 重采样频率  "align_timezone": true // 是否对齐时区（默认 true）}
```

|                        |         |               |                                                     |
| ---------------------- | ------- | ------------- | --------------------------------------------------- |
| 字段                     | 类型      | 默认值           | 可选值                                                 |
| missing_value_strategy | string  | `interpolate` | `interpolate`（插值填充）、`forward_fill`（前向填充）、`drop`（删除） |
| outlier_strategy       | string  | `clip`        | `clip`（截断）、`remove`（删除）、`none`（不处理）                 |
| resample               | string  | `1h`          | `15min`（15分钟）、`30min`（30分钟）、`1h`（1小时）、`1d`（1天）      |
| align_timezone         | boolean | true          | -                                                   |

**响应示例（202）**：

```JSON
{  "status": "success",  "data": {    "job_id": "job_def456", // 任务 ID（用于查询进度）    "dataset_id": "ds_abc123",    "status": "queued" // 任务状态（排队中）  }}
```

#### GET `/datasets/{dataset_id}`

获取数据集元信息。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "ds_abc123",    "name": "家庭2026年第一季度用电",    "status": "ready", // 状态（已就绪）    "timezone": "Asia/Shanghai",    "sampling_interval": "1h", // 采样间隔（预处理后更新）    "row_count": 8760, // 总行数（1小时粒度 × 365天）    "time_range": {      "from": "2026-01-01T00:00:00Z", // 数据起始时间      "to": "2026-12-31T23:00:00Z" // 数据结束时间    },    "created_at": "2026-01-01T12:00:00Z",    "updated_at": "2026-01-02T08:00:00Z" // 最后更新时间  }}
```

**数据集状态说明**：`uploaded`（已上传）| `preprocessing`（预处理中）| `ready`（已就绪）| `error`（处理失败）

#### PATCH `/datasets/{dataset_id}`

更新数据集元信息（仅支持部分字段）。

**请求体**：

```JSON
{  "name": "家庭2026年Q1用电数据", // 新名称  "timezone": "UTC" // 新时区}
```

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "ds_abc123",    "name": "家庭2026年Q1用电数据",    "timezone": "UTC",    "updated_at": "2026-01-02T10:00:00Z"  }}
```

#### GET `/datasets/{dataset_id}/data`

获取用电数据明细（分页）。

**查询参数**：

|        |        |                                                       |
| ------ | ------ | ----------------------------------------------------- |
| 参数     | 类型     | 描述                                                    |
| from   | string | 起始时间（ISO 8601，如 `2026-01-01T00:00:00Z`）               |
| to     | string | 结束时间（ISO 8601，如 `2026-01-02T23:59:59Z`）               |
| limit  | int    | 每页最大行数（默认 100，最大 1000）                                |
| cursor | string | 分页游标                                                  |
| format | string | 响应格式（`default` 默认格式 / `compact` 紧凑格式，适用于 ECharts 可视化） |

**响应示例（默认格式）**：

```JSON
{  "status": "success",  "data": {    "items": [      {"timestamp": "2026-01-01T00:00:00Z", "value": 0.72}, // 时间戳 + 用电值（kWh）      {"timestamp": "2026-01-01T01:00:00Z", "value": 0.68}    ]  },  "meta": {    "next_cursor": "cursor_xyz",    "has_more": true  }}
```

**响应示例（紧凑格式，format=compact）**：

```JSON
{  "status": "success",  "data": {    "items": [      ["2026-01-01T00:00:00Z", 0.72], // [时间戳, 用电值]，减少数据量      ["2026-01-01T01:00:00Z", 0.68]    ]  },  "meta": {"next_cursor": "cursor_xyz", "has_more": true}}
```

#### DELETE `/datasets/{dataset_id}`

删除数据集及所有关联结果（统计、报告、模型输出等）。

**响应示例**：

```JSON
{  "status": "success",  "data": {"deleted": true}}
```

---

### 2.3 统计分析

#### POST `/datasets/{dataset_id}/statistics`

执行用电数据统计分析（总用电量、峰谷分布、日均用电等）。

**请求体**：

```JSON
{  "from": "2026-01-01T00:00:00Z", // 统计起始时间  "to": "2026-01-31T23:59:59Z", // 统计结束时间  "peak_valley_rules": { // 峰谷时段规则（自定义）    "peak_hours": ["10:00-12:00", "18:00-22:00"], // 峰时（高电价时段）    "valley_hours": ["00:00-06:00"], // 谷时（低电价时段）    "flat_hours": ["06:00-10:00", "12:00-18:00", "22:00-24:00"] // 平时（平电价时段）  }}
```

**响应示例（202）**：

```JSON
{  "status": "success",  "data": {    "job_id": "job_stat001", // 任务 ID    "stat_id": "stat_abc123" // 统计结果 ID（用于查询最终结果）  }}
```

#### GET `/statistics/{stat_id}`

获取统计分析结果。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "stat_abc123",    "dataset_id": "ds_abc123",    "time_range": {      "from": "2026-01-01T00:00:00Z",      "to": "2026-01-31T23:59:59Z"    },    "total_consumption": 530.4, // 总用电量（kWh）    "daily_average": 17.1, // 日均用电量（kWh）    "peak_load": { // 峰值负荷      "value": 2.8, // 峰值（kWh）      "timestamp": "2026-01-15T19:00:00Z" // 峰值出现时间    },    "valley_load": { // 谷值负荷      "value": 0.3, // 谷值（kWh）      "timestamp": "2026-01-08T03:00:00Z" // 谷值出现时间    },    "period_distribution": [ // 峰谷平时段分布      {"name": "peak", "consumption": 223.4, "ratio": 0.42}, // 峰时：用电量223.4kWh，占比42%      {"name": "valley", "consumption": 85.2, "ratio": 0.16}, // 谷时：用电量85.2kWh，占比16%      {"name": "flat", "consumption": 221.8, "ratio": 0.42} // 平时：用电量221.8kWh，占比42%    ],    "trend": "increasing", // 趋势（increasing 上升 / stable 平稳 / decreasing 下降）    "created_at": "2026-01-01T12:30:00Z"  }}
```

---

### 2.4 负荷模式识别（用电行为分类）

#### POST `/datasets/{dataset_id}/load-patterns`

执行负荷模式识别（K均值聚类或规则-based 方法）。

**请求体**：

```JSON
{  "method": "kmeans", // 识别方法  "k": 3, // 聚类数量（仅K均值有效）  "features": ["hourly_profile", "daily_avg", "peak_hour"], // 特征维度  "language": "zh-CN" // 结果语言}
```

|          |        |          |                                                                                   |
| -------- | ------ | -------- | --------------------------------------------------------------------------------- |
| 字段       | 类型     | 默认值      | 可选值                                                                               |
| method   | string | `kmeans` | `kmeans`（K均值聚类）、`rules`（规则匹配）                                                     |
| k        | int    | 3        | 2-5（K均值聚类的类别数量）                                                                   |
| features | array  | all      | `hourly_profile`（小时用电曲线）、`daily_avg`（日均用电）、`peak_hour`（峰值时段）、`valley_ratio`（谷值占比） |
| language | string | `zh-CN`  | `zh-CN`（中文）、`en-US`（英文）                                                           |

**响应示例（202）**：

```JSON
{  "status": "success",  "data": {    "job_id": "job_lp001", // 任务 ID    "pattern_id": "lp_abc123" // 模式识别结果 ID  }}
```

#### GET `/load-patterns/{pattern_id}`

获取负荷模式识别结果。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "lp_abc123",    "dataset_id": "ds_abc123",    "method": "kmeans",    "label": "night_usage", // 模式标签（英文）    "label_display": "夜间用电型", // 模式标签（中文）    "confidence": 0.85, // 置信度（0-1）    "cluster_info": {      "cluster_id": 2, // 聚类ID      "centroid": [0.4, 0.3, 0.7], // 聚类中心（对应特征维度）      "description": "用电高峰出现在 22:00-02:00" // 模式描述    },    "hourly_profile": [ // 小时用电曲线（平均值）      {"hour": "00:00", "value": 0.8},      {"hour": "01:00", "value": 0.7},      {"hour": "02:00", "value": 0.5}    ],    "created_at": "2026-01-01T13:00:00Z"  }}
```

**负荷模式标签说明**：

|                    |       |                                      |
| ------------------ | ----- | ------------------------------------ |
| 英文标签               | 中文标签  | 描述                                   |
| `daytime_usage`    | 日间用电型 | 用电高峰集中在 08:00-18:00                  |
| `night_usage`      | 夜间用电型 | 用电高峰集中在 22:00-02:00                  |
| `balanced`         | 均衡用电型 | 全天用电分布均匀                             |
| `office_worker`    | 上班族型  | 早（07:00-09:00）晚（18:00-22:00）用电高峰，日间低 |
| `home_office`      | 居家办公型 | 日间（09:00-18:00）用电稳定，无明显低谷            |
| `energy_saver`     | 节能型   | 全天用电量普遍偏低                            |
| `high_consumption` | 高耗能型  | 全天用电量普遍偏高                            |

---

### 2.5 报告生成（可视化与导出）

#### POST `/datasets/{dataset_id}/reports`

生成用电分析报告（支持 PDF/Excel 导出，包含多种可视化图表）。

**请求体**：

```JSON
{  "formats": ["pdf", "xlsx"], // 导出格式  "charts": ["load_curve", "peak_valley_pie", "trend_line", "comparison"], // 包含图表  "time_range": {    "from": "2026-01-01T00:00:00Z",    "to": "2026-01-31T23:59:59Z"  },  "language": "zh-CN" // 报告语言}
```

|          |        |           |                                                                                                                |
| -------- | ------ | --------- | -------------------------------------------------------------------------------------------------------------- |
| 字段       | 类型     | 默认值       | 可选值                                                                                                            |
| formats  | array  | `["pdf"]` | `pdf`（PDF 文档）、`xlsx`（Excel 表格）                                                                                 |
| charts   | array  | all       | `load_curve`（用电曲线）、`peak_valley_pie`（峰谷占比饼图）、`trend_line`（趋势线图）、`comparison`（环比/同比对比图）、`daily_heatmap`（日用电热力图） |
| language | string | `zh-CN`   | `zh-CN`（中文）、`en-US`（英文）                                                                                        |

**响应示例（202）**：

```JSON
{  "status": "success",  "data": {    "job_id": "job_rpt001", // 任务 ID    "report_id": "rpt_abc123" // 报告 ID  }}
```

#### GET `/reports/{report_id}`

查询报告生成状态。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "rpt_abc123",    "dataset_id": "ds_abc123",    "status": "succeeded", // 状态（succeeded 成功 / failed 失败 / running 生成中）    "files": [      {"format": "pdf", "size_bytes": 524288}, // PDF 文件大小（512KB）      {"format": "xlsx", "size_bytes": 131072} // Excel 文件大小（128KB）    ],    "created_at": "2026-01-01T14:00:00Z"  }}
```

#### GET `/reports/{report_id}/download`

下载生成的报告文件。

**查询参数**：

|        |        |      |                      |
| ------ | ------ | ---- | -------------------- |
| 参数     | 类型     | 是否必填 | 描述                   |
| format | string | 是    | 下载格式（`pdf` 或 `xlsx`） |

**响应**：二进制文件流（自动触发下载，响应头包含 `Content-Type` 和 `Content-Disposition`）。

---

### 2.6 节能建议（个性化推荐）

#### POST `/datasets/{dataset_id}/recommendations`

生成个性化节能建议（支持规则匹配、大语言模型生成、混合模式）。

**请求体**：

```JSON
{  "mode": "hybrid", // 推荐模式  "llm_provider": "openai", // 大语言模型提供商  "language": "zh-CN" // 建议语言}
```

|              |        |          |                                                             |
| ------------ | ------ | -------- | ----------------------------------------------------------- |
| 字段           | 类型     | 默认值      | 可选值                                                         |
| mode         | string | `hybrid` | `rules`（规则匹配）、`llm`（大语言模型生成）、`hybrid`（混合模式，优先规则+LLM补充）      |
| llm_provider | string | `openai` | `openai`（OpenAI）、`anthropic`（Anthropic）、`ollama`（本地 Ollama） |
| language     | string | `zh-CN`  | `zh-CN`（中文）、`en-US`（英文）                                     |

**响应示例（202）**：

```JSON
{  "status": "success",  "data": {    "job_id": "job_rec001", // 任务 ID    "recommendation_id": "rec_abc123" // 建议结果 ID  }}
```

#### GET `/recommendations/{recommendation_id}`

获取节能建议结果。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "rec_abc123",    "dataset_id": "ds_abc123",    "status": "succeeded",    "mode": "hybrid",    "items": [      {        "type": "peak_shifting", // 建议类型（峰谷转移）        "priority": "high", // 优先级（high 高 / medium 中 / low 低）        "title": "调整高峰用电时段",        "detail": "您家峰时用电占比42%，建议将洗衣、充电等大功率设备使用安排在谷时（00:00-06:00），可节省约15%电费。",        "potential_savings": "15%" // 潜在节电量/电费      },      {        "type": "anomaly_warning", // 建议类型（异常告警）        "priority": "medium",        "title": "异常用电提醒",        "detail": "检测到1月15日19:00出现突发高负荷（2.8kWh），请检查是否有设备异常运行（如空调未关闭、热水器故障等）。",        "potential_savings": null // 无直接节电量      }    ],    "created_at": "2026-01-01T15:00:00Z"  }}
```

---

### 2.7 数据看板（概览数据）

#### GET `/dashboards/{dataset_id}`

获取数据集概览数据（用于前端看板展示，包含核心指标、图表数据、异常提醒等）。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "dataset_id": "ds_abc123",    "summary": { // 核心指标摘要      "total_consumption": 530.4, // 总用电量（kWh）      "daily_average": 17.1, // 日均用电量（kWh）      "load_pattern": "night_usage", // 用电模式      "load_pattern_display": "夜间用电型", // 用电模式（中文）      "anomaly_count": 3, // 异常次数      "last_updated": "2026-01-01T16:00:00Z" // 最后更新时间    },    "charts": { // 可视化图表数据      "load_curve_24h": [ // 24小时平均用电曲线        {"hour": 0, "avg_value": 0.45},        {"hour": 1, "avg_value": 0.38},        // ... 其余时段      ],      "daily_trend": [ // 日均用电趋势        {"date": "2026-01-01", "total": 17.2},        {"date": "2026-01-02", "total": 16.8},        // ... 其余日期      ],      "peak_valley_distribution": [ // 峰谷占比        {"name": "peak", "value": 0.42},        {"name": "valley", "value": 0.16},        {"name": "flat", "value": 0.42}      ]    },    "recent_anomalies": [ // 近期异常      {        "timestamp": "2026-01-15T19:00:00Z",        "type": "spike", // 异常类型（突发高峰）        "score": 0.93 // 异常得分（0-1，越高越异常）      }    ],    "top_recommendations": [ // top3 节能建议      "将洗衣、充电等活动安排在谷时段，可节省15%电费",      "检查1月15日19:00的突发高负荷设备，避免无效耗电",      "夜间用电占比高，建议更换节能灯具（如LED灯）"    ]  }}
```

---

### 2.8 异常检测（用电异常识别）

#### POST `/datasets/{dataset_id}/anomalies`

执行用电异常检测（基于自编码器 Autoencoder 模型）。

**请求体**：

```JSON
{  "method": "autoencoder", // 检测方法（默认自编码器）  "threshold": 0.85, // 异常得分阈值（0-1，越高越严格）  "window_hours": 24 // 滑动窗口大小（小时）}
```

|              |        |               |                      |
| ------------ | ------ | ------------- | -------------------- |
| 字段           | 类型     | 默认值           | 描述                   |
| method       | string | `autoencoder` | 异常检测算法（目前仅支持自编码器）    |
| threshold    | float  | 0.85          | 异常判定阈值（得分 ≥ 阈值则视为异常） |
| window_hours | int    | 24            | 上下文窗口大小（用于判断“正常”模式）  |

**响应示例（202）**：

```JSON
{  "status": "success",  "data": {    "job_id": "job_anom001", // 任务 ID    "anomaly_id": "anom_abc123" // 异常检测结果 ID  }}
```

#### GET `/anomalies/{anomaly_id}`

获取异常检测结果。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "anom_abc123",    "dataset_id": "ds_abc123",    "threshold": 0.85,    "anomalies": [      {        "timestamp": "2026-01-15T19:00:00Z", // 异常时间        "value": 2.8, // 异常用电值（kWh）        "score": 0.93, // 异常得分        "type": "spike", // 异常类型（英文）        "type_display": "突发高负荷" // 异常类型（中文）      },      {        "timestamp": "2026-01-20T00:00:00Z",        "value": 0.05, // 异常用电值（极低）        "score": 0.88,        "type": "sustained_low", // 异常类型（英文）        "type_display": "持续低负荷" // 异常类型（中文）      }    ],    "total_count": 2, // 异常总数    "created_at": "2026-01-01T17:00:00Z"  }}
```

**异常类型说明**：

|                 |       |                            |
| --------------- | ----- | -------------------------- |
| 英文类型            | 中文类型  | 描述                         |
| `spike`         | 突发高负荷 | 短时间内用电值急剧升高（如设备异常启动）       |
| `sustained_low` | 持续低负荷 | 长时间用电值远低于正常水平（如设备未运行但应运行）  |
| `pattern_shift` | 模式突变  | 用电模式突然改变（如平时日间用电，突然变为夜间用电） |

---

### 2.9 告警配置（全局设置）

全局告警配置用于模拟数据生成器的实时异常检测。当检测到异常时，系统会根据配置发送邮件通知。

> **注意**：告警配置为全局设置，适用于所有通过模拟器生成的数据。历史数据集的异常检测通过 `/datasets/{dataset_id}/anomalies` 接口单独执行。

#### GET `/alert-config`

获取当前告警配置。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "email": "user@example.com",    "threshold": 0.9,    "frequency": "immediate",    "types": ["spike", "sustained_low"],    "enabled": true,    "updated_at": "2026-01-01T18:00:00Z"  }}
```

#### PUT `/alert-config`

更新全局告警配置（用于模拟数据实时检测）。

**请求体**：

```JSON
{  "email": "user@example.com",  "threshold": 0.9,  "frequency": "immediate",  "types": ["spike", "sustained_low"],  "enabled": true}
```

|           |        |             |                                                             |
| --------- | ------ | ----------- | ----------------------------------------------------------- |
| 字段        | 类型     | 默认值         | 可选值                                                         |
| email     | string | 必需          | 接收告警的邮箱地址                                                   |
| threshold | float  | 0.85        | 告警阈值（0-1，异常得分 ≥ 阈值时触发）                                      |
| frequency | string | `immediate` | `immediate`（即时通知）、`hourly`（每小时汇总）、`daily_digest`（每日汇总）      |
| types     | array  | all         | `spike`（突发高负荷）、`sustained_low`（持续低负荷）、`pattern_shift`（模式突变） |
| enabled   | bool   | true        | 是否启用告警                                                      |

**响应示例**：

```JSON
{  "status": "success",  "data": {    "email": "user@example.com",    "threshold": 0.9,    "frequency": "immediate",    "types": ["spike", "sustained_low"],    "enabled": true,    "updated_at": "2026-01-01T18:00:00Z"  }}
```

---

### 2.10 模拟数据生成（测试用）

#### POST `/simulations`

创建模拟任务（生成符合特定用电模式的测试数据，用于功能验证）。

**请求体**：

```JSON
{  "dataset_id": "ds_abc123", // 关联数据集（数据将写入该数据集）  "schedule": "*/5 * * * *", // 生成频率（Cron 表达式，此处为每5分钟生成1条）  "pattern": "office_worker", // 模拟用电模式  "noise_level": 0.05 // 随机噪声（0-0.2，越大数据越离散）}
```

|             |        |          |                                                                                |
| ----------- | ------ | -------- | ------------------------------------------------------------------------------ |
| 字段          | 类型     | 默认值      | 描述                                                                             |
| schedule    | string | 必需       | Cron 表达式（定义数据生成频率）                                                             |
| pattern     | string | `random` | 模拟模式（`random` 随机 / `office_worker` 上班族 / `night_owl` 夜猫子 / `home_office` 居家办公） |
| noise_level | float  | 0.05     | 随机噪声比例（控制数据真实性）                                                                |

**响应示例（201）**：

```JSON
{  "status": "success",  "data": {    "id": "sim_abc123", // 模拟任务 ID    "dataset_id": "ds_abc123",    "status": "active", // 状态（active 运行中 / stopped 已停止）    "next_run": "2026-01-01T19:05:00Z", // 下次生成时间    "created_at": "2026-01-01T19:00:00Z"  }}
```

#### POST `/simulations/{simulation_id}/trigger`

手动触发模拟数据生成（忽略 Cron 调度）。

**响应示例**：

```JSON
{  "status": "success",  "data": {"triggered": true, "generated_rows": 1} // 生成成功，新增1条数据}
```

#### GET `/simulations/{simulation_id}`

查询模拟任务状态。

#### DELETE `/simulations/{simulation_id}`

停止并删除模拟任务。

---

### 2.11 行为分析（深度学习分类）

#### POST `/datasets/{dataset_id}/behavior-analyses`

执行用户用电行为分类（基于 LSTM 模型，识别长期用电习惯）。

**请求体**：

```JSON
{  "model_type": "lstm_classifier", // 模型类型（LSTM 分类器）  "window_days": 7 // 分析窗口（基于最近7天数据）}
```

|             |        |                   |                          |
| ----------- | ------ | ----------------- | ------------------------ |
| 字段          | 类型     | 默认值               | 描述                       |
| model_type  | string | `lstm_classifier` | 深度学习模型类型（目前仅支持 LSTM 分类器） |
| window_days | int    | 7                 | 分析窗口大小（天数，越大分类越准确）       |

**响应示例（202）**：

```JSON
{  "status": "success",  "data": {    "job_id": "job_ba001", // 任务 ID    "analysis_id": "ba_abc123" // 行为分析结果 ID  }}
```

#### GET `/behavior-analyses/{analysis_id}`

获取行为分析结果。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "ba_abc123",    "dataset_id": "ds_abc123",    "model_type": "lstm_classifier",    "label": "night_owl", // 行为标签（英文）    "label_display": "夜猫子型", // 行为标签（中文）    "confidence": 0.82, // 置信度（0-1）    "probabilities": { // 各类别概率分布      "office_worker": 0.05,      "home_office": 0.08,      "night_owl": 0.82,      "energy_saver": 0.03,      "high_consumption": 0.02    },    "inference_time_ms": 156, // 模型推理时间（毫秒）    "created_at": "2026-01-01T20:00:00Z"  }}
```

**行为标签说明**（同 2.4 负荷模式标签）：

|                    |       |            |
| ------------------ | ----- | ---------- |
| 英文标签               | 中文标签  | 描述         |
| `office_worker`    | 早出晚归型 | 早晚用电高峰，日间低 |
| `home_office`      | 居家办公型 | 全天用电稳定     |
| `night_owl`        | 夜猫子型  | 夜间用电高峰     |
| `energy_saver`     | 节能型   | 整体用电量低     |
| `high_consumption` | 高耗能型  | 整体用电量高     |

---

### 2.12 问答会话（大语言模型代理）

#### POST `/qa/sessions`

创建问答会话（基于数据集上下文，通过大语言模型解答用户用电相关问题）。

**请求体**：

```JSON
{  "dataset_id": "ds_abc123", // 关联数据集（仅基于该数据集回答）  "llm_provider": "openai", // 大语言模型提供商  "language": "zh-CN" // 问答语言}
```

|              |        |          |                               |
| ------------ | ------ | -------- | ----------------------------- |
| 字段           | 类型     | 默认值      | 可选值                           |
| llm_provider | string | `openai` | `openai`、`anthropic`、`ollama` |
| language     | string | `zh-CN`  | `zh-CN`、`en-US`               |

**响应示例（201）**：

```JSON
{  "status": "success",  "data": {    "id": "qa_abc123", // 会话 ID    "dataset_id": "ds_abc123",    "llm_provider": "openai",    "created_at": "2026-01-01T21:00:00Z"  }}
```

#### POST `/qa/sessions/{session_id}/messages`

向大语言模型发送问题（基于会话上下文）。

**请求体**：

```JSON
{  "content": "为什么上周的夜间用电增加了？" // 用户问题}
```

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "msg_def456", // 消息 ID    "role": "assistant", // 角色（assistant 助手 / user 用户）    "content": "根据分析结果，上周（1月8日-14日）您的夜间用电量较前一周增加了约23%。主要原因可能是：\n\n1. **22:00-01:00时段用电增加**：该时段平均负荷从0.6kWh升至0.8kWh\n2. **检测到的异常**：1月12日23:00出现突发高负荷（1.2kWh）\n\n建议检查是否有新增的夜间运行设备（如加湿器、电暖器），或电热设备使用频率增加。",    "citations": [ // 参考数据来源      {"type": "statistics", "id": "stat_abc123"}, // 统计分析结果      {"type": "anomalies", "id": "anom_abc123"} // 异常检测结果    ],    "created_at": "2026-01-01T21:01:00Z"  }}
```

#### GET `/qa/sessions/{session_id}`

获取会话历史（用户问题 + 助手回答）。

**响应示例**：

```JSON
{  "status": "success",  "data": {    "id": "qa_abc123",    "dataset_id": "ds_abc123",    "messages": [      {"id": "msg_abc123", "role": "user", "content": "为什么上周的夜间用电增加了？", "created_at": "2026-01-01T21:00:50Z"},      {"id": "msg_def456", "role": "assistant", "content": "根据分析结果...", "created_at": "2026-01-01T21:01:10Z"}    ],    "created_at": "2026-01-01T21:00:00Z"  }}
```

#### DELETE `/qa/sessions/{session_id}`

删除会话及历史消息。

---

## 3. 实现说明

### 3.1 异步任务处理流程

所有耗时操作（如数据预处理、模型推理、报告生成）均返回 `202 Accepted` 状态码和 `job_id`，前端需按以下流程处理：

1. 从初始响应中获取 `job_id`

2. 定期调用 `GET /jobs/{job_id}` 轮询任务状态（建议轮询间隔 2-5 秒）

3. 当任务状态为 `succeeded` 时，通过返回的 `result_id`（如 `stat_id`/`pattern_id`）查询最终结果

4. 当任务状态为 `failed` 时，通过 `error` 字段获取失败原因

### 3.2 跨域配置（CORS）

为支持 React 等前端框架（开发环境通常运行在不同端口），需启用跨域：

```Python
# Robyn 框架示例代码app.add_header("Access-Control-Allow-Origin", "*")  # 生产环境建议指定具体域名app.add_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")app.add_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
```

### 3.3 模型加载优化

PyTorch 模型（LSTM、Autoencoder）需在服务启动时加载并缓存，避免重复加载导致性能损耗：

- 存储在 `app.state` 或单例服务中

- 优先使用 GPU（CUDA）加速推理（若硬件支持）

- 模型文件建议放在 `models/` 目录，通过相对路径加载

### 3.4 大语言模型上下文构建

问答会话（QA）中，大语言模型的提示词（Prompt）需包含以下上下文信息，确保回答准确性：

```Plain
系统提示词 + 用户用电画像 + 统计分析结果 + 负荷模式 + 近期异常 → 大语言模型 → 回答
```

示例系统提示词：

你是住宅能源智能助手，需基于用户提供的用电数据集回答问题。回答需结合统计数据、负荷模式和异常检测结果，语言简洁明了，提供具体建议。

### 3.5 安全与部署注意事项

1. **网络绑定**：API 默认绑定 `127.0.0.1`（仅本地访问），避免未授权的外部访问

2. **文件安全**：限制文件上传大小（50MB），仅允许 CSV/Excel 格式，校验文件内容（避免恶意文件）

3. **敏感信息保护**：SMTP 邮箱凭证、LLM API Key 等需存储在环境变量中，禁止在响应中暴露

4. **SQLite 优化**：启用 WAL 模式以支持后台任务（调度器、推理）与 API 的并发访问

5. **数据备份**：建议定期备份 `energy.db` 文件，可通过复制文件或 SQLite `.backup` 命令实现

6. **部署模式**：本系统采用单用户个人部署模式，数据完全本地化存储
