"""LLM backends: the real Anthropic API, and a mock used for offline tests."""
from __future__ import annotations

import asyncio
import random
import time
from typing import Dict, Optional

from .config import MODELS


class FatalAPIError(RuntimeError):
    """Stop the whole run (bad key, spend limit reached, unknown model, ...)."""


class AnthropicAgent:
    def __init__(self, model: str, max_retries: int = 8, timeout: float = 120.0):
        import anthropic  # imported lazily so tests run without the SDK configured

        if model not in MODELS:
            raise ValueError(f"unknown model {model!r}; add it to simtrust/config.py")
        self.model = model
        self.cfg = MODELS[model]
        self._anthropic = anthropic
        # the SDK reads ANTHROPIC_API_KEY from the environment and retries 429/5xx with backoff
        self.client = anthropic.AsyncAnthropic(max_retries=max_retries, timeout=timeout)

    async def complete(self, system: str, user: str, meta: Optional[dict] = None) -> Dict:
        a = self._anthropic
        t0 = time.time()
        try:
            resp = await self.client.messages.create(
                model=self.model,
                max_tokens=self.cfg["max_tokens"],
                system=system,
                messages=[{"role": "user", "content": user}],
                extra_body=self.cfg.get("extra_body") or None,
            )
        except a.AuthenticationError as e:
            raise FatalAPIError(f"API key rejected ({e}). Check ANTHROPIC_API_KEY in your .env file.") from e
        except a.PermissionDeniedError as e:
            raise FatalAPIError(f"Permission denied: {e}") from e
        except a.NotFoundError as e:
            raise FatalAPIError(f"Model {self.model!r} not found: {e}") from e
        except a.BadRequestError as e:
            msg = str(e)
            if "usage limits" in msg or "credit balance" in msg.lower():
                raise FatalAPIError(f"Spend limit / credits exhausted: {msg}") from e
            return {"text": "", "stop_reason": "bad_request", "error": msg[:500],
                    "input_tokens": 0, "output_tokens": 0, "latency": time.time() - t0}
        except a.RateLimitError as e:
            if "enforced_spend_limit" in str(e) or "usage threshold" in str(e):
                raise FatalAPIError(f"Monthly spend cap reached: {e}") from e
            return {"text": "", "stop_reason": "rate_limited", "error": str(e)[:500],
                    "input_tokens": 0, "output_tokens": 0, "latency": time.time() - t0}
        except (a.APIConnectionError, a.APITimeoutError, a.InternalServerError) as e:
            return {"text": "", "stop_reason": "api_error", "error": str(e)[:500],
                    "input_tokens": 0, "output_tokens": 0, "latency": time.time() - t0}

        text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text")
        u = resp.usage
        in_tok = (u.input_tokens or 0) + (getattr(u, "cache_creation_input_tokens", 0) or 0) \
            + (getattr(u, "cache_read_input_tokens", 0) or 0)
        return {"text": text, "stop_reason": resp.stop_reason, "error": None,
                "input_tokens": in_tok, "output_tokens": u.output_tokens or 0,
                "latency": time.time() - t0, "response_model": resp.model}

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.cfg["price_in"] + output_tokens * self.cfg["price_out"]) / 1e6


class MockAgent:
    """Synthetic player with a known behavioral policy, for testing the pipeline end to end.

    Alice simulates less as c rises (the "intuitive" pattern), Bobble defects more when it is
    not told it can be simulated.  ~3% of answers are malformed to exercise the retry path.
    """

    def __init__(self, model: str = "mock", seed: int = 0, malformed_rate: float = 0.03):
        self.model = model
        self.rng = random.Random(seed)
        self.malformed_rate = malformed_rate
        self.cfg = {"price_in": 0.0, "price_out": 0.0}

    async def complete(self, system: str, user: str, meta: Optional[dict] = None) -> Dict:
        await asyncio.sleep(0)
        meta = meta or {}
        r = self.rng
        labels = meta["labels"]  # canonical -> shown
        if meta["role"] == "alice":
            c = meta.get("c")
            if c is None:
                probs = {"TRUST": 0.4, "WALK_OUT": 0.6}
            else:
                s = max(0.0, 0.9 - c / 40)
                probs = {"SIMULATE": s, "TRUST": (1 - s) * 0.3, "WALK_OUT": (1 - s) * 0.7}
            belief = r.randint(5, 40)
        else:
            pd = 0.08 if meta.get("informed") and meta.get("c") is not None else 0.45
            probs = {"DEFECT": pd, "COOPERATE": 1 - pd}
            belief = r.randint(20, 80)
        acts, ws = zip(*probs.items())
        a = r.choices(acts, ws)[0]
        if r.random() < self.malformed_rate:
            text = "I am not sure what to do here."
        else:
            text = f"Weighing the payoffs, I choose this.\nDECISION: {labels[a]}\nBELIEF: {belief}"
        return {"text": text, "stop_reason": "end_turn", "error": None,
                "input_tokens": len(user) // 4, "output_tokens": len(text) // 4, "latency": 0.0}

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return 0.0
