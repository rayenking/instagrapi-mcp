"""Pydantic models (instagrapi types) -> compact JSON-safe dicts for MCP responses."""

from typing import Any

# Strings longer than this are truncated to keep responses token-friendly.
_MAX_STR = 2000


def _prune(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            pruned = _prune(item)
            if pruned in (None, "", [], {}):
                continue
            out[key] = pruned
        return out
    if isinstance(value, (list, tuple)):
        return [_prune(item) for item in value]
    if isinstance(value, str) and len(value) > _MAX_STR:
        return value[:_MAX_STR] + "...[truncated]"
    return value


def to_dict(model: Any) -> dict | list:
    """Serialize a pydantic model (or list of models) into a compact dict/list."""
    if isinstance(model, (list, tuple)):
        return [_prune(_one(item)) for item in model]
    return _prune(_one(model))


def _one(model: Any) -> Any:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    if hasattr(model, "dict"):  # pydantic v1 fallback
        return model.dict()
    return model
