from functools import lru_cache

from medassist_lung_agent.config import settings


@lru_cache(maxsize=1)
def _load_pipeline():
    if not settings.qwen_model_path:
        return None

    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    tokenizer = AutoTokenizer.from_pretrained(settings.qwen_model_path, trust_remote_code=True)
    model_kwargs = {"device_map": "auto", "trust_remote_code": True}
    if settings.qwen_load_in_4bit:
        model_kwargs["load_in_4bit"] = True
    model = AutoModelForCausalLM.from_pretrained(settings.qwen_model_path, **model_kwargs)
    return pipeline("text-generation", model=model, tokenizer=tokenizer)


def generate_with_qwen(prompt: str) -> str | None:
    pipe = _load_pipeline()
    if pipe is None:
        return None
    out = pipe(prompt, max_new_tokens=512, do_sample=False, return_full_text=False)
    return out[0]["generated_text"].strip()

