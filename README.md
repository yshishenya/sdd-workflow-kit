# sdd-workflow-kit

[![smoke-speckit](https://github.com/yshishenya/sdd-workflow-kit/actions/workflows/smoke-speckit.yml/badge.svg)](https://github.com/yshishenya/sdd-workflow-kit/actions/workflows/smoke-speckit.yml)
[![release](https://img.shields.io/github/v/release/yshishenya/sdd-workflow-kit)](https://github.com/yshishenya/sdd-workflow-kit/releases)
[![python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

`sdd-workflow-kit` подключается к любому репозиторию как `git submodule` и дает CLI `sdd-kit`.

CLI безопасно и идемпотентно синхронизирует в проект «управляемые» файлы (шаблоны/скрипты/доки/CI), чтобы ваш процесс разработки был:

- повторяемым между репозиториями
- обновляемым через пин по git тегу/SHA
- проверяемым в CI (drift-check)

## Содержание

- [Что это](#что-это)
- [Зачем](#зачем)
- [Как это работает](#как-это-работает)
- [Установка в проект (админу)](#установка-в-проект-админу)
- [Как пользоваться (разработчику)](#как-пользоваться-разработчику)
- [CI: drift-check](#ci-drift-check)
- [Обновления (админу)](#обновления-админу)
- [Опционально: Memory Bank](#опционально-memory-bank)
- [Опционально: Skillpacks](#опционально-skillpacks)
- [Troubleshooting](#troubleshooting)

## Что это

Внутри два ключевых элемента:

- `bin/sdd-kit` (Python CLI): `bootstrap`, `sync`, `check`, `detect`, плюс управление skillpacks.
- `sddkit/_templates/*`: шаблоны, из которых `sync` генерирует managed-файлы в ваших проектах.

Отдельно поддерживается режим **Spec Kit** (GitHub `spec-kit`) как каноничный SDD пайплайн. В этом режиме `sdd-kit`:

- ставит `.specify/*` (скрипты/шаблоны Spec Kit) из pinned upstream
- генерирует команды агента `speckit.*` (например, для Codex: `.codex/prompts/speckit.plan.md`)
- проверяет дрейф инфраструктуры (а не ваших фичевых артефактов)

## Зачем

Проблема: хороший процесс (SDD, инструкции агенту, CI-гейты, шаблоны доков) сложно «разносить» по многим репозиториям.

Решение: один репозиторий-kit как источник правды + submodule в каждом проекте.

- Подключили submodule.
- Запустили `bootstrap` один раз.
- Дальше `sync` обновляет только managed-файлы.
- `check` в CI ловит дрейф.

Важно: по умолчанию включен **safe mode**: kit не перезаписывает неуправляемые (чужие) файлы.

## Как это работает

Коротко:

- `.sddkit/config.toml` в проекте определяет, чем управляет kit.
- `sdd-kit sync` вычисляет «ожидаемое состояние» и приводит managed-файлы к нему.
- `sdd-kit check` сравнивает факт с ожиданием и падает на `DRIFT/MISSING/UNMANAGED`.
- В **Spec Kit mode** фичевые артефакты (`specs/**`) создаются самим Spec Kit и **не** drift-check’аются.

```mermaid
flowchart LR
  KIT["sdd-workflow-kit (git submodule)"] --> SYNC["sdd-kit sync"]
  SYNC --> SPECIFY[".specify/* (Spec Kit scripts + templates)"]
  SYNC --> PROMPTS[".codex/prompts/speckit.*.md"]
  SYNC --> FRAG[".sddkit/fragments/AGENTS.manual.md"]

  DEV["Developer / agent"] --> SPK["speckit.specify/plan/tasks/implement"]
  SPK --> SPECIFY
  SPK --> SPECS["specs/###-feature/{spec,plan,tasks}.md"]

  SPECIFY --> AG["AGENTS.md (Spec Kit updater)"]
  FRAG --> AG

  CHECK["sdd-kit check (CI/local gate)"] --> SPECIFY
  CHECK --> PROMPTS
  CHECK --> AG
```

Где смотреть подробную инструкцию внутри конкретного проекта:

- `docs/SDD/README.md` (managed-документ, обновляется через `sdd-kit sync`)

## Установка в проект (админу)

### 1) Подключить kit как submodule

Рекомендуемый путь:

```bash
git submodule add git@github.com:yshishenya/sdd-workflow-kit.git .tooling/sdd-workflow-kit
```

### 2) Инициализировать submodules

```bash
git submodule update --init --recursive
```

### 3) Bootstrap (создать конфиг и сразу синхронизировать managed-файлы)

SDD через Spec Kit (рекомендуется для новых фич):

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project . --profile speckit --locale ru
```

Memory Bank + `meta/*` scaffolding (Airis-профиль):

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project . --profile airis --locale ru
```

Нейтральный профиль (без лишнего):

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project . --profile generic --locale ru
```

`bootstrap`:

- создаст `.sddkit/config.toml` (если его еще нет)
- запустит `sync`

### 4) Закоммитить изменения

После `bootstrap` обычно появляются новые managed-файлы (доки/скрипты/CI). Закоммитьте их вместе с добавлением submodule.

## Как пользоваться (разработчику)

### 0) После `git clone`

Если репозиторий использует submodules:

```bash
git submodule update --init --recursive
```

### 1) SDD цикл (Spec Kit)

Команды `speckit.*` — это агентские команды (prompts), которые ведут вас по одному каноничному циклу:
`spec.md -> plan.md -> tasks.md -> implement`.

Артефакты фичи лежат в `specs/###-feature-name/`.

#### `speckit.specify <описание>`

Зачем: стартовать новую фичу и получить качественный `spec.md` (что/зачем), без реализации.

Как использовать:

- запускать из корня репозитория
- передавать 1-3 предложения описания фичи (без "как")

Что делает:

- создаёт и checkout'ит ветку вида `001-short-name`
- создаёт папку `specs/001-short-name/`
- пишет `specs/001-short-name/spec.md` по шаблону
- часто создаёт `specs/001-short-name/checklists/requirements.md` для самопроверки качества спека

Скрипт без агента (mac/linux):

```bash
bash .specify/scripts/bash/create-new-feature.sh "Add ..."
```

#### `speckit.plan`

Зачем: превратить `spec.md` в технический план и дизайн-артефакты.

Что делает:

- создаёт/обновляет `specs/.../plan.md`
- генерирует дизайн-артефакты в `specs/.../` (например `research.md`, `data-model.md`, `contracts/*`, `quickstart.md` — зависит от проекта)
- обновляет `AGENTS.md` через `update-agent-context` (overlay MANUAL блок при этом сохраняется)

Как использовать:

- запускать на feature-ветке (`001-...`) после готового `spec.md`
- если в требованиях есть неоднозначности — сначала `speckit.clarify`

Скрипты без агента:

```bash
bash .specify/scripts/bash/setup-plan.sh
bash .specify/scripts/bash/update-agent-context.sh codex
```

#### `speckit.tasks`

Зачем: получить исполнимый `tasks.md` (задачи с зависимостями и путями к файлам).

Что делает:

- создаёт/обновляет `specs/.../tasks.md` по шаблону
- раскладывает задачи по user stories, добавляет ID (T001...), пометки параллельности `[P]`

Как использовать:

- запускать после `speckit.plan`
- если поменяли `plan.md` — перегенерировать `tasks.md` (это ожидаемо)

#### `speckit.implement`

Зачем: выполнить `tasks.md` по шагам, не теряя связь со спеком/планом.

Что делает:

- читает `tasks.md`/`plan.md` (и опциональные артефакты)
- реализует задачи фазами, отмечает выполненные как `[X]` в `tasks.md`
- может остановиться, если requirements-checklists в `specs/.../checklists/` не закрыты

Как использовать:

- делать по 1 задаче за раз, часто запускать реальные проверки (тесты/линт/сборка)
- перед PR прогонять `sdd-kit check`

#### Дополнительные команды `speckit.*` (по ситуации)

- `speckit.clarify`: если в `spec.md` есть неоднозначности; задаёт вопросы и дописывает ответы в `spec.md`.
- `speckit.checklist`: создаёт чеклист качества требований в `specs/.../checklists/*.md` (это не тесты кода, это "unit tests" для спека).
- `speckit.analyze`: read-only анализ согласованности `spec.md`/`plan.md`/`tasks.md` (полезно перед implement).
- `speckit.constitution`: создаёт/обновляет `.specify/memory/constitution.md` (принципы). В гибридном режиме не редактируйте `.specify/templates/*` и `.codex/prompts/*` вручную: они managed и пинятся kit'ом.
- `speckit.taskstoissues`: превращает задачи в GitHub issues (требует GitHub remote и настроенный GitHub MCP у агента).


### 2) Перед PR

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit check --project .
```

Если `check` упал на `DRIFT/MISSING`:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .
```

## CI: drift-check

Есть два подхода.

- Подход A (рекомендуется, обязателен для `manage.speckit=true`): запускать `sdd-kit check` прямо из submodule в проекте.
- Подход B: использовать composite action из этого репо (удобно, но не подходит для Spec Kit mode).

Важно для Spec Kit mode: checkout должен быть с `submodules: recursive`.

## Обновления (админу)

### Обновить `sdd-workflow-kit` в проекте

1. Обновите указатель submodule на новый тег:

```bash
cd .tooling/sdd-workflow-kit
git fetch --tags origin
git checkout vX.Y.Z
cd ../..
```

2. Подтяните nested submodules:

```bash
git submodule update --init --recursive
```

3. Пересинхронизируйте managed-файлы и проверьте дрейф:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .
python3 .tooling/sdd-workflow-kit/bin/sdd-kit check --project .
```

4. Закоммитьте изменения (обновление submodule + обновленные managed-файлы).

### Обновить upstream Spec Kit (только для мейнтейнеров этого kit)

Upstream Spec Kit живет как submodule: `upstreams/spec-kit` (пин по SHA).

Процедура:

1. Обновить указатель submodule на нужный тег/коммит.
2. Прогнать `python3 scripts/smoke_speckit.py`.
3. Выпустить новую версию kit (тег/релиз).

## Опционально: Memory Bank

Memory Bank это отдельный слой (`meta/memory_bank/*`). Он не конфликтует со Spec Kit.

Включается флагами в `.sddkit/config.toml`:

```toml
[manage]
memory_bank = true
meta_tools = true
meta_sdd = true
```

Затем:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .
```

## Опционально: Skillpacks

Перенести локальные Codex skills в kit (чтобы kit был самодостаточным):

```bash
python3 bin/sdd-kit import-codex-skills --from "$HOME/.codex/skills" --pack codex
```

Установить skills в проект:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --to project
```

## Troubleshooting

### `UNMANAGED ... (safe_mode)`

Это значит: файл уже существует, но он не помечен как managed. В safe mode kit его не трогает.

Варианты:

- переименовать/удалить файл и снова `sync`
- выключить управление этим файлом в `[manage]`

### В CI не виден `upstreams/spec-kit`

Почти всегда причина: забыли `submodules: recursive` в `actions/checkout`.

### Spec Kit ругается на ветку

Spec Kit ожидает ветки вида `001-feature-name`. Создавайте фичи через `speckit.specify`.

## Требования

- Git (submodule)
- Python 3.11+

## Лицензии

- Upstream `github/spec-kit` (MIT) вендорится как submodule и устанавливается в проекты как managed файлы.
- См. `THIRD_PARTY_NOTICES.md`.
