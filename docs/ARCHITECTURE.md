# 系统架构

## 目标

MedAssist Lung Agent 不是普通聊天机器人，而是一个包含两个核心能力的医疗辅助 agent：

1. 肺部 X 光辅助筛查。
2. 日常健康咨询 RAG。

## 流程

```text
用户
  |
  |-- 健康问题 --------------------------+
  |                                      |
  v                                      |
Agent 编排层                             |
  |-- 意图识别: 呼吸道/胃肠/用药/食物/胸片 |
  |-- 紧急程度: routine/urgent/emergency |
  |                                      |
  v                                      |
RAG 检索 docs/knowledge                  |
  |                                      |
  +-- Qwen 已配置: RAG + Qwen 生成回答    |
  +-- Qwen 未配置: RAG fallback 回答      |
                                         |
用户看到: 回答 + 红旗提醒 + 建议动作 + 来源
```

```text
用户上传胸片
  |
  v
ResNet18 CNN
  |
  |-- normal/pneumonia 概率
  |-- Grad-CAM 热力图
  |
  v
用户看到: 分类概率 + 风险提示 + 可解释热力图
```

## 当前完成度

已完成：

- FastAPI 后端。
- Web demo。
- 138 篇 RAG 种子知识文档。
- RAG 检索与 query expansion。
- 健康咨询 fallback。
- Qwen 完整模型/LoRA adapter 配置入口。
- ResNet18 胸片推理。
- Grad-CAM 可解释性。
- Agent 意图识别和紧急程度分级。
- `/api/status` 状态检查。
- Windows 一键启动脚本。
- 云服务器启动脚本和部署说明。

仍需云服务器/GPU 后增强：

- 真实加载 Qwen 微调模型并调试生成质量。
- 使用真实测试集批量评估 CNN。
- 替换或补充更多真实爬取的可信医学文档。
- 升级向量 RAG，例如 bge/m3e/text2vec embedding。
- 添加实验结果表格和截图，整理成毕设材料。

## 安全边界

- 本项目只做健康科普和辅助筛查。
- 不给确定诊断。
- 不开处方。
- 不替代医生面诊和放射科医生阅片。
- 出现胸痛、呼吸困难、意识异常、抽搐、咯血、严重脱水、血便黑便等红旗症状时，优先提示线下就医或急诊。

