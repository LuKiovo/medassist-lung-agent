# MedAssist Lung Agent

一个医疗辅助 agent：支持肺部 X 光肺炎辅助筛查、日常健康咨询、RAG 检索增强回答，以及可扩展的医学知识库爬取/索引流程。

> 重要声明：本项目只用于学习、科研和辅助信息检索，不能替代医生诊断、处方或急救建议。涉及胸痛、呼吸困难、持续高热、意识异常、严重脱水、婴幼儿/孕妇/老人/慢病患者等情况，应及时就医。

## 个人贡献点

- 使用本地已经训练好的 ResNet18 肺炎二分类模型作为影像模块。
- 健康咨询不是裸 LLM，而是先从可信医学资料中检索证据，再生成回答。
- 提供医学文档下载/清洗/索引脚本，后续可以继续爬取中文指南、医院科普或教材 TXT。
- 预留 Qwen 微调模型接入位置，可通过环境变量加载 GitHub 上的微调模型。

## 功能

- Web 演示页：`GET /`，可直接进行健康咨询和胸片上传分析。
- `POST /api/xray/analyze`：上传胸片，返回 normal/pneumonia 概率和风险提示。
- `POST /api/chat`：日常健康咨询，返回 RAG 检索依据、回答、追问项、就医红旗提醒和紧急资源。
- `POST /api/rag/reindex`：重新构建本地知识库索引。
- `GET /api/status`：查看 RAG、CNN、Qwen 配置状态。
- `GET /api/health`：服务健康检查。

## 目录

```text
medassist_lung_agent/
  api/              FastAPI 路由
  imaging/          肺部 X 光 CNN 推理
  rag/              文档加载、爬取、TF-IDF 检索索引
  llm/              Qwen/本地模型接入与安全回答策略
  safety/           医疗红旗和免责声明
  static/           Web 演示页面
docs/knowledge/     RAG 种子知识库
scripts/            运行、索引、爬取脚本
```

## 快速开始

Windows 一键启动：

```powershell
.\start_medassist.bat
```

脚本会创建虚拟环境、安装依赖、构建 RAG 索引、启动服务并打开网页。
Windows 下脚本会优先使用 `py` 创建虚拟环境，找不到时再尝试 `python`；虚拟环境创建后会固定使用 `.venv\Scripts\python.exe`。

手动启动：

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/build_rag_index.py
.\.venv\Scripts\python.exe -m uvicorn medassist_lung_agent.main:app --host 0.0.0.0 --port 8000
```

访问 API 文档：

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

## 配置

可以通过环境变量覆盖默认路径：

```powershell
$env:CHEST_MODEL_PATH="F:\visual_project\best_model_resnet18.pth"
$env:RAG_DOC_DIR="F:\Agent\docs\knowledge"
$env:RAG_INDEX_PATH="F:\Agent\data\rag_index.pkl"
$env:QWEN_MODEL_PATH="你的本地Qwen微调模型目录或HuggingFace模型名"
```

也可以在项目根目录创建 `.env`，程序会自动读取。若 Qwen 模型较大，建议在算力云 GPU 服务器上运行，并使用 `QWEN_LOAD_IN_4BIT=1` 尝试 4-bit 加载。

Qwen 详细接入方式见 `docs/QWEN_SETUP.md`。如果微调结果是 LoRA adapter，需要同时配置 `QWEN_BASE_MODEL_PATH` 和 `QWEN_ADAPTER_PATH`。

## Agent 交互

健康咨询采用两阶段交互：用户先输入主问题，agent 判断意图和紧急程度，并返回追问项；前端会把追问项展示成卡片，用户可选择性填写后再次提交。若检测到 `emergency`，页面会弹出紧急提示窗口，显示 120 和人工医生入口占位。

## 胸片可解释性

胸片分析接口会额外返回 `gradcam_png_base64`，前端会显示 Grad-CAM 热力图，用于观察模型主要关注区域。它只能帮助理解模型行为，不能证明诊断结论正确。

## 添加 RAG 文档

当前仓库包含 138 篇本项目整理的日常健康咨询与胸片辅助诊断种子文档，位于 `docs/knowledge/`。后续可继续用爬虫下载可信医学网页，替换或扩展这些种子文档。

方式一：直接把 `.txt` / `.md` 放到 `docs/knowledge/`，然后重建索引：

```powershell
.\.venv\Scripts\python.exe scripts/build_rag_index.py
```

方式二：生成本项目的种子知识库：

```powershell
.\.venv\Scripts\python.exe scripts/generate_seed_knowledge.py
.\.venv\Scripts\python.exe scripts/build_rag_index.py
```

方式三：从网页下载清洗成 TXT：

```powershell
.\.venv\Scripts\python.exe scripts/crawl_medical_docs.py --url https://medlineplus.gov/fever.html
.\.venv\Scripts\python.exe scripts/build_rag_index.py
```

建议优先使用可信来源，例如 MedlinePlus、CDC、Mayo Clinic、国家卫健委、三甲医院科普、临床指南。不要把论坛帖子作为主要依据。

## 模型改进建议

现在的 CNN 是 ResNet18 二分类，可以作为第一版项目核心。后续可升级：

- 换 DenseNet121 / EfficientNet，并加入 Grad-CAM，可解释性更适合医疗影像项目。
- 用 ChestX-ray14、RSNA Pneumonia Detection Challenge 或 CheXpert 做多标签任务，而不只是 normal/pneumonia。
- 增加 AUROC、Sensitivity、Specificity、F1、混淆矩阵，README 中展示实验表格。
- 对外部测试集做验证，说明泛化能力，简历上会比单一 accuracy 更可信。

可以用已有测试集评估当前模型：

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_cnn.py --data-dir F:\path\to\chest_xray\test
```

更多部署说明见 `docs/DEPLOYMENT.md`，后续规划见 `docs/ROADMAP.md`。

系统架构见 `docs/ARCHITECTURE.md`，当前成熟度和下一步建议见 `docs/PROJECT_STATUS.md`。
