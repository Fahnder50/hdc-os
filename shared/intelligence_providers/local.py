import ipaddress
import json
from typing import Any, Mapping
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from shared.intelligence_layer.contracts import ProviderKind


def _local_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http" or not parsed.hostname:
        raise ValueError("Local model endpoint must use plain HTTP on loopback")
    try:
        loopback = ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError as error:
        raise ValueError("Model endpoint must be a numeric loopback address") from error
    if not loopback:
        raise ValueError("Cloud and non-loopback model endpoints are forbidden")
    return endpoint.rstrip("/")


class OllamaProvider:
    provider_kind = ProviderKind.OLLAMA
    provider_name = "ollama"

    def __init__(self, model: str, endpoint: str, timeout_seconds: float):
        if not model.strip():
            raise ValueError("A local model name is required")
        self.model, self.endpoint, self.timeout_seconds = model, _local_endpoint(endpoint), timeout_seconds

    def generate(self, prompt: str, schema: Mapping[str, Any]) -> Mapping[str, Any]:
        body = json.dumps({"model": self.model, "stream": False, "format": schema, "messages": [{"role": "user", "content": prompt}], "options": {"temperature": 0}}).encode()
        request = Request(f"{self.endpoint}/api/chat", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(json.loads(response.read().decode())["message"]["content"])


class LlamaCppProvider:
    provider_kind = ProviderKind.LLAMACPP
    provider_name = "llamacpp"

    def __init__(self, model: str, endpoint: str, timeout_seconds: float):
        self.model, self.endpoint, self.timeout_seconds = model, _local_endpoint(endpoint), timeout_seconds

    def generate(self, prompt: str, schema: Mapping[str, Any]) -> Mapping[str, Any]:
        body = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "response_format": {"type": "json_object", "schema": schema}}).encode()
        request = Request(f"{self.endpoint}/v1/chat/completions", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(json.loads(response.read().decode())["choices"][0]["message"]["content"])


def provider_from_config(kind: str, model: str, endpoint: str, timeout_seconds: float):
    providers = {ProviderKind.OLLAMA: OllamaProvider, ProviderKind.LLAMACPP: LlamaCppProvider}
    try:
        provider_kind = ProviderKind(kind.upper())
    except ValueError as error:
        raise ValueError("Provider must be OLLAMA, LLAMACPP, LOCAL_MODEL or DETERMINISTIC") from error
    if provider_kind not in providers:
        raise ValueError(f"{provider_kind.value} requires an injected local provider implementation")
    return providers[provider_kind](model, endpoint, timeout_seconds)
