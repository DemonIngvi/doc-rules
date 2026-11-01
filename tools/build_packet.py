"""Собирает узкий пакет для LLM-гейта, чтобы агент читал один файл, а не весь проект."""
import argparse
import pathlib
import re

BRIEFS = {
    "G01": """Гейт G01. Ты независимый ревьюер, автор документов тебе неизвестен.
Вопрос: какие решения разработчику придётся придумать самому, чтобы реализовать эту историю?
Считай находкой только решение, которого нет в пакете. Вкусовые вопросы и детали кода не находки.
Для каждой находки дай: цитату из истории, которое решение отсутствует, уровень blocker или minor.
Не более 8 находок. Без вступлений.""",
    "G02": """Гейт G02. Ты независимый ревьюер архитектуры.
Домены: аутентификация, авторизация, данные и миграции, ошибки, конфигурация и секреты, безопасность,
наблюдаемость, развёртывание, резервное копирование, производительность, внешние зависимости.
Для каждого домена укажи: decided, deferred или silent, и дай цитату. Silent значит: решения нет и отсрочка не записана.
Без вступлений, одна строка на домен.""",
    "G08": """Гейт G08. Проверь только критерии приёмки ниже.
Критерий плох, если по нему нельзя написать автотест без догадок о данных, времени или ожидаемом результате.
Для каждого плохого критерия дай цитату, причину и как переписать. Хорошие не перечисляй.
Не более 8 находок. Без вступлений.""",
    "G11": """Гейт G11. Ты независимый ревьюер, автор документов тебе неизвестен.
Вопрос: может ли разработчик реализовать эти эпики, не придумывая незаписанных решений?
Вердикт: PASS, CONCERNS или FAIL. Сначала вердикт, затем не более 8 находок с цитатами, по важности.
Не учитывай вердикты других документов. Без вступлений.""",
}


def section(text, start, stop=None):
    """Возвращает часть документа от заголовка start до заголовка stop."""
    begin = text.index(start)
    end = text.index(stop, begin + 1) if stop else len(text)
    return text[begin:end].strip()


def glossary(prd):
    return section(prd, "## 3. Glossary", "## 4. Features")


def epic(epics, number):
    following = f"## Epic {number + 1}:"
    return section(epics, f"## Epic {number}:", following if following in epics else None)


def criteria_only(text):
    """Оставляет названия историй и критерии, отбрасывая формулировки As a / I want."""
    keep = [line for line in text.splitlines()
            if re.match(r"(### Story|\*\*Given|\*\*When|\*\*Then|\*\*And)", line)]
    return "\n".join(keep)


def build(gate, root):
    output = root / "_bmad-output"
    plan = output / "planning-artifacts"
    impl = output / "implementation-artifacts"
    prd = (plan / "prds/prd-bmad-example-2026-11-01/prd.md").read_text(encoding="utf-8")
    spine = (plan / "architecture/architecture-bmad-example-2026-11-01/ARCHITECTURE-SPINE.md").read_text(encoding="utf-8")
    epics = (plan / "epics.md").read_text(encoding="utf-8")
    experience = (plan / "ux-designs/ux-bmad-example-2026-11-01/EXPERIENCE.md").read_text(encoding="utf-8")
    story = (impl / "1-1-project-team-и-role.md").read_text(encoding="utf-8")
    parts = {
        "G01": [story, spine, glossary(prd)],
        "G02": [spine],
        "G08": [criteria_only(epic(epics, 1))],
        "G11": [prd, spine, epics, experience],
    }[gate]
    return "\n\n---\n\n".join([BRIEFS[gate], *parts])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gate", choices=sorted(BRIEFS))
    parser.add_argument("--root", default=r"D:\documentation\bmad-example", type=pathlib.Path)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()
    packet = build(args.gate, args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(packet, encoding="utf-8")
    print(args.gate, len(packet), "символов")
