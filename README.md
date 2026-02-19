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
- [Каталог Speckit Skills](#каталог-speckit-skills)
- [CI: drift-check](#ci-drift-check)
- [Обновления (админу)](#обновления-админу)
- [Опционально: Memory Bank](#опционально-memory-bank)
- [Опционально: Человекочитаемые спецификации](#опционально-человекочитаемые-спецификации)
- [Опционально: Skillpacks](#опционально-skillpacks)
- [Troubleshooting](#troubleshooting)

## Что это

Внутри два ключевых элемента:

- `bin/sdd-kit` (Python CLI): `bootstrap`, `sync`, `check`, `detect`, плюс управление skillpacks.
- `sddkit/_templates/*`: шаблоны, из которых `sync` генерирует managed-файлы в ваших проектах.

Отдельно поддерживается режим **Spec Kit** (GitHub `spec-kit`) как каноничный SDD пайплайн. В этом режиме `sdd-kit`:

- ставит `.specify/*` (скрипты/шаблоны Spec Kit) из pinned upstream
- генерирует команды `speckit-*` как Codex skills (например, `.codex/skills/speckit-plan/SKILL.md`)
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
  SYNC --> PROMPTS[".codex/skills/speckit-command-name/SKILL.md"]
  SYNC --> FRAG[".sddkit/fragments/AGENTS.manual.md"]

  DEV["Developer / agent"] --> SPK["$speckit-specify, $speckit-plan, $speckit-tasks, $speckit-implement"]
  SPK --> SPECIFY
  SPK --> SPECS["specs/###-feature/spec.md, plan.md, tasks.md"]

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

Команды `speckit-*` — это команды-скрипты (Codex skills), которые ведут вас по одному каноничному циклу:
`spec.md -> plan.md -> tasks.md -> implement`.

Артефакты фичи лежат в `specs/###-feature-name/`.

Схема:

```mermaid
flowchart TD
  START["Start"] --> SPECIFY["$speckit-specify"]
  SPECIFY --> SPEC["specs/###-.../spec.md"]

  SPEC --> AMBIG{"Ambiguity?"}
  AMBIG -->|yes| CLARIFY["$speckit-clarify"] --> SPEC

  AMBIG -->|no| PLAN["$speckit-plan"]
  PLAN --> PLAN_OUT["plan.md + artifacts + AGENTS.md"]
  PLAN_OUT --> TASKS["$speckit-tasks"]
  TASKS --> TASKS_MD["tasks.md"]

  TASKS_MD --> ANALYZE_OK{"Need analysis?"}
  ANALYZE_OK -->|yes| ANALYZE["$speckit-analyze (read-only)"] --> TASKS_MD
  ANALYZE_OK -->|no| IMPLEMENT["$speckit-implement"]
  IMPLEMENT --> CODE["Code + tests"]

  CODE --> DRIFT["sdd-kit check (drift gate)"]
  DRIFT --> PR["PR"]
```

### Как skills реально исполняются (runtime flow)

```mermaid
flowchart LR
  U["User runs $speckit-..."] --> S["Load .codex/skills/speckit-*/SKILL.md"]
  S --> C["Execution Contract"]
  C --> R["Run .specify/scripts/... first"]
  R --> O["Parse script output (often JSON)"]
  O --> A["Update specs/NNN-... artifacts"]
  A --> X["Return report / next step"]
```

Runtime rules (important):

- каждый `speckit-*` skill содержит `Execution Contract`
- если в skill есть `.specify/scripts/...`, сначала запускается скрипт, потом анализ/правки
- чтение исходников скриптов до первой попытки запуска не является корректным путем
- при ошибке запуска: сначала показать ошибку, потом уже разбирать скрипт

## Каталог Speckit Skills

Все команды запускаются как `$speckit-...` в Codex.

| Skill | Зачем | Что создает/обновляет | Когда запускать |
|---|---|---|---|
| `$speckit-specify` | Создать новую спецификацию фичи | `specs/NNN-.../spec.md`, ветка `NNN-...`, checklist | Старт новой фичи |
| `$speckit-clarify` | Снять неоднозначности в требованиях | `spec.md` (Clarifications + правки) | Перед plan, если есть пробелы |
| `$speckit-plan` | Построить техплан и артефакты дизайна | `plan.md`, `research.md`, `data-model.md`, `contracts/*`, `quickstart.md`, `AGENTS.md` | После готового `spec.md` |
| `$speckit-tasks` | Разложить работу на исполнимые задачи | `tasks.md` | После `plan.md` |
| `$speckit-implement` | Выполнить план по задачам | Код + тесты + отметки в `tasks.md` | После `tasks.md` |
| `$speckit-analyze` | Проверить согласованность spec/plan/tasks | Read-only report в ответе агента | Перед implement или перед PR |
| `$speckit-checklist` | Проверить качество требований по теме | `specs/.../checklists/*.md` | После specify/clarify/plan |
| `$speckit-constitution` | Заполнить/обновить принципы проекта | `.specify/memory/constitution.md` | Инициализация/обновление правил |
| `$speckit-taskstoissues` | Конвертировать задачи в GitHub issues | Issues в GitHub | Когда нужно внешний трекинг |
| `$speckit-planreview` | Мульти-модельное ревью spec/plan/tasks | `specs/.../reviews/planreview.md` | После plan, до tasks/implement |

Зависимости и внешние инструменты:

- базовый цикл (`specify/plan/tasks/implement`) работает на `.specify/scripts/*`
- для `$speckit-planreview` желательно установленный `opencode`
- для `$speckit-taskstoissues` нужен GitHub remote и рабочая интеграция GitHub MCP

#### `$speckit-specify <описание>`

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

#### `$speckit-plan`

Зачем: превратить `spec.md` в технический план и дизайн-артефакты.

Что делает:

- создаёт/обновляет `specs/.../plan.md`
- генерирует дизайн-артефакты в `specs/.../` (например `research.md`, `data-model.md`, `contracts/*`, `quickstart.md` — зависит от проекта)
- обновляет `AGENTS.md` через `update-agent-context` (overlay MANUAL блок при этом сохраняется)

Как использовать:

- запускать на feature-ветке (`001-...`) после готового `spec.md`
- если в требованиях есть неоднозначности — сначала `$speckit-clarify`

Скрипты без агента:

```bash
bash .specify/scripts/bash/setup-plan.sh
bash .specify/scripts/bash/update-agent-context.sh codex
```

#### `$speckit-tasks`

Зачем: получить исполнимый `tasks.md` (задачи с зависимостями и путями к файлам).

Что делает:

- создаёт/обновляет `specs/.../tasks.md` по шаблону
- раскладывает задачи по user stories, добавляет ID (T001...), пометки параллельности `[P]`

Как использовать:

- запускать после `$speckit-plan`
- если поменяли `plan.md` — перегенерировать `tasks.md` (это ожидаемо)

#### `$speckit-implement`

Зачем: выполнить `tasks.md` по шагам, не теряя связь со спеком/планом.

Что делает:

- читает `tasks.md`/`plan.md` (и опциональные артефакты)
- реализует задачи фазами, отмечает выполненные как `[X]` в `tasks.md`
- может остановиться, если requirements-checklists в `specs/.../checklists/` не закрыты

Как использовать:

- делать по 1 задаче за раз, часто запускать реальные проверки (тесты/линт/сборка)
- перед PR прогонять `sdd-kit check`

#### Дополнительные команды `speckit-*` (по ситуации)

- `$speckit-clarify`: если в `spec.md` есть неоднозначности; задаёт вопросы и дописывает ответы в `spec.md`.
- `$speckit-checklist`: создаёт чеклист качества требований в `specs/.../checklists/*.md` (это не тесты кода, это "unit tests" для спека).
- `$speckit-planreview`: мульти-модельное ревью `spec.md/plan.md/tasks.md` (advisory-only) и запись отчёта в `specs/.../reviews/planreview.md`. Рекомендуется после `$speckit-plan` и до `$speckit-tasks`/`$speckit-implement`. Требует установленный `opencode` (и опционально другие инструменты).
- `$speckit-analyze`: read-only анализ согласованности `spec.md`/`plan.md`/`tasks.md` (полезно перед implement).
- `$speckit-constitution`: создаёт/обновляет `.specify/memory/constitution.md` (принципы). В гибридном режиме не редактируйте `.specify/templates/*` и `.codex/skills/*` вручную: они managed и пинятся kit'ом.
- `$speckit-taskstoissues`: превращает задачи в GitHub issues (требует GitHub remote и настроенный GitHub MCP у агента).


### 2) Перед PR

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit check --project .
```

Если `check` упал на `DRIFT/MISSING`:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .
```

### 3) `AGENTS.md` в Spec Kit mode (как настраивать и обновлять)

`AGENTS.md` — это файл контекста/правил для агента: карта репозитория, команды, ограничения, договоренности по стилю/процессу.

В **Spec Kit mode** `AGENTS.md` создаёт/обновляет сам Spec Kit скриптом `update-agent-context` (обычно это происходит на шаге `$speckit-plan`).

Правила:

- Не редактируйте `AGENTS.md` напрямую: Spec Kit будет перегенерировать его.
- Для ваших организационных заметок используйте **MANUAL-блок**:
  - редактируйте `.sddkit/fragments/AGENTS.manual.md`
  - применяйте: `python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .`
  - `sdd-kit check` проверяет только соответствие MANUAL-блока вашему fragment'у (не весь файл).
- В новых установках `AGENTS.manual.md` автоматически создается с кросс-ссылками на:
  - `docs/SDD/README.md` (основной workflow)
  - `meta/memory_bank/*` (если Memory Bank используется)
  - PR/task update правила (`workflows/code_review.md`, `guides/task_updates.md`)
- Также в этом fragment по умолчанию есть краткие правила оформления PR:
  - base branch, title (Conventional Commits), обязательные разделы описания, ссылки на spec/work-item, pre-review проверки.
  - описание PR должно быть в структурированном Markdown (заголовки/списки/чеклисты), не «простыня» plain text.
  - запрещены видимые escape-переносы как текст (`\n`, `\r\n`, `\t`) в теле PR; нужны реальные переносы строк.

Если проект старый и в `.sddkit/fragments/AGENTS.manual.md` у вас еще короткий legacy-текст, `sdd-kit sync` обновит его на новый шаблон автоматически.
Если файл уже редактировали вручную, kit его не перезапишет.

Если нужно обновить `AGENTS.md` вручную (например, вы сильно поменяли структуру репозитория или команды):

```bash
bash .specify/scripts/bash/update-agent-context.sh codex
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

1. Обновить указатель submodule на нужный тег/коммит:

```bash
cd upstreams/spec-kit
git fetch --tags origin
git checkout <TAG_OR_SHA>
cd ../..
git add upstreams/spec-kit
git commit -m "chore: bump spec-kit upstream to <TAG_OR_SHA>"
```

2. Прогнать смоук-тесты (они проверяют, что install + drift-check + основные скрипты работают):

```bash
python3 scripts/smoke_speckit.py
python3 scripts/smoke_airis.py
```

3. Бампнуть версию `sdd-workflow-kit`, поставить тег и запушить (см. ниже).

### Синхронизация с upstream (если ваш проект — fork)

Если проект является форком, делайте синхронизацию с upstream отдельным процессом, чтобы минимизировать конфликты с managed-файлами.

1. Один раз добавить remote `upstream`:

```bash
git remote add upstream <UPSTREAM_GIT_URL>
git fetch upstream --tags
```

2. Создать ветку синхронизации:

```bash
git checkout <integration-branch>
git pull
git checkout -b chore/upstream-sync-YYYY-MM-DD
```

3. Интегрировать upstream (выберите политику команды):

- merge:

```bash
git merge upstream/<branch>
```

- rebase:

```bash
git rebase upstream/<branch>
```

4. Разрулить конфликты, прогнать проверки проекта, затем обязательно:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .
python3 .tooling/sdd-workflow-kit/bin/sdd-kit check --project .
```

## Опционально: Memory Bank

Memory Bank это отдельный слой (`meta/memory_bank/*`). Он не конфликтует со Spec Kit.

**Работает ли он автоматически?** Нет. Kit устанавливает и обновляет managed-шаблоны при `sdd-kit sync`, но содержание Memory Bank вы (или агент) поддерживаете вручную. Никаких фоновых демонов/хуков по умолчанию нет.

Где лежит (по умолчанию): `meta/memory_bank/`.

Как пользоваться (минимум):

1. Перед любой задачей откройте `meta/memory_bank/README.md` и пройдите Mandatory Reading Sequence.
2. Если добавили зависимость или поменяли архитектуру, обновите `meta/memory_bank/tech_stack.md` и/или соответствующий `meta/memory_bank/patterns/*`.
3. Для трекинга работы (чтобы избежать конфликтов):
   - на feature-ветках не правьте `meta/memory_bank/current_tasks.md`
   - пишите обновления в `meta/memory_bank/branch_updates/*.md`
   - на integration ветке переносите обновления в `current_tasks.md` и удаляйте обработанные `branch_updates/*`

Хелпер: `meta/tools/merge_task_updates.sh` подскажет, какие `branch_updates/*.md` ждут обработки.

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

## Опционально: Человекочитаемые спецификации

- В Spec Kit mode спеки/планы/задачи уже человекочитаемые: `specs/###-.../{spec,plan,tasks}.md` (Markdown).
- Если вы используете JSON SDD (опционально, `meta/sdd/specs/*.json`), то для людей можно генерировать Markdown рендером:

```bash
meta/tools/sdd render --help
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

Установить **Spec Kit команды** (`speckit-*`) как Codex skills:

```bash
# В проект (./.codex/skills/speckit-*)
python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --pack speckit --to project

# Глобально (~/.codex/skills/speckit-*) — если текущая сессия Codex не читает project-local skills
python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --pack speckit --to global
```

## Troubleshooting

### `UNMANAGED ... (safe_mode)`

Это значит: файл уже существует, но он не помечен как managed. В safe mode kit его не трогает.

Варианты:

- переименовать/удалить файл и снова `sync`
- выключить управление этим файлом в `[manage]`
- для старых глобальных `~/.codex/skills/speckit-*` (не managed) удалите эти каталоги и повторите:
  `python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --pack speckit --to global`

### Не видно `speckit-*` в `/skills`

Проверьте, откуда текущая сессия Codex читает skills (project-local или global) и установите туда:

```bash
# project-local
python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --pack speckit --to project

# global
python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --pack speckit --to global
```

Если раньше ставились legacy навыки вручную, удалите старые `~/.codex/skills/speckit-*` и установите заново.
После установки откройте новый чат (или перезапустите Codex), затем проверьте `/skills`.

### В CI не виден `upstreams/spec-kit`

Почти всегда причина: забыли `submodules: recursive` в `actions/checkout`.

### Spec Kit ругается на ветку

Spec Kit ожидает ветки вида `001-feature-name`. Создавайте фичи через `$speckit-specify`.

## Требования

- Git (submodule)
- Python 3.11+

## Лицензии

- Upstream `github/spec-kit` (MIT) вендорится как submodule и устанавливается в проекты как managed файлы.
- См. `THIRD_PARTY_NOTICES.md`.
