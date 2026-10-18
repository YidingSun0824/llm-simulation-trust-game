"""Run games between LLM agents and log every call.

One *game* in a cell (frame, c, informed):
  1. Alice and Bobble each get their own prompt and answer independently (simultaneous move).
  2. If Alice chose SIMULATE, Bobble's *exact same prompt* is sent once more: that answer is the
     sandboxed copy.  Two fidelity conditions are then resolved from the same game:
       perfect  - the simulation reveals Bobble's real answer (a seeded replay of the same model);
       sampled  - the simulation reveals the independent copy's answer (a fresh run of the model).
     Alice follows the simulation (trust iff it showed COOPERATE), as in the paper.
  3. One JSON line is appended to results/raw/<run>.jsonl.  Re-running resumes where it stopped.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from .agents import FatalAPIError
from .config import cell_id, cells
from .frames import FRAMES
from .parse import parse_response
from .prompts import alice_prompt, bobble_prompt

RESULTS = Path(__file__).resolve().parent.parent / "results"


def _seed(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class CostTracker:
    def __init__(self, budget: float):
        self.budget = budget
        self.spent = 0.0
        self.calls = 0
        self.in_tok = 0
        self.out_tok = 0

    def add(self, agent, r: Dict):
        self.calls += 1
        self.in_tok += r.get("input_tokens", 0)
        self.out_tok += r.get("output_tokens", 0)
        self.spent += agent.cost(r.get("input_tokens", 0), r.get("output_tokens", 0))

    @property
    def exhausted(self) -> bool:
        return self.spent >= self.budget


class Runner:
    def __init__(self, agents: Dict[str, object], out_path: Path, budget: float = 30.0,
                 concurrency: int = 8, verbose: bool = True):
        self.agents = agents  # model name -> agent
        self.out_path = Path(out_path)
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        self.prompt_dir = self.out_path.parent.parent / "prompts"
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
        self.tracker = CostTracker(budget)
        self.concurrency = concurrency
        self.sem = asyncio.Semaphore(concurrency)
        self.verbose = verbose
        self.fatal: Optional[str] = None
        self._saved_prompts = set(p.stem for p in self.prompt_dir.glob("*.txt"))

    # ---------------------------------------------------------------- helpers
    def done_ids(self) -> set:
        if not self.out_path.exists():
            return set()
        ids = set()
        with open(self.out_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ids.add(json.loads(line)["game_id"])
                    except (json.JSONDecodeError, KeyError):
                        pass
        return ids

    def _save_prompt(self, system: str, user: str) -> str:
        h = _sha(system + "\n\n" + user)
        if h not in self._saved_prompts:
            (self.prompt_dir / f"{h}.txt").write_text(f"[SYSTEM]\n{system}\n\n[USER]\n{user}\n")
            self._saved_prompts.add(h)
        return h

    async def _call(self, agent, system: str, user: str, meta: dict, allowed: List[str]) -> Dict:
        """One model answer, with up to 2 extra attempts on parse failure or transient errors."""
        attempts = []
        for attempt in range(3):
            if self.fatal:
                raise FatalAPIError(self.fatal)
            async with self.sem:
                r = await agent.complete(system, user, meta)
            self.tracker.add(agent, r)
            label, belief = parse_response(r["text"], allowed)
            attempts.append({"text": r["text"], "stop_reason": r["stop_reason"], "error": r.get("error"),
                             "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"],
                             "latency": round(r.get("latency", 0.0), 3)})
            if label is not None:
                return {"label": label, "belief": belief, "attempts": attempts}
            if r["stop_reason"] in ("rate_limited", "api_error"):
                await asyncio.sleep(10 * (attempt + 1))
            if r["stop_reason"] == "refusal":
                break  # a safety refusal is data, not noise: record it, don't resample it away
        return {"label": None, "belief": None, "attempts": attempts}

    # ---------------------------------------------------------------- one game
    async def play(self, model: str, frame_name: str, c, informed: bool, idx: int) -> Optional[dict]:
        agent = self.agents[model]
        frame = FRAMES[frame_name]
        g = frame.game
        cid = cell_id(frame_name, c, informed)
        game_id = f"{model}|{cid}|{idx}"
        rng_a = random.Random(_seed(game_id, "alice"))
        rng_b = random.Random(_seed(game_id, "bobble"))

        sa, ua, ma = alice_prompt(frame, c, informed, rng_a)
        sb, ub, mb = bobble_prompt(frame, c, informed, rng_b)
        ha, hb = self._save_prompt(sa, ua), self._save_prompt(sb, ub)
        a_allowed = [frame.alice_labels[x] for x in ma["order"]]
        b_allowed = [frame.bobble_labels[x] for x in mb["order"]]
        meta_a = {"role": "alice", "c": c, "informed": informed, "frame": frame_name, "labels": frame.alice_labels}
        meta_b = {"role": "bobble", "c": c, "informed": informed, "frame": frame_name, "labels": frame.bobble_labels}

        ra, rb = await asyncio.gather(self._call(agent, sa, ua, meta_a, a_allowed),
                                      self._call(agent, sb, ub, meta_b, b_allowed))
        a = frame.alice_from_label(ra["label"]) if ra["label"] else None
        b = frame.bobble_from_label(rb["label"]) if rb["label"] else None

        rcopy = None
        b_copy = None
        if a == "SIMULATE":
            rcopy = await self._call(agent, sb, ub, meta_b, b_allowed)  # the identical message
            b_copy = frame.bobble_from_label(rcopy["label"]) if rcopy["label"] else None

        perfect = sampled = None
        if a and b:
            perfect = g.payoff(a, b, c or 0)
            if a != "SIMULATE":
                sampled = perfect
            elif b_copy:
                sampled = g.payoff_sampled(a, b, b_copy, c)

        return {
            "game_id": game_id, "model": model, "frame": frame_name, "cell": cid,
            "c": c, "sim_available": c is not None, "informed": bool(informed and c is not None), "idx": idx,
            "alice_action": a, "alice_belief_defect": ra["belief"], "alice_order": ma["order"], "alice_prompt": ha,
            "bobble_action": b, "bobble_belief_trust": rb["belief"], "bobble_order": mb["order"], "bobble_prompt": hb,
            "copy_action": b_copy, "copy_belief_trust": rcopy["belief"] if rcopy else None,
            "u_alice_perfect": perfect[0] if perfect else None, "u_bobble_perfect": perfect[1] if perfect else None,
            "u_alice_sampled": sampled[0] if sampled else None, "u_bobble_sampled": sampled[1] if sampled else None,
            "alice_attempts": ra["attempts"], "bobble_attempts": rb["attempts"],
            "copy_attempts": rcopy["attempts"] if rcopy else None,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    # ---------------------------------------------------------------- whole run
    async def run(self, preset: dict) -> dict:
        done = self.done_ids()
        jobs = []
        for model, n in preset["models"].items():
            for frame_name, c, informed in cells(preset):
                for i in range(n):
                    gid = f"{model}|{cell_id(frame_name, c, informed)}|{i}"
                    if gid not in done:
                        jobs.append((model, frame_name, c, informed, i))
        # interleave cells so a budget stop or crash leaves a balanced design
        jobs.sort(key=lambda j: (j[4], j[0], j[1], str(j[2]), j[3]))
        total = len(jobs)
        if self.verbose:
            print(f"[run] {len(done)} games already logged, {total} to play -> {self.out_path}", flush=True)
        if total == 0:
            return self.summary(0, 0)

        written = 0
        failed = 0
        t0 = time.time()
        queue: asyncio.Queue = asyncio.Queue()
        for j in jobs:
            queue.put_nowait(j)

        with open(self.out_path, "a") as f:
            async def worker():
                nonlocal written, failed
                while not queue.empty() and not self.fatal:
                    if self.tracker.exhausted:
                        self.fatal = self.fatal or f"budget of ${self.tracker.budget:.2f} reached"
                        break
                    job = queue.get_nowait()
                    try:
                        rec = await self.play(*job)
                    except FatalAPIError as e:
                        self.fatal = str(e)
                        break
                    except Exception as e:  # keep going; the game will be retried on resume
                        failed += 1
                        print(f"[warn] game {job} failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                        continue
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
                    written += 1
                    if self.verbose and (written % 25 == 0 or written == total):
                        el = time.time() - t0
                        eta = el / written * (total - written)
                        print(f"[run] {written}/{total} games  spent ${self.tracker.spent:.3f}  "
                              f"elapsed {el/60:.1f} min  eta {eta/60:.1f} min", flush=True)

            n_workers = max(1, self.concurrency)  # one game in flight per API slot is plenty
            await asyncio.gather(*(worker() for _ in range(n_workers)))

        if self.fatal and self.verbose:
            print(f"[stop] {self.fatal}", flush=True)
        return self.summary(written, failed)

    def summary(self, written: int, failed: int) -> dict:
        t = self.tracker
        return {"games_written": written, "games_failed": failed, "calls": t.calls, "input_tokens": t.in_tok,
                "output_tokens": t.out_tok, "spent_usd": round(t.spent, 4), "stopped_because": self.fatal}
