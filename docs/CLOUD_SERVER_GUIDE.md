# 算力云运行建议

本项目可以本地演示，但以下情况建议拷贝到算力云 GPU 服务器运行：

- 接入 Qwen 7B 或更大的完整模型。
- 加载 Qwen LoRA adapter 并进行真实推理。
- 重新训练 CNN 或对大量胸片做批量评估。
- 把 RAG 从 TF-IDF 升级为 embedding 向量检索，并批量构建向量库。

## 本地够用的场景

- Web demo。
- 单张胸片 ResNet18 推理。
- TF-IDF RAG 检索。
- 小规模功能测试。

## 推荐云服务器流程

```bash
git clone https://github.com/LuKiovo/medassist-lung-agent.git
cd medassist-lung-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

上传模型权重到数据盘，例如：

```text
/root/autodl-tmp/models/best_model_resnet18.pth
/root/autodl-tmp/models/qwen-medical-merged
```

创建 `.env`：

```bash
CHEST_MODEL_PATH=/root/autodl-tmp/models/best_model_resnet18.pth
RAG_DOC_DIR=docs/knowledge
RAG_INDEX_PATH=data/rag_index.pkl
QWEN_MODEL_PATH=/root/autodl-tmp/models/qwen-medical-merged
QWEN_LOAD_IN_4BIT=1
```

启动：

```bash
bash scripts/start_cloud.sh
```

## 资源提醒

不要在 CPU 上硬跑大模型。若没有 GPU，建议先保持 Qwen 未配置，让系统走 RAG fallback；等云服务器准备好后再配置 Qwen。

