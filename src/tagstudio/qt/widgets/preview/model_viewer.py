from __future__ import annotations

from pathlib import Path

import structlog
from PySide6.Qt3DCore import QEntity
from PySide6.Qt3DExtras import QOrbitCameraController, Qt3DWindow
from PySide6.Qt3DRender import QSceneLoader
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QHBoxLayout, QWidget

logger = structlog.get_logger(__name__)


class ModelViewer(QWidget):
    """Interactive 3‑D model viewer."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._window = Qt3DWindow()
        self._container = QWidget.createWindowContainer(self._window, self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._container)

        self._root = QEntity()
        self._loader = QSceneLoader(self._root)
        self._window.setRootEntity(self._root)

        camera = self._window.camera()
        camera.lens().setPerspectiveProjection(45.0, 16 / 9, 0.1, 1000.0)
        camera.setViewCenter((0, 0, 0))
        controller = QOrbitCameraController(self._root)
        controller.setCamera(camera)

    def load_model(self, file_path: Path) -> None:
        """Load a 3‑D model into the scene."""
        url = QUrl.fromLocalFile(str(file_path))
        if not self._loader.setSource(url):
            logger.warning("Failed to load 3‑D model", path=file_path)

