import logging

import comfy.ldm.modules.attention as attention_module


MODE_DISABLED = "disabled"
MODE_SDPA = "sdpa"
MODE_PYTORCH = "pytorch"
MODE_SAGE = "sage"
MODE_FLASH = "flash"

ATTENTION_MODES = [
    MODE_DISABLED,
    MODE_SDPA,
    MODE_PYTORCH,
    MODE_SAGE,
    MODE_FLASH,
]


def _resolve_attention_function(mode: str):
    if mode in (MODE_SDPA, MODE_PYTORCH):
        return attention_module.attention_pytorch

    if mode == MODE_SAGE:
        if not getattr(attention_module, "SAGE_ATTENTION_IS_AVAILABLE", False):
            raise RuntimeError(
                "SageAttention is not available in this ComfyUI environment. "
                "Start ComfyUI with Sage installed, or choose 'sdpa' / 'pytorch' instead."
            )
        return attention_module.attention_sage

    if mode == MODE_FLASH:
        if not getattr(attention_module, "FLASH_ATTENTION_IS_AVAILABLE", False):
            raise RuntimeError(
                "Flash Attention is not available in this ComfyUI environment. "
                "Install flash-attn, or choose 'sdpa' / 'pytorch' instead."
            )
        return attention_module.attention_flash

    raise ValueError(f"Unsupported attention mode: {mode}")


def _make_attention_override(attention_function):
    target = getattr(attention_function, "__wrapped__", attention_function)

    def attention_override(func, *args, **kwargs):
        return target(*args, **kwargs)

    return attention_override


class PerModelAttentionOverride:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "mode": (
                    ATTENTION_MODES,
                    {
                        "default": MODE_DISABLED,
                        "tooltip": (
                            "'disabled' removes the per-model override and falls back to ComfyUI's global "
                            "attention choice. 'sdpa' and 'pytorch' both force PyTorch attention for this model."
                        ),
                    },
                ),
            }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "apply"
    CATEGORY = "loaders/model"
    DESCRIPTION = (
        "Set a per-model attention override. Use this to opt a single model out of global SageAttention "
        "without changing ComfyUI's startup flags."
    )

    def apply(self, model, mode):
        model_clone = model.clone()
        transformer_options = model_clone.model_options.setdefault("transformer_options", {})

        if mode == MODE_DISABLED:
            transformer_options.pop("optimized_attention_override", None)
            logging.info("Per-model attention override cleared; model will use ComfyUI global attention.")
            return (model_clone,)

        attention_function = _resolve_attention_function(mode)
        transformer_options["optimized_attention_override"] = _make_attention_override(attention_function)
        logging.info("Per-model attention override set to '%s'.", mode)
        return (model_clone,)


NODE_CLASS_MAPPINGS = {
    "PerModelAttentionOverride": PerModelAttentionOverride,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PerModelAttentionOverride": "Attention Override (Per Model)",
}
