# MedAssist Lung Agent

一个面向简历和毕设继续扩展的医疗辅助 agent：支持肺部 X 光肺炎辅助筛查、日常健康咨询、RAG 检索增强回答，以及可扩展的医学知识库爬取/索引流程。

> 重要声明：本项目只用于学习、科研和辅助信息检索，不能替代医生诊断、处方或急救建议。涉及胸痛、呼吸困难、持续高热、意识异常、严重脱水、婴幼儿/孕妇/老人/慢病患者等情况，应及时就医。

## 你的个人贡献点

- 使用你已经训练好的 ResNet18 肺炎二分类模型作为影像模块，默认读取 `F:\visual_project\best_model_resnet18.pth`。
- 健康咨询不是裸 LLM，而是先从可信医学资料中检索证据，再生成回答。
- 提供医学文档下载/清洗/索引脚本，后续可以继续爬取中文指南、医院科普或教材 TXT。
- 预留 Qwen 微调模型接入位置，可通过环境变量加载你 GitHub 上的微调模型。

## 功能

- `POST /api/xray/analyze`：上传胸片，返回 normal/pneumonia 概率和风险提示。
- `POST /api/chat`：日常健康咨询，返回 RAG 检索依据、回答和就医红旗提醒。
- `POST /api/rag/reindex`：重新构建本地知识库索引。
- `GET /api/health`：服务健康检查。

## 目录

```text
medassist_lung_agent/
  api/              FastAPI 路由
  imaging/          肺部 X 光 CNN 推理
  rag/              文档加载、爬取、TF-IDF 检索索引
  llm/              Qwen/本地模型接入与安全回答策略
  safety/           医疗红旗和免责声明
docs/knowledge/     RAG 种子知识库
scripts/            运行、索引、爬取脚本
```

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/build_rag_index.py
python -m uvicorn medassist_lung_agent.main:app --host 0.0.0.0 --port 8000
```

访问 API 文档：

```text
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

如果 Qwen 模型较大，建议在算力云 GPU 服务器上运行，并使用 `QWEN_LOAD_IN_4BIT=1` 尝试 4-bit 加载。

## 添加 RAG 文档

方式一：直接把 `.txt` / `.md` 放到 `docs/knowledge/`，然后重建索引：

```powershell
python scripts/build_rag_index.py
```

方式二：从网页下载清洗成 TXT：

```powershell
python scripts/crawl_medical_docs.py --url https://medlineplus.gov/fever.html
python scripts/build_rag_index.py
```

建议优先使用可信来源，例如 MedlinePlus、CDC、Mayo Clinic、国家卫健委、三甲医院科普、临床指南。不要把论坛帖子作为主要依据。

## 模型改进建议

你现在的 CNN 是 ResNet18 二分类，可以作为第一版项目核心。后续可升级：

- 换 DenseNet121 / EfficientNet，并加入 Grad-CAM，可解释性更适合医疗影像项目。
- 用 ChestX-ray14、RSNA Pneumonia Detection Challenge 或 CheXpert 做多标签任务，而不只是 normal/pneumonia。
- 增加 AUROC、Sensitivity、Specificity、F1、混淆矩阵，README 中展示实验表格。
- 对外部测试集做验证，说明泛化能力，简历上会比单一 accuracy 更可信。

## GitHub 上传

我可以帮你初始化 git、提交并推到 GitHub。需要满足其一：

- 你本机已登录 GitHub，并且提供目标仓库 HTTPS/SSH 地址；
- 或你先在 GitHub 创建空仓库，再把地址发给我。

不建议把 `.pth` 大模型权重直接提交到普通 GitHub 仓库；更推荐 Git LFS、Release、Hugging Face、网盘或在 README 写下载方式。

