from functools import lru_cache

import torch

from medassist_lung_agent.config import settings


@lru_cache(maxsize=1)
def _load_pipeline():
    model_path = settings.qwen_model_path
    adapter_path = settings.qwen_adapter_path
    base_model_path = settings.qwen_base_model_path

    if not model_path and not (adapter_path and base_model_path):
        return None

    from transformers import AutoModelForCausalLM, AutoTokenizer

    load_path = base_model_path if adapter_path else model_path
    tokenizer = AutoTokenizer.from_pretrained(load_path, trust_remote_code=True)
    model_kwargs = {
        "device_map": "auto",
        "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
        "trust_remote_code": True,
    }
    if settings.qwen_load_in_4bit:
        model_kwargs["load_in_4bit"] = True
    model = AutoModelForCausalLM.from_pretrained(load_path, **model_kwargs)

    if adapter_path:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    return tokenizer, model


def _build_prompt(tokenizer, prompt: str):
    messages = [
        {"role": "system", "content": "你是一个谨慎的中文医疗健康科普助手，必须基于资料回答，不能替代医生诊断或处方。"},
        {"role": "user", "content": prompt},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return prompt


def generate_with_qwen(prompt: str) -> str | None:
    loaded = _load_pipeline()
    if loaded is None:
        return None
    tokenizer, model = loaded
    formatted = _build_prompt(tokenizer, prompt)
    inputs = tokenizer(formatted, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = output_ids[0][inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
