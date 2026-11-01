# Документация на новый проект

Как устроены репозитории и что происходит при создании документации, например для проекта `acme`.

## Репозитории инструментов

| Репозиторий | Видимость | За что отвечает |
| --- | --- | --- |
| [BMAD-METHOD](https://github.com/DemonIngvi/BMAD-METHOD) | Приватный | BMad Method: `upstream` — чистая копия оригинала, `custom` — наши правки |
| [doc-kit](https://github.com/DemonIngvi/doc-kit) | Публичный | Создание проекта и закрепление версий |
| [doc-architecture](https://github.com/DemonIngvi/doc-architecture) | Публичный | Архитектура в YAML, сборка Spine |
| [doc-gates](https://github.com/DemonIngvi/doc-gates) | Публичный | Проверки и запуск LLM-гейтов |
| [doc-rules](https://github.com/DemonIngvi/doc-rules) | Публичный | Правила, исследования, замеры, план |
| [doc-publisher](https://github.com/DemonIngvi/doc-publisher) | Публичный | Публикация в Docmost |
| [docmost-stack](https://github.com/DemonIngvi/docmost-stack) | Публичный | Запуск Docmost |
| [documentation_docmost](https://github.com/DemonIngvi/documentation_docmost) | Публичный | Пример: проект «Вектор» |
| rnd-helper | Приватный | Помощник человека в R&D, каркас |
| sdd-helper | Приватный | Помощник человека в требованиях, каркас |

Каждый репозиторий меняется и выпускает версии независимо.

## Два слоя

- **Слой для ИИ:** BMAD, YAML, проверки. Здесь живут факты.
- **Слой для человека:** Docmost. Страницы генерируются из слоя для ИИ, правки там не считаются источником.

## Как начать

```
python doc-kit/tools/kit.py init acme --dir D:/projects --github
```

`doc-kit` создаёт `acme-docs`, устанавливает закреплённые версии `BMAD-METHOD`, `doc-architecture` и `doc-gates`. `doc-publisher` и `docmost-stack` работают отдельно от проекта.

После первого Spine навык `doc-arch` раскладывает архитектуру на единицы и ведёт заполнение модели системы: участники, системы, данные, функции, процессы, сервисы, компоненты, хранилища, интеграции и потоки. `check.py` проверяет связи и считает готовность.

Страницы C1, C2, C3, реестры и панель готовности подключаются в `docmost.yaml` через поле `view`.

## Что вызывает ИИ

ИИ работает только в `acme-docs` и вызывает установленные там навыки. Правила читает из `doc-rules`. В репозитории инструментов во время проекта он ничего не пишет.

## Последовательность

| # | Что происходит | Что запускается | Где меняется |
| --- | --- | --- | --- |
| 1 | Создание проекта | `doc-kit` | Новый `acme-docs`, `doc.lock.yaml` |
| 2 | Бриф, PRD, UX | Навыки BMAD | `acme-docs/_bmad-output` |
| 3 | Механические проверки | `doc-check` | `acme-docs/_quality` |
| 4 | Архитектура | `bmad-architecture`, затем `doc-arch` | `acme-docs/docs/architecture`, Spine собирается |
| 5 | Эпики и истории | Навыки BMAD | `acme-docs/_bmad-output` |
| 6 | Независимый вердикт | `doc-gate` G11, затем подпись человека | `acme-docs/_quality` |
| 7 | Публикация | `doc-publisher` | Пространство `acme` в Docmost |
| 8 | Перед кодом по истории | `doc-check`, `doc-gate` G01 | `acme-docs/_quality` |
| 9 | Реализация | `bmad-build` | Репозиторий кода `acme` |

## Что появляется в результате

- `acme-docs`: документация и результаты проверок, приватный репозиторий.
- `acme`: код, создаётся на шаге 9.
- Пространство в Docmost: не репозиторий, а генерируемое представление.

## Обновления

Улучшение инструмента делается в его репозитории и выходит новой версией. Проект переходит на неё правкой строки в `doc.lock.yaml` и командой `kit.py sync`.

BMAD обновляется так: новая версия приходит в `upstream`, ветка `custom` переносится поверх неё, выходит тег `custom-<версия>.<номер>`. Подробности в `CUSTOM.md` внутри `BMAD-METHOD`.
