# 部署说明

## 本地开发

```powershell
cd F:\Agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/build_rag_index.py
python -m uvicorn medassist_lung_agent.main:app --host 0.0.0.0 --port 8000
```

打开：

```text
http://127.0.0.1:8000/
```

## 算力云 GPU 服务器

1. 克隆仓库。

```bash
git clone https://github.com/LuKiovo/medassist-lung-agent.git
cd medassist-lung-agent
```

2. 安装依赖。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. 上传或下载模型权重。

建议把 `best_model_resnet18.pth` 放在服务器的数据盘，例如：

```text
/root/autodl-tmp/models/best_model_resnet18.pth
```

然后配置环境变量：

```bash
export CHEST_MODEL_PATH=/root/autodl-tmp/models/best_model_resnet18.pth
export RAG_DOC_DIR=docs/knowledge
export RAG_INDEX_PATH=data/rag_index.pkl
```

4. 构建 RAG 索引并启动服务。

```bash
python scripts/build_rag_index.py
python -m uvicorn medassist_lung_agent.main:app --host 0.0.0.0 --port 8000
```

5. 如果接入 Qwen 微调模型。

```bash
export QWEN_MODEL_PATH=/root/autodl-tmp/models/qwen-medical-lora-or-merged
export QWEN_LOAD_IN_4BIT=1
```

如果是 LoRA 权重，建议先合并成完整模型目录，或后续在 `medassist_lung_agent/llm/qwen_client.py` 里补 PEFT 加载逻辑。

## 模型文件不要直接提交

GitHub 普通仓库不适合直接提交 `.pth`、`.pt`、`.safetensors` 等大文件。推荐方式：

- GitHub Releases：适合几十 MB 到几百 MB 的权重。
- Hugging Face Hub：适合模型版本管理和下载。
- 云盘或对象存储：适合毕设答辩时临时分发。

README 中写清楚模型下载路径和放置位置即可。

