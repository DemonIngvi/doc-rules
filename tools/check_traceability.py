"""Проверяет трассировку примера BMAD: FR -> история -> архитектура."""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\documentation\bmad-example\_bmad-output")
plan = root / "planning-artifacts"
prd = (plan / "prds/prd-bmad-example-2026-11-01/prd.md").read_text(encoding="utf-8")
epics = (plan / "epics.md").read_text(encoding="utf-8")
spine = (plan / "architecture/architecture-bmad-example-2026-11-01/ARCHITECTURE-SPINE.md").read_text(encoding="utf-8")

frs = sorted({int(n) for n in re.findall(r"^#### FR-(\d+):", prd, re.M)})
stories = set(re.findall(r"^### Story (\d+\.\d+):", epics, re.M))
coverage = dict(re.findall(r"^\| FR-(\d+) \| (\d+\.\d+) \|", epics, re.M))
uj = set(re.findall(r"\*\*(UJ-\d+)\.", prd))
ads = re.findall(r"^### (AD-\d+)", spine, re.M)

errors = []
errors += [f"FR-{n} нет в карте покрытия" for n in frs if str(n) not in coverage]
errors += [f"FR-{k} ссылается на несуществующую историю {v}" for k, v in coverage.items() if v not in stories]
errors += [f"История {s} не покрывает ни один FR" for s in sorted(stories) if s not in coverage.values()]
errors += [f"Ссылка на неизвестный {u}" for u in set(re.findall(r"UJ-\d+", prd)) - uj]
errors += [f"FR-{n} нет в frontmatter архитектуры" for n in frs if f"FR-{n}," not in spine and f"FR-{n}]" not in spine]

print(f"FR: {len(frs)}, истории: {len(stories)}, UJ: {len(uj)}, AD: {len(ads)}")
print("\n".join(errors) if errors else "Ошибок трассировки нет")
sys.exit(1 if errors else 0)
