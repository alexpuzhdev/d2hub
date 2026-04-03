from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    from PySide6 import QtCore, QtWidgets
    from .application.app_controller import AppController
    from .config.loader import load_config
    from .config.reader import read_config
    from .config.validator import validate_yaml_configs
    from .config.gsi_config_writer import write_gsi_config
    from .infrastructure.dota_detector import DotaDetector
    from .ui.qt.tray import TrayIcon, TrayState
    from .ui.qt.admin_window import AdminWindow

    project_root = Path(__file__).resolve().parents[2]
    default_config = project_root / "configs" / "timings.yaml"
    config_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_config

    yaml_result = validate_yaml_configs(config_path)
    if not yaml_result.ok:
        logger.error("Config errors: %s", yaml_result.errors)

    config = load_config(config_path)

    # Читаем raw YAML для заполнения админки
    raw_config = read_config(config_path)
    # Мерж модулей для raw данных
    config_dir = config_path.parent
    for module_path in raw_config.get("modules", []):
        module_data = read_config(config_dir / module_path)
        for key in ("timeline", "rules", "windows", "danger_windows"):
            if key in module_data:
                raw_config.setdefault(key, []).extend(module_data[key])
    # Мерж macro
    macro_path = raw_config.get("macro_config")
    if macro_path:
        macro_data = read_config(config_dir / macro_path)
        if "macro_timings" in macro_data:
            raw_config["macro_timings"] = macro_data["macro_timings"]

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # Не завершать приложение при закрытии окон — живём в трее
    app.setQuitOnLastWindowClosed(False)

    tray = TrayIcon()
    if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
        logger.warning("System tray is not available on this system")
    tray.setVisible(True)
    tray.show()
    admin = AdminWindow()
    admin.load_from_raw_config(raw_config)

    # Кнопка пересоздания GSI конфига
    def _recreate_gsi() -> None:
        dota_path = admin.settings_dota_path.text().strip()
        if not dota_path:
            QtWidgets.QMessageBox.warning(admin, "Ошибка", "Укажите путь к Dota 2 во вкладке Настройки")
            return
        try:
            cfg = write_gsi_config(Path(dota_path))
            QtWidgets.QMessageBox.information(admin, "Готово", f"GSI конфиг создан:\n{cfg}\n\nПерезапустите Dota 2!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(admin, "Ошибка", f"Не удалось создать GSI конфиг:\n{e}")

    admin.set_on_recreate_gsi(_recreate_gsi)

    controller = AppController(config)

    # Thread-safe bridge: DotaDetector callbacks run in a worker thread,
    # but Qt widgets must be updated from the main thread.
    # Use QMetaObject.invokeMethod with QueuedConnection via signals.
    class DetectorBridge(QtCore.QObject):
        dota_found = QtCore.Signal()
        dota_lost = QtCore.Signal()

    bridge = DetectorBridge()
    bridge.dota_found.connect(
        lambda: (tray.set_state(TrayState.DOTA_FOUND), controller.start_services())
    )
    bridge.dota_lost.connect(
        lambda: (tray.set_state(TrayState.WAITING), controller.stop_services())
    )

    detector = DotaDetector(
        on_found=bridge.dota_found.emit,
        on_lost=bridge.dota_lost.emit,
    )
    detector.start()

    controller.set_on_admin(admin.show)

    tray.set_callbacks(
        on_open_settings=admin.show,
        on_toggle_hud=controller.toggle_hud_visibility,
        on_role_changed=controller.set_role,
        on_quit=lambda: (detector.stop(), controller.shutdown(), app.quit()),
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
