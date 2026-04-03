# D2Hub v2 — Дизайн-спецификация

## Обзор

Эволюция Dota 2 HUD-помощника: из CLI-запускаемого overlay в полноценное десктопное приложение с system tray, админкой, расширенной GSI-интеграцией, определением роли и подсказками по сборкам.

**Платформа:** Windows only.
**Ограничение:** внешний вид HUD overlay не меняется (Dota+ стиль сохраняется).

---

## 1. System Tray + автодетект Dota

### Tray-иконка

Три состояния:
- **Серая** — Dota не запущена, приложение ждёт
- **Жёлтая** — Dota запущена, GSI ещё не подключился
- **Зелёная** — GSI активен, всё работает

### Контекстное меню (правый клик)

- Статус: "Dota: Online/Offline"
- Открыть настройки → Admin Panel
- Показать/скрыть HUD
- Роль: [текущая ▾] → подменю: carry / mid / offlane / soft_support / hard_support
- Выход

### Автодетект Dota

- Поллинг `tasklist` на `dota2.exe` каждые 5 секунд
- Dota найдена → запуск GSI-сервера, показ HUD
- Dota закрыта → скрытие HUD, остановка GSI-сервера, возврат в режим ожидания

### Запуск "с кнопки"

- PyInstaller собирает в `.exe`
- Ярлык на рабочий стол / в меню Пуск
- Опциональное добавление в автозагрузку Windows

---

## 2. Валидация конфигов при запуске

При старте приложения последовательно проверяются:

1. **GSI конфиг файл** — существует ли `gamestate_integration_dota_hud.cfg` в папке Dota (`cfg/gamestate_integration/`). Если нет — предложить создать автоматически.
2. **Содержимое GSI конфига** — правильный порт (4000), запрошены нужные секции (`map`, `hero`, `player`, `items`), адекватные таймауты.
3. **YAML конфиги приложения** — `timings.yaml` и все модули валидны, нет битых ссылок, тайминги парсятся без ошибок.
4. **Статус соединения** — после старта tray-иконка отражает состояние: "Ожидание Dota..." → "GSI подключён" / "GSI не отвечает".

При ошибках — tray notification с описанием проблемы.

---

## 3. Расширение GSI

### Новый GSI конфиг

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

### Расширение GSIState

Новые поля из GSI payload:
- `hero.name` — имя героя (`npc_dota_hero_crystal_maiden`)
- `player.kills`, `player.deaths`, `player.assists`, `player.gpm`, `player.last_hits`, `player.wards_placed`
- `items.slot0..5` — текущие предметы (имя, cooldown)

### Определение роли

- Статичный маппинг `hero_name → default_role` в YAML/JSON (~130 героев)
- При обнаружении героя → tray-нотификация: "Crystal Maiden → Hard Support. Сменить?"
- Роль можно переключить в трей-меню в любой момент матча

### Фильтрация подсказок по роли

В YAML таймингах опциональное поле `roles`:

```yaml
timeline:
  - at: "0:00"
    items: ["Stack camp for carry"]
    roles: [soft_support, hard_support]
  - at: "7:00"
    items: ["Wisdom rune"]
    # roles не указано — показывается всем
```

Если `roles` не указано — подсказка для всех. Если указано — только для выбранной роли.

---

## 4. Админка (Qt окно из трея)

Qt окно с вкладками, открывается из tray-меню. Не блокирует HUD.

### Вкладки

1. **Тайминги (Timeline)** — таблица: время | подсказка | роли. CRUD кнопки. Сортировка по времени.
2. **Правила (Rules)** — таблица: start | until | every | текст | роли. CRUD.
3. **Предупреждения (Windows)** — таблица: from | to | level | priority | текст. Выпадающий список для level (danger/warn/info).
4. **Macro тайминги** — таблица: название | first_spawn | interval | up_window | цвет. Color picker для цвета прогресс-бара.
5. **Сборка героя** — текущий герой (из GSI), рекомендуемая сборка (из d2pt), чекбокс "Показывать в HUD".
6. **Общие настройки** — позиция X/Y, прозрачность (слайдер), размер шрифта, хоткей lock, путь к Dota (`dota_path` — единое поле, используется для поиска GSI конфига и console.log).
7. **Статус** — Dota запущена/нет, GSI подключён/нет, конфиг валиден/нет, текущий герой, роль. Кнопка "Пересоздать GSI конфиг".

### Hot-reload

При сохранении любой вкладки — YAML перезаписывается, `AppController` перечитывает конфиг без перезапуска. HUD обновляется мгновенно.

---

## 5. Оптимизация производительности

### 5.1 Dirty-flag для UI

Сейчас `_apply_text_colors()` и `self.update()` вызываются каждые 200мс даже без изменений. Добавить грязный флаг — перерисовка только при реальном изменении состояния.

### 5.2 Пул виджетов MacroProgressBar

Сейчас `_apply_macro_lines()` удаляет и пересоздаёт все виджеты каждый вызов. Создать пул — инициализировать один раз, обновлять через `set_data()`.

### 5.3 Замена библиотеки keyboard

Глобальный хук `keyboard` перехватывает ВСЕ нажатия. Заменить на `RegisterHotKey` WinAPI (через ctypes) — регистрируем только нужные клавиши (F7).

### 5.4 Убрать print в GSI handler

`print("[GSI]", state_copy)` на каждый POST (~10 раз/сек). Заменить на `logging` с уровнем DEBUG.

### 5.5 aiohttp вместо HTTPServer

Заменить синхронный `http.server.HTTPServer` на `aiohttp`. Это также унифицирует async-подход для d2pt API запросов.

---

## 6. Интеграция d2pt — build hint в HUD

### Получение данных

- При определении героя + роли → запрос к d2pt API (через aiohttp)
- Кеширование на матч — один запрос на героя
- Если API недоступен → строка не показывается, ошибка в лог

### Отображение в HUD

- Новый блок `BUILD` — одна строка под MACRO
- Формат: `"Next: BKB ~4200g"`
- "Следующий" предмет: сравнение текущих предметов из GSI `items` с рекомендуемой сборкой → первый отсутствующий
- Вкл/выкл через настройки

### Fallback-стратегия

Адаптер с интерфейсом `BuildProvider`:
- **d2pt** (приоритет) — API запрос
- **static** (fallback) — локальный JSON, обновляемый раз в патч

### Конфиг

```yaml
build_integration:
  enabled: true
  provider: "d2pt"
  static_path: "builds.json"
```

---

## 7. Поток данных (итого)

```
Dota 2 →(GSI POST)→ aiohttp Server :4000 →(hero, items, map, player)→ AppController
AppController →(hero name)→ Role detection (static map + user override)
AppController →(role)→ Filtered timings → HUD Overlay
AppController →(hero + role)→ d2pt API →(build)→ HUD "Next item" hint
Admin Panel →(save YAML)→ AppController.reload() → HUD обновлён
```

## 8. Жизненный цикл

```
Запуск (.exe / ярлык) → Валидация конфигов → Tray icon (серый)
Поллинг dota2.exe (5 сек) → Dota найдена → Tray (жёлтый) + GSI сервер старт
GSI данные получены → hero определён → роль предложена → Tray (зелёный) + HUD показан
Dota закрыта → HUD скрыт → GSI сервер стоп → Tray (серый, ожидание)
```

## 9. Новые зависимости

- `aiohttp` — async HTTP сервер + клиент для d2pt API
- `pyinstaller` (dev) — сборка в .exe

Убираем:
- `keyboard` — заменяем на WinAPI RegisterHotKey (ctypes, без зависимости)
