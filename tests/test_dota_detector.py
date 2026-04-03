from __future__ import annotations

from unittest.mock import patch, MagicMock
from dota_hud.infrastructure.dota_detector import DotaDetector


def test_detector_not_running_when_process_absent():
    mock_result = MagicMock()
    mock_result.stdout = "Image Name                     PID\nSystem Idle Process              0"
    mock_result.returncode = 0
    with patch("subprocess.run", return_value=mock_result):
        detector = DotaDetector()
        assert detector.is_running() is False


def test_detector_running_when_process_present():
    mock_result = MagicMock()
    mock_result.stdout = "Image Name                     PID\ndota2.exe                      1234"
    mock_result.returncode = 0
    with patch("subprocess.run", return_value=mock_result):
        detector = DotaDetector()
        assert detector.is_running() is True


def test_detector_handles_exception():
    with patch("subprocess.run", side_effect=OSError("fail")):
        detector = DotaDetector()
        assert detector.is_running() is False


def test_callbacks_instantiated_with_on_found():
    callback = lambda: None
    detector = DotaDetector(on_found=callback)
    assert detector._on_found is callback


def test_callbacks_instantiated_with_on_lost():
    callback = lambda: None
    detector = DotaDetector(on_lost=callback)
    assert detector._on_lost is callback


def test_detector_custom_process_name():
    detector = DotaDetector(process_name="custom.exe")
    assert detector._process_name == "custom.exe"


def test_detector_custom_poll_interval():
    detector = DotaDetector(poll_interval=2.0)
    assert detector._poll_interval == 2.0
