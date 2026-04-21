# comfy-sageattention-optout-customnodes

Minimal ComfyUI custom node for per-model attention overrides.

This node is intended for the case where ComfyUI is started with a global attention mode such as `--use-sage-attention`, but a specific model needs to opt out and use a different attention implementation.

## Node

`Attention Override (Per Model)`

Modes:

- `disabled`: remove the per-model override and fall back to ComfyUI's global attention selection
- `sdpa`: force PyTorch scaled dot-product attention for this model
- `pytorch`: alias for `sdpa`
- `sage`: force SageAttention for this model
- `flash`: force Flash Attention for this model if available

## Notes

- This node only changes the model passed through it.
- `disabled` does not disable global SageAttention. It only removes the per-model override.
- If ComfyUI was started with global SageAttention and you want one model to opt out, use `sdpa`.

## Donations & Support

If this saves you time, you can support the work here:

- [Patreon](https://www.patreon.com/EnviralDesign)
- [GitHub Sponsors](https://github.com/sponsors/EnviralDesign)
- [PayPal](https://www.paypal.com/donate?hosted_button_id=RP8EJAHSDTZ86)
