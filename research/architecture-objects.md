# Объекты YAML для описания архитектуры

Статус: **черновик, в код не внедрён**. Сначала нужна проба на примере «Вектор» и сравнение с текущими единицами.

Основа: TOGAF, ArchiMate, SIPOC, C4. По стандартам прочитаны обзоры и справочные страницы, а не полные тексты. Перед внедрением формулировки нужно сверить с первоисточниками.

## Что не так сейчас

Текущие единицы повторяют разделы документа BMAD, а не устройство системы. В них нет бизнес-процессов, функций, объектов данных и потоков. Часть файлов к архитектуре не относится: это служебные данные сборки и правила кода.

## Что взято из стандартов

| Источник | Что берём | Что не берём |
| --- | --- | --- |
| TOGAF | Четыре слоя: бизнес, данные, приложения, технологии. Разделение логического и физического. Право убирать сущности из метамодели | Всю метамодель и управление на уровне предприятия |
| ArchiMate | Разделение на активные части, поведение и пассивные данные. Связи serving, access, flow | Графическую нотацию и полный набор связей |
| SIPOC | Пять полей процесса: поставщики, входы, процесс, выходы, потребители | Отдельную диаграмму |
| C4 | Вложенность: система, контейнер, компонент | Названия уровней не меняем: C1, C2, C3 |

## Предлагаемый список

| Слой | Объект | Файл | Что описывает | Главные поля |
| --- | --- | --- | --- | --- |
| Бизнес | Участник | `actors/<id>.yaml` | Роль или внешняя организация | `kind`, `goals` |
| Бизнес | Процесс | `processes/<id>.yaml` | Бизнес-процесс по SIPOC | `suppliers`, `inputs`, `steps`, `outputs`, `customers`, `functions` |
| Приложения | Система | `systems/<id>.yaml` | Своя или внешняя система, C1 | `kind`, `owner` |
| Приложения | Функция | `functions/<id>.yaml` | Что система делает для процесса | `system`, `reqs`, `reads`, `writes` |
| Приложения | Компонент | `components/<id>.yaml` | Контейнер внутри системы, C2 | `system`, `tech`, `functions` |
| Приложения | Блок | `blocks/<компонент>/<id>.yaml` | Часть компонента, C3 | `functions`, `on_failure` |
| Данные | Объект данных | `data/<id>.yaml` | Логическая сущность | `class`, `sensitivity`, `owner`, `lifecycle`, `attributes` |
| Данные | Хранилище | `stores/<id>.yaml` | Физическое размещение данных | `objects`, `retention`, `backup` |
| Связи | Поток данных | `flows/<id>.yaml` | Что, откуда и куда движется | `from`, `to`, `objects`, `trigger`, `flow_type`, `volume` |
| Связи | Интеграция | `integrations/<id>.yaml` | Как устроен канал | `from`, `to`, `integration_type`, `protocol`, `auth`, `timeout`, `retry`, `idempotent` |
| Технологии | Узел | `nodes/<id>.yaml` | Где запущены компоненты | `environment`, `runs`, `tech` |
| Общее | Типы | `types.yaml` | Допустимые значения | `integration_type`, `flow_type`, `data_class`, `sensitivity` |

Главное различие: **поток отвечает, что движется и зачем, интеграция отвечает, по какому каналу**. Один канал может нести много потоков, поэтому это два объекта.

Простые связи остаются полями: `system`, `reads`, `writes`, `runs`. Отдельный объект нужен только связи со своими атрибутами. Таких две: поток и интеграция.

## Словари типов

```yaml
integration_type: [sync-api, async-queue, webhook, event-stream, file, shared-db, ui]
flow_type: [command, query, event, replication, batch]
data_class: [reference, master, transactional, event, derived]
sensitivity: [public, internal, personal, secret]
```

Значения предварительные. Новое значение вносится в словарь и проверяется скриптом.

## Пример на «Векторе»

```yaml
# processes/intake.yaml
id: intake
title: Приём заявки
suppliers: [заказчик]
inputs: [request]
steps: [принять заявку, найти дубли, превратить в работу]
outputs: [user-story]
customers: [команда]
functions: [request-accept, duplicate-search]
```

```yaml
# flows/F-webhook.yaml
id: F-webhook
title: Событие об изменении Work Item
from: vektor
to: external-system
objects: [work-item]
trigger: изменение Work Item
flow_type: event
over: I-webhook
```

```yaml
# integrations/I-webhook.yaml
id: I-webhook
from: worker
to: external-system
integration_type: webhook
protocol: HTTPS
auth: подпись запроса
timeout: не задан
retry: не менее трёх повторов
idempotent: не задано
```

Поля «не задано» здесь показывают пробелы примера. Пример иллюстрирует форму и не утверждён как архитектура «Вектора».

## Что будет с текущими файлами

| Сейчас | Становится |
| --- | --- |
| `decisions/` | Остаётся: решения объясняют выбор и ссылаются на объекты |
| `components/`, `blocks/`, `stores/` | Остаются с новыми полями |
| `interfaces/` | Переходит в `integrations/` |
| `fmea.yaml`, `params.yaml`, `quality.yaml` | Остаются сквозными, ссылаются на объекты |
| `modules.yaml` | Зависимости компонентов выводятся из интеграций и блоков |
| `capability-map.yaml` | Выводится из `function.reqs` и `component.functions` |
| `stack.yaml` | Остаётся реестром технологий |
| `conventions.yaml`, `deferred.yaml` | Служебные разделы Spine, не объекты архитектуры |
| `frontmatter.yaml`, `_order.yaml`, `sections/` | Служебные данные сборки Spine |

Spine остаётся сборкой: BMAD и `bmad-build` читают именно его.

## Что проверяет скрипт

- Каждая функция относится к системе и хотя бы к одному процессу или требованию.
- У каждого объекта данных есть владелец, а у каждого хранилища есть объекты.
- Функция читает или пишет только объекты, которые дошли до её системы потоком или лежат в её хранилище.
- У потока между разными системами указана интеграция.
- Значения типов есть в `types.yaml`.
- Выход одного шага процесса является входом следующего или выходом всего процесса.

## Проба перед внедрением

1. Описать этими объектами «Вектор» и записать, сколько файлов и токенов потребовалось.
2. Заранее записать критерий: G01 на тех же трёх историях находит не меньше проблем, а объём пакета вырастает не больше чем вдвое.
3. Сравнить с текущим пакетом по 5 запусков на вариант.
4. Описать один иной тип системы, чтобы проверить, что объекты не подогнаны под «Вектор».

## Источники

- [TOGAF: Architecture Content, The Open Group](https://pubs.opengroup.org/togaf-standard/architecture-content/chap02.html)
- [ArchiMate 3.2, изменения по версиям, The Open Group](https://digital-portfolio.opengroup.org/archimate-specs/latest/99-appendices/05-changes-v3.html)
- [ArchiMate 3.2, перечень понятий, Bizzdesign](https://bizzdesign.com/wp-content/uploads/2023/06/2023-ArchiMate3.2-concepts.pdf)
- [SIPOC, TechTarget](https://www.techtarget.com/it-strategy/definition/SIPOC-suppliers-inputs-process-outputs-customers-diagram)
- [Structurizr DSL, справочник языка](https://docs.structurizr.com/dsl/language)
