from PySide6.Qt3DExtras import Qt3DWindow, Qt3DWindow
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QVector3D

class PreviewThumb(QWidget):
    def __init__(self, library: Library, driver: "QtDriver"):
        # ... mevcut init kodu ...
        self.preview_3d = GLViewer()
        container = QWidget.createWindowContainer(self.preview_3d)
        container.setMinimumSize(512, 512)
        container.hide()
        image_layout.addWidget(container) 