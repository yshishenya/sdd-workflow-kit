# sdd-workflow-kit

Универсальный kit для упаковки и повторного использования вашего процесса разработки (workflow), Spec-Driven Development (SDD), инструкций для агента (например, `AGENTS.md`) и наборов “скиллов” в любом репозитории.

Подключается в проект как `git submodule`, после чего одной командой безопасно (без перетирания ваших файлов) добавляет и держит в синхронизации “управляемые” файлы: инструкции, scaffolding, wrapper-скрипты и CI-проверку дрейфа.

---

## Зачем это нужно

Типичная проблема: у вас есть хороший процесс (воркфлоу, SDD, стандарты кодинга, туллинг, agent-настройки), но каждый новый репозиторий приходится настраивать вручную, а изменения в процессе тяжело “разнести” по всем проектам.

Этот репозиторий решает задачу так:

- Есть один “источник правды” (этот kit).
- Каждый проект подключает kit (как submodule) и синхронизирует управляемые файлы.
- Управляемые файлы обновляются идемпотентно и безопасно.
- CI может проверять, что проект не “уплыл” от стандарта.

---

## Что именно умеет kit

- Генерировать и обновлять `AGENTS.md` (инструкции агенту) из шаблона.
- Устанавливать и держать в синхронизации Spec Kit (профиль `speckit`): `.specify/*` + `speckit.*` prompt-файлы для агента (Codex/Claude), с drift-check и без конфликта за владение `AGENTS.md`.
- (Опционально) создавать и поддерживать “Memory Bank” (`meta/memory_bank/*`) как единый навигационный слой по процессам/стеку/паттернам.
- (Опционально) добавлять `meta/sdd/*` и wrapper-скрипты в `meta/tools/*` (для SDD и служебных утилит).
- (Опционально) добавлять CI workflow для проверки дрейфа или использовать готовый composite GitHub Action.
- Импортировать локальные Codex skills из `~/.codex/skills` в `skillpacks/*` и устанавливать их в проекты (или в глобальный CODEX_HOME).

---

## Гарантия “безопасности” (не ломает ваш проект)

Kit работает в режиме “управляемых файлов”.

Правила:

- Kit пишет и обновляет только файлы, которые сам пометил как управляемые.
- Если файл уже существует и он не управляемый, kit его не трогает и пропускает.
- Любые изменения воспроизводимы: `sync` можно запускать сколько угодно раз.

Маркер управления выглядит так и находится в начале файла:

```text
managed-by: sdd-workflow-kit
```

---

## Быстрый старт (внутри целевого проекта)

### 1) Подключить kit как submodule

Рекомендуемый путь в репозитории:

```bash
git submodule add git@github.com:yshishenya/sdd-workflow-kit.git .tooling/sdd-workflow-kit
```

### 2) Bootstrap (создать конфиг и сгенерировать управляемые файлы)

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project . --locale ru
```

Если вы создаете новый репозиторий и хотите сразу Memory Bank + `meta/*` scaffolding (Airis-профиль):

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project . --locale ru --profile airis
```

Если вы хотите использовать GitHub Spec Kit как **каноничный SDD pipeline** (спеки в `specs/###-feature/*`, `.specify/*`, агент-команды `speckit.*`):

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project . --profile speckit --locale en
```

В этом режиме kit:

- Не создает legacy layout `specs/{pending,active,completed}`.
- Не “владеет” файлом `AGENTS.md` целиком (Spec Kit обновляет его своим скриптом). Kit управляет только MANUAL-блоком (см. ниже).
- Устанавливает `.specify/*` и генерирует `speckit.*.md` prompt-файлы в `.codex/prompts` (и/или `.claude/commands`).

### 3) Дальше поддерживать синхронизацию

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .
```

### 4) Проверка дрейфа (локально и в CI)

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit check --project .
```

---

## Команды CLI

CLI доступен как скрипт:

- Внутри проекта (через submodule): `.tooling/sdd-workflow-kit/bin/sdd-kit`
- Внутри самого kit: `bin/sdd-kit`

Команды:

| Команда | Назначение |
| --- | --- |
| `detect` | Определить характеристики проекта (языки, package managers) |
| `bootstrap` | Создать `.sddkit/config.toml` (если его нет) и выполнить `sync` |
| `sync` | Синхронизировать управляемые файлы (безопасно, идемпотентно) |
| `check` | Проверить, что управляемые файлы актуальны (удобно для CI) |
| `import-codex-skills` | Импортировать skills из CODEX_HOME в `skillpacks/*` этого репо |
| `install-skills` | Установить skillpack в проект или глобально |

Подсказка по флагам:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit --help
```

---

## Конфигурация проекта: `.sddkit/config.toml`

`bootstrap` создаст конфиг автоматически. Дальше вы настраиваете, что именно kit должен “вести”.

Пример (минимально важные части):

```toml
[sddkit]
locale = "ru"
safe_mode = true
profile = "generic"

[manage]
agents_md = true
github_workflow = true
memory_bank = false
meta_tools = false
meta_sdd = false
docs_scaffold = false
specs_scaffold = false
speckit = false
codex_scaffold = false

[github]
kit_path = ".tooling/sdd-workflow-kit"
config = ".sddkit/config.toml"
fail_on_missing_config = false
```

Важные принципы:

- `safe_mode = true` означает “не перезаписывать чужие (неуправляемые) файлы”.
- Если у вас уже есть свой `AGENTS.md`, вы можете отключить его управление: `agents_md = false`.
- Если вы включили Spec Kit (`speckit = true`), рекомендуется отключить `agents_md` и `specs_scaffold` (профиль `speckit` делает это автоматически при bootstrap).

### Spec Kit-опции

```toml
[manage]
speckit = true

[speckit]
agent = "codex"        # codex|claude|all
script_variant = "sh"  # sh|ps
```

Что делает `manage.speckit=true`:

- Копирует `.specify/templates/*` (из `github/spec-kit`, кроме `templates/commands/*` и `vscode-settings.json`)
- Копирует `.specify/scripts/bash/*` (или `powershell/*` при `script_variant="ps"`)
- Создает `.specify/memory/constitution.md` только если файла нет (не дрейф-чекается по содержимому)
- Генерирует prompt-файлы команд: `.codex/prompts/speckit.*.md` и/или `.claude/commands/speckit.*.md`
- Создает `.specify/THIRD_PARTY_NOTICES.md` (MIT license + pin на версию upstream)

---

## Как добавлять локальные инструкции агенту, не трогая управляемый файл

Есть два режима:

- Если `AGENTS.md` управляется kit-ом (`manage.agents_md=true`), но вам нужно добавить проектные детали, используйте фрагмент:

```text
.sddkit/fragments/AGENTS.append.md
```

Дальше выполните:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .
```

### Spec Kit mode: overlay только в MANUAL-блок

В Spec Kit режиме (`manage.speckit=true`) kit **не** генерирует `AGENTS.md` целиком. Spec Kit обновляет его через `update-agent-context.*`.

Kit управляет только блоком:

```text
<!-- MANUAL ADDITIONS START -->
...
<!-- MANUAL ADDITIONS END -->
```

Источник правды для этого блока:

```text
.sddkit/fragments/AGENTS.manual.md
```

`sync` патчит только этот блок (если `AGENTS.md` уже существует). `check` проверяет только этот блок, а не весь файл.

---

## Профили (адаптация под тип проекта)

При создании нового конфига `bootstrap` может использовать пресет:

- `generic`: максимально нейтральный профиль.
- `airis`: профиль с Memory Bank и `meta/*` scaffolding под Airis-подход.
- `speckit`: профиль, где **ядро SDD** идет через GitHub Spec Kit (`.specify/*`, `speckit.*` prompts), а kit остается overlay (skills/scaffolds/CI). Не управляет `AGENTS.md` целиком и не создает legacy `specs/{pending,active,completed}`.
- `auto`: выбрать профиль автоматически (используется по умолчанию при bootstrap).

Важно: `--profile` влияет только на первичное создание конфига. Дальше все контролируется значениями в `.sddkit/config.toml`.

---

## Локализация шаблонов

Поддерживаются локали `en` и `ru`.

Выбор:

- Через `.sddkit/config.toml`: `[sddkit] locale = "ru"`
- На один запуск: `--locale ru`

Шаблоны лежат в `sddkit/_templates/<locale>/...`.

---

## Skillpacks: перенос и установка “скиллов”

### 1) Снять “снимок” ваших локальных Codex skills в этот репозиторий

```bash
python3 bin/sdd-kit import-codex-skills --from "$HOME/.codex/skills" --pack codex
```

После этого skillpack будет жить в `skillpacks/codex/skills/*`, а kit станет самодостаточным.

### 2) Установить skillpack в проект

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --to project
```

### 3) Установить skillpack глобально (в CODEX_HOME)

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --to global
```

Рекомендуемая практика:

- Держать skillpacks в этом репо как “официальный набор” для организации.
- Устанавливать “project” режимом в репозитории, где нужно зафиксировать версию skills рядом с кодом.

---

## CI: проверка дрейфа в GitHub Actions

Есть два подхода.

### Подход A: коммитить сгенерированный workflow в проект

Kit может создать `.github/workflows/sdd-kit-check.yml` (если включено `github_workflow = true`).

Логика простая: в CI выполняется `sdd-kit check`.

### Подход B: использовать готовый composite action из этого репозитория

Пример workflow:

```yaml
name: sdd-kit-check
on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: yshishenya/sdd-workflow-kit@main
        with:
          project_root: "."
          config: ".sddkit/config.toml"
          fail_on_missing_config: "false"
```

Best practice:

- Пинить action на тег или SHA, а не на `main`, чтобы сборки были воспроизводимыми.

---

## Обновление kit в проекте (рекомендованный процесс)

1. Обновить submodule на новую версию (git pull внутри submodule или обновление указателя).
2. Выполнить `sync`.
3. Закоммитить изменения управляемых файлов вместе с обновлением submodule.

### Обновление upstream Spec Kit (внутри этого репозитория)

Spec Kit vendored как submodule: `upstreams/spec-kit` (пинится по SHA).

Процедура обновления:

1. Обновить указатель submodule на нужный тег/коммит Spec Kit.
2. Прогнать smoke: `python3 scripts/smoke_speckit.py`
3. Обновить `THIRD_PARTY_NOTICES.md` (pin/tag/SHA) при необходимости.

---

## Как расширять kit под вашу организацию

Схема расширения:

- Добавляйте/правьте шаблоны в `sddkit/_templates/`.
- Добавляйте новые scaffolds и включайте их флагами в `[manage]`.
- При необходимости добавляйте новый профиль и его дефолты в коде (профилизация нужна только для bootstrap).

Важный принцип: любые изменения должны сохранять “safe mode” и не перетирать неуправляемые файлы.

---

## LLM-подсказка для адаптации под произвольный проект

Готовый промпт для LLM лежит в `LLM_ADAPTATION_PROMPT.md`.

Он удобен для сценария:

- “Вот репозиторий, вот его стек и ограничения, вот вывод `sdd-kit detect`”
- “Подбери `config.toml` и минимальный набор scaffolds, не ломая существующее”

---

## Требования

- Git (для submodule)
- Python 3.11+ (для запуска CLI)

---

## FAQ

### Kit пропускает файл, который я хотел бы обновлять

Скорее всего файл уже существует и не помечен как управляемый. По правилам безопасности kit не будет его трогать.

Варианты:

- Перенесите содержимое вручную в “управляемый” файл и удалите/переименуйте старый.
- Отключите управление этим файлом через `[manage]`.

### Как посмотреть план изменений, не записывая файлы

Используйте dry-run:

```bash
python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project . --dry-run
```

---

## Contributing

Если вы развиваете kit внутри команды:

- Держите изменения максимально аддитивными (новые шаблоны/скеффолды вместо правки поведения).
- Проверяйте, что `sync` идемпотентен и безопасен.
- Перед мерджем прогоняйте `sdd-kit check` на примерах проектов.
