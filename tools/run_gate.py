"""Запускает LLM-гейт в минимальном контексте: без инструментов, настроек, памяти и MCP.

Запуск: python run_gate.py G01 --packet G01.md --out results/
Путь к Claude Code задаётся переменной CLAUDE_BIN.
"""
import argparse
import json
import os
import pathlib
import subprocess

SYSTEM = "Ты независимый ревьюер документации. Выполни инструкцию из начала сообщения. Отвечай на русском."


def run(packet, model):
    command = [
        os.environ.get("CLAUDE_BIN", "claude"), "-p",
        "--model", model,
        "--tools", "",
        "--strict-mcp-config",
        "--setting-sources", "",
        "--no-session-persistence",
        "--system-prompt", SYSTEM,
        "--output-format", "json",
    ]
    done = subprocess.run(command, input=packet, capture_output=True, encoding="utf-8", timeout=300)
    if done.returncode:
        raise SystemExit(done.stdout[-800:] + done.stderr[-800:])
    return json.loads(done.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gate")
    parser.add_argument("--packet", type=pathlib.Path)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()

    text = args.packet.read_text(encoding="utf-8") if args.packet else "Ответь одним словом: готово."
    reply = run(text, args.model)
    usage = reply.get("usage", {})
    fresh = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
    summary = {
        "gate": args.gate,
        "model": args.model,
        "fresh_input": fresh,
        "cache_read": usage.get("cache_read_input_tokens", 0),
        "output": usage.get("output_tokens", 0),
        "total": fresh + usage.get("cache_read_input_tokens", 0) + usage.get("output_tokens", 0),
        "cost_usd": reply.get("total_cost_usd"),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{args.gate}.md").write_text(reply.get("result", ""), encoding="utf-8")
    (args.out / f"{args.gate}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
