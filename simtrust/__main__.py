"""Command line:  python -m simtrust <command>

  check                       one real call per model in the 'main' preset: key + parameters OK?
  run --preset pilot          play games (presets: smoke, pilot, pilot-sonnet, main, opus)
  estimate --preset main      cost/time estimate, using measured token counts if a pilot exists
  show --n 8                  print random transcripts (read these before the main run!)
  analyze                     tables + figures into results/
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
from pathlib import Path

from .config import MODELS, PRESETS, cells

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw"


_KEY_SOURCE = "unset"


def _load_env():
    """Read .env and let it WIN over any ANTHROPIC_API_KEY already set in the shell
    (Claude Code, conda or an old export can leave a stale key there)."""
    global _KEY_SOURCE
    shell_key = os.environ.get("ANTHROPIC_API_KEY")
    try:
        from dotenv import dotenv_values
        file_key = (dotenv_values(ROOT / ".env").get("ANTHROPIC_API_KEY") or "").strip().strip('"').strip("'")
    except ImportError:
        file_key = ""
    if file_key:
        os.environ["ANTHROPIC_API_KEY"] = file_key
        _KEY_SOURCE = ".env" + (" (overriding a different key set in your shell)" if shell_key and shell_key != file_key else "")
    elif shell_key:
        _KEY_SOURCE = "shell environment variable (no key in .env)"


def _mask(key: str) -> str:
    return f"{key[:11]}…{key[-4:]} ({len(key)} chars)" if len(key) > 16 else "<too short>"


def _need_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key.startswith("sk-ant-") or "PASTE" in key:
        sys.exit("No real API key found. Open .env, replace sk-ant-PASTE-YOUR-KEY-HERE with your key, and SAVE "
                 "(the dot on the editor tab must disappear).")
    if any(ch.isspace() for ch in key):
        sys.exit("The API key in .env contains a space or line break. Put it on one line with nothing after it.")
    print(f"[key] using {_mask(key)} from {_KEY_SOURCE}", flush=True)


def _agents(preset: dict, mock: bool):
    if mock:
        from .agents import MockAgent
        return {m: MockAgent(m, seed=i) for i, m in enumerate(preset["models"])}
    _need_key()
    from .agents import AnthropicAgent
    return {m: AnthropicAgent(m) for m in preset["models"]}


def cmd_run(args):
    from .runner import Runner
    preset = PRESETS[args.preset]
    out = Path(args.out) if args.out else RAW / f"{args.preset}{'-mock' if args.mock else ''}.jsonl"
    runner = Runner(_agents(preset, args.mock), out, budget=args.budget, concurrency=args.concurrency)
    summary = asyncio.run(runner.run(preset))
    print(json.dumps(summary, indent=2))
    if summary["stopped_because"]:
        sys.exit(1)


def cmd_check(args):
    """Send one real Alice prompt and one Bobble prompt per model and show what came back."""
    _need_key()
    from .agents import AnthropicAgent, FatalAPIError
    from .frames import NEUTRAL
    from .parse import parse_response
    from .prompts import alice_prompt, bobble_prompt
    models = list(PRESETS[args.preset]["models"])
    total = 0.0
    for m in models:
        agent = AnthropicAgent(m, max_retries=3)
        for role, fn in (("alice", alice_prompt), ("bobble", bobble_prompt)):
            s, u, meta = fn(NEUTRAL, 10, True, random.Random(0))
            labels = NEUTRAL.alice_labels if role == "alice" else NEUTRAL.bobble_labels
            allowed = [labels[x] for x in meta["order"]]
            try:
                r = asyncio.run(agent.complete(s, u, {"role": role}))
            except FatalAPIError as e:
                sys.exit(f"[check] {m}: {e}")
            cost = agent.cost(r["input_tokens"], r["output_tokens"])
            total += cost
            print(f"--- {m} as {role}: stop={r['stop_reason']} in={r['input_tokens']} out={r['output_tokens']} "
                  f"cost=${cost:.4f} parsed={parse_response(r['text'], allowed)}")
            if r.get("error"):
                print("    ERROR:", r["error"])
            print("    " + r["text"].strip().replace("\n", "\n    "))
    print(f"[check] OK. total spent ${total:.4f}")


def _measured_tokens():
    """Average tokens per call by model, from any existing non-mock logs."""
    stats = {}
    for p in RAW.glob("*.jsonl"):
        if "mock" in p.name:
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            for k in ("alice_attempts", "bobble_attempts", "copy_attempts"):
                for at in r.get(k) or []:
                    s = stats.setdefault(r["model"], [0, 0, 0])
                    s[0] += at["input_tokens"]; s[1] += at["output_tokens"]; s[2] += 1
    return {m: (a / n, b / n) for m, (a, b, n) in stats.items() if n}


def cmd_estimate(args):
    preset = PRESETS[args.preset]
    measured = _measured_tokens()
    n_cells = len(list(cells(preset)))
    grand = 0.0
    for m, n in preset["models"].items():
        tin, tout = measured.get(m, (900, 250))
        src = "measured" if m in measured else "assumed"
        games = n_cells * n
        calls = games * 2.8  # Alice + Bobble + a copy whenever Alice simulates (+ rare retries)
        cost = calls * (tin * MODELS[m]["price_in"] + tout * MODELS[m]["price_out"]) / 1e6
        grand += cost
        print(f"{m:20s} {games:5d} games  ~{calls:6.0f} calls  {tin:5.0f} in / {tout:4.0f} out tok per call "
              f"({src})  ~${cost:6.2f}")
    print(f"{'TOTAL':20s} ~${grand:.2f}   (a 20-30% margin is sensible)")


def cmd_show(args):
    path = Path(args.input) if args.input else max(RAW.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    recs = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    if args.frame:
        recs = [r for r in recs if r["frame"] == args.frame]
    if args.model:
        recs = [r for r in recs if r["model"] == args.model]
    rng = random.Random(args.seed)
    for r in rng.sample(recs, min(args.n, len(recs))):
        print("=" * 100)
        print(f"{r['game_id']}   Alice={r['alice_action']}  Bobble={r['bobble_action']}  copy={r['copy_action']}  "
              f"payoffs(perfect)=({r['u_alice_perfect']}, {r['u_bobble_perfect']})")
        for who in ("alice", "bobble", "copy"):
            if args.role and who != args.role:
                continue
            for at in r.get(f"{who}_attempts") or []:
                print(f"--- {who} [{at['stop_reason']}]")
                print("    " + (at["text"] or "<empty>").strip().replace("\n", "\n    "))
    print(f"\n({len(recs)} games in {path.name})")


def cmd_analyze(args):
    from .analysis import analyze
    inputs = [Path(p) for p in args.input] if args.input else [RAW / "main.jsonl"]
    analyze(inputs, ROOT / "results", tag=args.tag)


def main(argv=None):
    _load_env()
    ap = argparse.ArgumentParser(prog="python -m simtrust", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run"); p.set_defaults(func=cmd_run)
    p.add_argument("--preset", default="pilot", choices=sorted(PRESETS))
    p.add_argument("--budget", type=float, default=30.0, help="hard stop in USD for this invocation")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--mock", action="store_true", help="use a synthetic agent (no API calls, no cost)")
    p.add_argument("--out", default=None)

    p = sub.add_parser("check"); p.set_defaults(func=cmd_check)
    p.add_argument("--preset", default="main", choices=sorted(PRESETS))

    p = sub.add_parser("estimate"); p.set_defaults(func=cmd_estimate)
    p.add_argument("--preset", default="main", choices=sorted(PRESETS))

    p = sub.add_parser("show"); p.set_defaults(func=cmd_show)
    p.add_argument("--input", default=None)
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--frame", choices=["narrative", "neutral"])
    p.add_argument("--model")
    p.add_argument("--role", choices=["alice", "bobble", "copy"])
    p.add_argument("--seed", type=int, default=0)

    p = sub.add_parser("analyze"); p.set_defaults(func=cmd_analyze)
    p.add_argument("--input", nargs="*", default=None)
    p.add_argument("--tag", default="")

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
