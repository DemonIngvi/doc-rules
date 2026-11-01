#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Калибровка T-02: запускает гейты на копии примера и считает попадания. Протокол: protocol.md

  uv run calibrate.py check --example <папка> --work <временная папка>   проверить, что дефекты вносятся
  uv run calibrate.py run G01 control --example ... --gates ... --work ... --out ... --runs 5
  uv run calibrate.py report --out <папка результатов>
  uv run calibrate.py sample --out <папка результатов>                   выборка для разметки точности
"""
import argparse
import itertools
import json
import os
import pathlib
import random
import re
import shutil
import statistics
import subprocess
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
SEEDS = {}
SKIP = shutil.ignore_patterns("_bmad", ".claude", ".doc-kit", "node_modules", "__pycache__")
CAP = 8
SAMPLE = 20
SEED = 42
GATES = ("G01", "G08", "G11")
MODEL = ("actors", "processes", "services", "systems", "functions", "components", "data", "stores", "flows", "integrations", "nodes")


def copy_example(example, target, seeds, model=True):
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(example, target, ignore=SKIP)
    if not model:
        for name in MODEL:
            shutil.rmtree(target / "docs" / "architecture" / name, ignore_errors=True)
    for seed in seeds:
        path = target / seed["file"]
        text = path.read_text(encoding="utf-8")
        if text.count(seed["old"]) != 1:
            raise SystemExit(f"{seed['id']}: образец найден {text.count(seed['old'])} раз")
        path.write_text(text.replace(seed["old"], seed["new"]), encoding="utf-8", newline="\n")


def run_series(args):
    plan = SEEDS[args.gate]
    seeds = plan["seeds"] if args.variant.startswith("seeded") else []
    work = args.work / f"{args.gate}-{args.variant}"
    copy_example(args.example, work, seeds, not args.variant.endswith("nomodel"))
    out = args.out / args.gate / args.variant
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONUTF8": "1"}
    for number in range(1, args.runs + 1):
        command = ["uv", "run", "--quiet", str(args.gates / "tools" / "run_gate.py"), args.gate, "--root", str(work),
                   "--force", "--run-id", f"run{number}"]
        if plan.get("target"):
            command += ["--target", str(work / plan["target"])]
        done = subprocess.run(command, capture_output=True, encoding="utf-8", env=env)
        print(args.gate, args.variant, number, done.stdout.strip()[-120:], done.stderr.strip()[-200:], flush=True)
        if done.returncode:
            sys.exit(done.returncode)
    for path in (work / "_quality" / args.gate).glob("*run*.yaml"):
        shutil.copy(path, out / path.name)


def load_runs(out, gate, variant):
    return [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((out / gate / variant).glob("*.yaml"))]


def found(run, seed):
    text = " ".join(f"{f.get('quote', '')} {f['problem']}" for f in run["findings"])
    return bool(re.search(seed["hit"], text, re.I | re.S))


def report(out):
    for gate in GATES:
        for variant in ("seeded", "seeded-nomodel"):
            report_series(out, gate, variant)


def report_series(out, gate, variant):
    if gate in SEEDS:
        seeds = SEEDS[gate]["seeds"]
        runs = load_runs(out, gate, variant)
        if not runs:
            return
        print(f"\n## {gate} {variant}: запусков {len(runs)}")
        rows = [[found(run, seed) for seed in seeds] for run in runs]
        recall = [sum(row) / len(seeds) for row in rows]
        pairs = [sum(a or b for a, b in zip(x, y)) / len(seeds) for x, y in itertools.combinations(rows, 2)]
        print(f"Полнота запуска: {statistics.mean(recall):.0%}, от {min(recall):.0%} до {max(recall):.0%}")
        print(f"Полнота двух запусков: {statistics.mean(pairs):.0%}")
        print(f"Полнота всех запусков: {sum(any(c) for c in zip(*rows)) / len(seeds):.0%}")
        for index, seed in enumerate(seeds):
            print(f"  {seed['id']} {seed['kind']}: {sum(row[index] for row in rows)} из {len(rows)}")
        for name in (variant, variant.replace("seeded", "control")):
            part = load_runs(out, gate, name)
            if part:
                tokens = [r["tokens"] for r in part]
                capped = sum(len(r["findings"]) >= CAP for r in part)
                verdicts = ", ".join(sorted(r["verdict"] for r in part))
                print(f"  {name}: токены {statistics.mean(tokens):.0f} ({min(tokens)}–{max(tokens)}), потолок {capped} из {len(part)}, вердикты {verdicts}")


def sample(out):
    rng = random.Random(SEED)
    result = {}
    for gate in [g for g in GATES if g in SEEDS]:
        seeds = SEEDS[gate]["seeds"]
        pool = []
        for variant in ("control", "seeded"):
            for index, run in enumerate(load_runs(out, gate, variant), 1):
                for finding in run["findings"]:
                    text = f"{finding.get('quote', '')} {finding['problem']}"
                    if not any(re.search(seed["hit"], text, re.I | re.S) for seed in seeds):
                        pool.append({"run": f"{variant}-{index}", "level": finding["level"], "quote": finding["quote"], "problem": finding["problem"]})
        rng.shuffle(pool)
        result[gate] = [{"n": n, **item} for n, item in enumerate(pool[:SAMPLE], 1)]
    keyed = {gate: [item.pop("run") for item in items] for gate, items in result.items()}
    (out / "sample.yaml").write_text(yaml.safe_dump(result, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    (out / "sample-key.json").write_text(json.dumps(keyed, ensure_ascii=False, indent=1), encoding="utf-8")
    print({gate: len(items) for gate, items in result.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["check", "run", "report", "sample"])
    parser.add_argument("gate", nargs="?", choices=GATES)
    parser.add_argument("variant", nargs="?", choices=["control", "seeded", "control-nomodel", "seeded-nomodel"])
    parser.add_argument("--seeds", default="seeds.yaml")
    parser.add_argument("--example", type=pathlib.Path)
    parser.add_argument("--gates", type=pathlib.Path)
    parser.add_argument("--work", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path)
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    SEEDS.update(yaml.safe_load((HERE / args.seeds).read_text(encoding="utf-8")))
    if args.command == "check":
        for gate in SEEDS:
            copy_example(args.example, args.work / f"check-{gate}", SEEDS[gate]["seeds"])
            print(gate, "дефектов внесено:", len(SEEDS[gate]["seeds"]))
    elif args.command == "run":
        run_series(args)
    elif args.command == "report":
        report(args.out)
    else:
        sample(args.out)


if __name__ == "__main__":
    main()
