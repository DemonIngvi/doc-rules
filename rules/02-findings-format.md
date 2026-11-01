# Формат результата гейта

Каждый гейт записывает результат в едином формате.

```yaml
gate: G01
target: 1-1-project-team-и-role.md
input_hash: sha256 входного пакета
run_by: run_gate.py sonnet
author: кто писал документ
verdict: pass | concerns | fail
tokens: 7691
estimate: 9000
not_checked: что гейт не проверял
findings:
  - level: blocker | minor
    quote: дословная цитата из документа
    problem: что отсутствует или неверно
    decision: accepted | rejected | deferred
    decided_by: человек или pending
```

## Правила

- Вердикт `pass` при неразобранном `blocker` недопустим.
- Если `run_by` совпадает с `author`, вердикт недействителен.
- Если хеш входа изменился, вердикт устарел и гейт запускается снова.
- Находка без дословной цитаты отбрасывается скриптом.
- Отвергнутые находки сохраняются: по ним считается точность гейта.
