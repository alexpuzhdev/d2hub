# Dota 2 Timings HUD (D2Hub)

## 1) Что это за проект
HUD-помощник для Dota 2: показывает тайминги, напоминания, окна риска и подсказки по сборке поверх игры. Работает из системного трея, автоматически определяет запущенную Dota 2.

**Важно:**
- HUD использует **официальный Game State Integration (GSI) от Valve**.
- HUD **не вмешивается в игровой процесс** и не изменяет файлы игры.
- Это **не чит** — отображает только заранее заданные тайминги и публичную информацию.

## 2) Системные требования
- **Windows 10/11**
- Установленная **Dota 2**
- **Python 3.10+** (для запуска из исходников) или готовый **D2Hub.exe**
- Права администратора **не требуются**

## 3) Установка из исходников

### Шаг 1. Установить Python
1. Скачайте Python 3.10+ с https://www.python.org/downloads/
2. При установке **обязательно отметьте** "Add Python to PATH"
3. Проверьте:
```cmd
python --version
```

### Шаг 2. Скачать проект
```cmd
git clone https://github.com/alexpuzhdev/d2hub.git
cd d2hub
```

Или скачайте ZIP-архив с GitHub и распакуйте, например в `C:\Games\d2hub`.

### Шаг 3. Установить зависимости (Poetry — рекомендуется)
```cmd
pip install poetry
poetry install
```

Poetry создаст виртуальное окружение и установит все зависимости из `pyproject.toml` автоматически.

### Шаг 3 (альтернатива). Установить без Poetry
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 4. Проверить установку
```cmd
poetry run pytest tests/ -v
```

Или без poetry:
```cmd
.venv\Scripts\activate
python -m pytest tests/ -v
```

## 4) Настройка Dota 2 (GSI)

### Автоматическая настройка (рекомендуется)
1. Запустите D2Hub (см. раздел 5)
2. Откройте **настройки** (правый клик по иконке в трее → "Открыть настройки")
3. Вкладка **"Настройки"** → укажите путь к Dota 2, например:
   ```
   C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta
   ```
4. Вкладка **"Статус"** → нажмите **"Пересоздать GSI конфиг"**
5. Перезапустите Dota 2

### Ручная настройка
Создайте файл:
```
<путь_к_dota>\game\dota\cfg\gamestate_integration\gamestate_integration_dota_hud.cfg
```

Полный путь (пример):
```
C:\Program Files (x86)\Steam\steamapps\common\dota 2 beta\game\dota\cfg\gamestate_integration\gamestate_integration_dota_hud.cfg
```

Содержимое файла:
```
"Dota HUD" {
  "uri" "http://127.0.0.1:4000"
  "timeout" "5.0"
  "buffer" "0.1"
  "throttle" "0.1"
  "heartbeat" "30.0"
  "data" {
    "map" "1"
    "hero" "1"
    "player" "1"
    "items" "1"
  }
}
```

После создания файла **перезапустите Dota 2**.

## 5) Запуск

### Вариант A: Через Poetry (рекомендуется)
```cmd
cd C:\Games\d2hub
poetry run dota-hud
```

С кастомным конфигом:
```cmd
poetry run dota-hud путь\к\timings.yaml
```

### Вариант A2: Без Poetry
```cmd
cd C:\Games\d2hub
.venv\Scripts\activate
python -m dota_hud
```

### Вариант B: Готовый .exe (рекомендуется для обычного использования)

Сборка:
```cmd
cd C:\Games\d2hub
.venv\Scripts\activate
pip install pyinstaller
pyinstaller d2hub.spec --clean
```

Или через скрипт:
```cmd
scripts\build.bat
```

Результат: `dist\D2Hub.exe` — запускается двойным кликом. Можно добавить в автозагрузку Windows.

## 6) Как работает приложение

### При запуске
1. В **системном трее** появляется иконка D2Hub (серый кружок)
2. Приложение проверяет YAML-конфиги на корректность
3. Каждые 5 секунд проверяет, запущена ли `dota2.exe`

### Когда Dota запущена
1. Иконка становится **жёлтой** (Dota найдена, ожидание GSI)
2. Запускается GSI-сервер на порту 4000
3. Когда GSI начинает присылать данные — иконка **зелёная**
4. Появляется **HUD overlay** поверх игры

### Когда Dota закрыта
1. HUD скрывается
2. GSI-сервер останавливается
3. Иконка в трее снова серая, приложение ждёт

## 7) Управление

### System Tray (правый клик по иконке)
- **Статус** — показывает текущее состояние (Online/Offline)
- **Открыть настройки** — окно админки с вкладками
- **Показать/скрыть HUD** — переключение видимости overlay
- **Роль** — выбор: Carry / Mid / Offlane / Soft Support / Hard Support
- **Выход** — закрытие приложения

### Горячие клавиши
- **F7** — lock/unlock HUD
  - **Lock**: клики проходят сквозь HUD (играете как обычно)
  - **Unlock**: HUD можно перетаскивать мышью

## 8) Админка (окно настроек)

Открывается из трея → "Открыть настройки". 7 вкладок:

| Вкладка | Что делает |
|---------|-----------|
| **Тайминги** | Добавить/изменить/удалить события по времени (0:00 — "Купить OBS") |
| **Правила** | Повторяющиеся напоминания (каждые 30 сек — "Проверь миникарту") |
| **Предупреждения** | Окна риска с уровнями danger/warn/info |
| **Macro** | Настройка рун: интервал, цвет прогресс-бара |
| **Сборка** | Рекомендуемая сборка на героя, вкл/выкл подсказки в HUD |
| **Настройки** | Позиция HUD, прозрачность, шрифт, хоткеи, путь к Dota |
| **Статус** | Dota/GSI/герой/роль/конфиг — текущее состояние + кнопка пересоздания GSI |

Все изменения сохраняются в YAML и применяются **без перезапуска** (hot-reload).

## 9) Роли и фильтрация подсказок

При обнаружении героя через GSI приложение автоматически предлагает роль (например, Crystal Maiden → Hard Support). Роль можно сменить в трей-меню.

Подсказки фильтруются по роли. В YAML можно указать:
```yaml
timeline:
  - at: "0:00"
    items: ["Купить OBS + Sentry, стакнуть лагерь"]
    roles: [soft_support, hard_support]  # только для саппортов
  - at: "7:00"
    items: ["Wisdom rune"]
    # roles не указано — показывается всем ролям
```

Доступные роли: `carry`, `mid`, `offlane`, `soft_support`, `hard_support`.

## 10) Что отображает HUD
- **Таймер матча** (синхронизирован с Dota через GSI)
- **NOW** — события прямо сейчас
- **NEXT** — следующее событие с обратным отсчётом
- **MACRO** — прогресс-бары рун (Wisdom/Power/Bounty)
- **Предупреждения** — окна риска с цветовой индикацией
- **BUILD** — подсказка по следующему предмету из сборки (опционально)

## 11) Конфигурация

Основной файл: `configs/timings.yaml`

```yaml
hud:
  title: "Dota HUD"
  width: 549
  height: 400
  x: 30
  y: 30
  alpha: 0.60
  font_family: "Radiance"
  font_size: 18

hotkeys:
  lock: F7

general:
  dota_path: "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta"
  gsi_port: 4000

build_integration:
  enabled: false
  provider: "static"
  static_path: "builds.json"

macro_config: "macro.yaml"
modules:
  - "modules/timeline.yaml"
  - "modules/rules.yaml"
  - "modules/windows.yaml"
```

### Модульная структура конфигов
```
configs/
  timings.yaml          # основной конфиг
  macro.yaml            # макро-тайминги (руны)
  modules/
    timeline.yaml       # разовые события по времени
    rules.yaml          # повторяющиеся правила
    windows.yaml        # окна риска (danger/warn/info)
```

## 12) Безопасность и легальность
- HUD использует **официальный GSI** от Valve
- HUD **не вмешивается в клиент Dota 2** и не изменяет игровые файлы
- HUD **не дает скрытых данных** и **не автоматизирует действия**
- HUD не является читом и не дает unfair advantage

## 13) Частые проблемы

### HUD не появляется
- Убедитесь что Dota 2 запущена
- Проверьте иконку в трее — какой цвет?
- Серая → Dota не обнаружена, проверьте что `dota2.exe` запущен
- Жёлтая → GSI не подключён, проверьте GSI конфиг

### Dota не шлёт данные
- Проверьте что файл `gamestate_integration_dota_hud.cfg` создан в правильной папке
- Убедитесь что в файле есть секции `"hero" "1"`, `"player" "1"`, `"items" "1"`
- Перезапустите Dota 2 после создания/изменения файла

### Подсказки не фильтруются по роли
- Проверьте что роль выбрана в трей-меню
- Убедитесь что в YAML у событий указано поле `roles`

### Ошибка при запуске
```cmd
# Проверьте что все зависимости установлены:
pip install PySide6 PyYAML aiohttp

# Запустите тесты:
python -m pytest tests/ -v
```

## 14) Разработка

### Запуск тестов
```cmd
cd C:\Games\d2hub
.venv\Scripts\activate
python -m pytest tests/ -v
```

### Структура проекта
```
src/dota_hud/
  __main__.py              # точка входа (tray-based)
  application/             # use cases, presenter, controller
  domain/                  # scheduler, events, roles, warnings
  infrastructure/          # GSI server, hotkeys, Dota detector, build provider
  config/                  # YAML loader, mapper, validator
  ui/qt/                   # PySide6: HUD overlay, admin window, tray
```

### Архитектура
Clean Architecture: domain → application → infrastructure/UI. Протоколы вместо интерфейсов, конфигурация через YAML.