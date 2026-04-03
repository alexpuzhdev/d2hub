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
    from .config.validator import validate_yaml_configs
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

    tray.set_callbacks(
        on_open_settings=admin.show,
        on_toggle_hud=controller.toggle_hud_visibility,
        on_role_changed=controller.set_role,
        on_quit=lambda: (detector.stop(), controller.shutdown(), app.quit()),
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
