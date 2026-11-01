# Объекты YAML для описания архитектуры

Статус: **черновик, в код не внедрён**. Сначала нужна проба на примере «Вектор» и сравнение с текущими единицами.

Основа, заданная владельцем: **TOGAF, C4 и ITIL**. Источниками были страницы Open Group, обзоры и материалы вендоров, а не полный текст стандартов. Названия каталогов TOGAF и определения ITIL нужно сверить с первоисточниками до внедрения.

## Что не так сейчас

Текущие единицы повторяют разделы документа BMAD, а не устройство системы. В них нет бизнес-процессов, функций, объектов данных, потоков и сервисов. Часть файлов к архитектуре не относится: это служебные данные сборки и правила кода.

## Что даёт каждая основа

Три нотации отвечают на разные вопросы и не конкурируют.

| Основа | Вопрос | Что берём | Что не берём |
| --- | --- | --- | --- |
| TOGAF | Из каких слоёв состоит архитектура | Слои: бизнес, данные, приложения, технологии. Разделение логического и физического. Право убирать лишние сущности из метамодели | Управление архитектурой предприятия, ADM |
| C4 | Как глубоко описана система | Вложенность: система, контейнер, компонент. Уровни C1, C2, C3 | Уровень кода C4 и саму нотацию как метамодель |
| ITIL | Что обслуживается и что зависит от чего | Сервис с обязательствами. Единица конфигурации с владельцем и жизненным циклом. Связи для анализа влияния. Вход и выход процесса | Инциденты, проблемы и изменения: это эксплуатация, а не описание архитектуры |

## Общие поля

Из ITIL взято правило: объект ведётся, только если его изменение или отказ влияет на сервис. Поэтому у каждого объекта есть общая часть единицы конфигурации.

```yaml
id: work-item
title: Work Item
owner: команда-ядра
lifecycle: active   # planned | active | deprecated | retired
criticality: high   # low | medium | high
```

## Предлагаемый список

| Слой TOGAF | Объект | Уровень C4 | Файл | Что описывает | Свои поля |
| --- | --- | --- | --- | --- | --- |
| Бизнес | Участник | C1 | `actors/<id>.yaml` | Роль или внешняя организация | `kind`, `goals` |
| Бизнес | Процесс | — | `processes/<id>.yaml` | Бизнес-процесс | `trigger`, `inputs`, `steps`, `outputs`, `actors`, `functions` |
| Бизнес и приложения | Сервис | — | `services/<id>.yaml` | Что потребитель получает и на каких условиях | `consumers`, `provider`, `functions`, `objectives` |
| Приложения | Система | C1 | `systems/<id>.yaml` | Своя или внешняя система | `kind`, `vendor` |
| Приложения | Функция | — | `functions/<id>.yaml` | Что система делает для процесса | `system`, `reqs`, `reads`, `writes` |
| Приложения | Компонент | C2 | `components/<id>.yaml` | Контейнер внутри системы | `system`, `tech`, `functions` |
| Приложения | Блок | C3 | `blocks/<компонент>/<id>.yaml` | Часть компонента | `functions`, `on_failure` |
| Данные | Объект данных | — | `data/<id>.yaml` | Логическая сущность | `class`, `sensitivity`, `states`, `attributes` |
| Данные | Хранилище | C2 | `stores/<id>.yaml` | Физическое размещение | `objects`, `retention`, `backup` |
| Связи | Поток данных | C1–C3 | `flows/<id>.yaml` | Что, откуда и куда движется | `from`, `to`, `objects`, `trigger`, `flow_type`, `volume`, `over` |
| Связи | Интеграция | C1–C2 | `integrations/<id>.yaml` | Как устроен канал | `from`, `to`, `integration_type`, `protocol`, `auth`, `timeout`, `retry`, `idempotent` |
| Технологии | Узел | — | `nodes/<id>.yaml` | Где запущены компоненты | `environment`, `runs`, `tech` |
| Общее | Типы | — | `types.yaml` | Допустимые значения | Словари ниже |

Два различия, на которых держится список:

- **Поток и интеграция.** Поток говорит, что движется и зачем, интеграция говорит, по какому каналу. Один канал несёт много потоков.
- **Сервис и функция.** Функция говорит, что система умеет, сервис говорит, что и на каких условиях получает потребитель. Обязательства сервиса связаны со сценариями качества.

Простые связи остаются полями: `system`, `reads`, `writes`, `runs`. Отдельный объект нужен только связи со своими атрибутами.

## Как объекты дают каталоги TOGAF

| Каталог или матрица TOGAF | Откуда берётся |
| --- | --- |
| Каталог приложений | `systems/`, `components/` |
| Каталог интерфейсов | `integrations/` |
| Каталог объектов данных | `data/` |
| Матрица приложения и данные | `functions/*.reads`, `functions/*.writes` |
| Матрица процессы и приложения | `processes/*.functions`, `functions/*.system` |
| Схема обмена приложений | `flows/`, `integrations/` |

Вручную эти таблицы не ведутся: они собираются скриптом и подходят для Docmost.

## Словари типов

```yaml
integration_type: [sync-api, async-queue, webhook, event-stream, file, shared-db, ui]
flow_type: [command, query, event, replication, batch]
data_class: [reference, master, transactional, event, derived]
sensitivity: [public, internal, personal, secret]
system_kind: [own, external, vendor]
```

Значения предварительные. Новое значение вносится в словарь и проверяется скриптом.

## Пример на «Векторе»

```yaml
# processes/intake.yaml
id: intake
title: Приём заявки
owner: тимлид поддержки
lifecycle: active
criticality: medium
trigger: поступил Request
inputs: [request]
steps: [принять заявку, найти дубли, превратить в работу]
outputs: [user-story]
actors: [тимлид-поддержки]
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

Поля «не задано» показывают пробелы примера. Примеры показывают форму и не утверждены как архитектура «Вектора».

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
- У каждого объекта есть владелец и состояние жизненного цикла.
- Функция читает или пишет только объекты, которые дошли до её системы потоком или лежат в её хранилище.
- У потока между разными системами указана интеграция.
- Значения типов есть в `types.yaml`.
- Выход шага процесса является входом следующего шага или выходом всего процесса.
- У сервиса есть функции и обязательства, обязательство связано со сценарием качества.
- По связям строится анализ влияния: что затронет отказ интеграции или хранилища.

## Проба перед внедрением

1. Описать этими объектами «Вектор» и записать, сколько файлов и токенов потребовалось.
2. Заранее записать критерий: G01 на тех же трёх историях находит не меньше проблем, а объём пакета вырастает не больше чем вдвое.
3. Сравнить с текущим пакетом по 5 запусков на вариант.
4. Описать систему другого типа, чтобы проверить, что объекты не подогнаны под «Вектор».

## Источники

- [TOGAF: Architecture Content, The Open Group](https://pubs.opengroup.org/togaf-standard/architecture-content/chap02.html)
- [TOGAF: обзор метамодели, Ardoq](https://help.ardoq.com/en/articles/534168-frameworks-resources-togaf-v9-2-architecture-content-metamodel)
- [C4: элементы и вложенность в Structurizr DSL](https://docs.structurizr.com/dsl/language)
- [ITIL: единица конфигурации и CMDB, Device42](https://www.device42.com/cmdb-best-practices/itil-cmdb/)
- [ITIL 4: где находится CMDB, Cloudaware](https://cloudaware.com/blog/itil-cmdb/)
- [Определение процессов ITIL через SIPOC, Global Knowledge](https://www.globalknowledge.com/ca-en/resources/resource-library/white-paper/using-sipoc-to-define-itil-processes/)
