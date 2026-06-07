# Qwen 接入说明

当前项目默认不会加载 Qwen。只有配置了 `.env` 或系统环境变量后，健康咨询接口才会在 RAG 检索后调用 Qwen 生成回答。

不建议在普通 CPU 笔记本上加载大 Qwen 模型。加载完整 Qwen 或 LoRA 微调模型可能占用大量内存/显存，建议在算力云 GPU 服务器上运行。小参数模型可尝试本地 CPU，但速度会很慢。

## 为什么之前没有加载

`.env.example` 中的 `QWEN_MODEL_PATH` 默认是空的，所以程序会自动走备用回答逻辑：

```text
QWEN_MODEL_PATH=
```

这不是你的 CNN 模型问题，也不是 RAG 本身不能工作，而是 LLM 没有配置。

## 方式一：加载合并后的完整模型

如果你的微调模型已经合并成完整 Hugging Face 模型目录，目录中通常包含：

```text
config.json
tokenizer.json / tokenizer.model
model.safetensors 或 pytorch_model*.bin
```

在项目根目录新建 `.env`：

```text
CHEST_MODEL_PATH=F:\visual_project\best_model_resnet18.pth
RAG_DOC_DIR=docs/knowledge
RAG_INDEX_PATH=data/rag_index.pkl
QWEN_MODEL_PATH=F:\models\qwen-medical-merged
QWEN_LOAD_IN_4BIT=0
```

Windows 启动：

```powershell
.\start_medassist.bat
```

## 方式二：加载 LoRA adapter

如果你的 GitHub 或训练输出只有 LoRA adapter，目录中通常包含：

```text
adapter_config.json
adapter_model.safetensors
```

这时必须同时提供 base model 和 adapter：

```text
QWEN_BASE_MODEL_PATH=F:\models\Qwen-base
QWEN_ADAPTER_PATH=F:\models\qwen-medical-lora
QWEN_LOAD_IN_4BIT=0
```

如果在云服务器上运行，可以改成 Linux 路径：

```bash
export QWEN_BASE_MODEL_PATH=/root/autodl-tmp/models/Qwen-base
export QWEN_ADAPTER_PATH=/root/autodl-tmp/models/qwen-medical-lora
export QWEN_LOAD_IN_4BIT=1
```

## 判断自己是哪一种模型

- 有 `model.safetensors`、`pytorch_model.bin`、`config.json`：多半是完整模型或合并模型，配置 `QWEN_MODEL_PATH`。
- 有 `adapter_config.json`、`adapter_model.safetensors`：多半是 LoRA adapter，配置 `QWEN_BASE_MODEL_PATH` + `QWEN_ADAPTER_PATH`。
- 只有训练脚本和数据，没有权重文件：还不能直接加载，需要先训练或下载权重。

## 注意

- GitHub 普通仓库不适合存大模型权重；建议放 Hugging Face、Release、网盘或云服务器数据盘。
- Qwen 加载失败时，系统仍会回退到 RAG fallback，不会影响胸片 CNN 分析。
- 真正测试 Qwen 前，应确认机器是否有合适 GPU，避免 CPU 长时间高负载。

