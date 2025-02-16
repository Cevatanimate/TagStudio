from PySide6.Qt3DExtras import Qt3DWindow, Qt3DWindow, QOrbitCameraController
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QVector3D, QColor, QRgb
from PySide6.QtCore import QUrl
from PySide6.QtGui import QSurfaceFormat

class GLViewer(Qt3DWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rootEntity = Qt3DCore.QEntity()
        self.setRootEntity(self.rootEntity)
        
        # Camera Settings
        self.camera().lens().setPerspectiveProjection(45.0, 16.0/9.0, 0.1, 1000)
        self.camera().setPosition(QVector3D(0, 0, 20))
        self.camera().setViewCenter(QVector3D(0, 0, 0))
        
        # Lighting
        self.lightEntity = Qt3DCore.QEntity(self.rootEntity)
        self.light = Qt3DRender.QPointLight(self.lightEntity)
        self.light.setColor("white")
        self.light.setIntensity(1)
        self.lightEntity.addComponent(self.light)
        
        # Kamera kontrolcüsü ekle
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setLinearSpeed(50)
        self.camController.setLookSpeed(180)
        self.camController.setCamera(self.camera())
        
    def load_model(self, file_path):
        # Eski mesh yerine scene loader kullan
        self.sceneLoader = Qt3DRender.QSceneLoader(self.rootEntity)
        self.sceneLoader.setSource(QUrl.fromLocalFile(file_path))
        
        # Model yüklenme durumunu kontrol et
        self.sceneLoader.statusChanged.connect(self.on_scene_loaded)
        
        # Temel materyal ayarları
        self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)
        self.material.setDiffuse(QColor(200, 200, 200))
        
        # Varsayılan transform ayarları
        self.transform = Qt3DCore.QTransform()
        self.transform.setScale(1.0)
        
        # Entity oluştur ve bileşenleri ekle
        self.modelEntity = Qt3DCore.QEntity(self.rootEntity)
        self.modelEntity.addComponent(self.sceneLoader)
        self.modelEntity.addComponent(self.material)
        self.modelEntity.addComponent(self.transform)
        
    def on_scene_loaded(self, status):
        if status == Qt3DRender.QSceneLoader.Ready:
            print("Model başarıyla yüklendi")
            # Model merkezini kamera görüşüne ayarla
            self.camera().setViewCenter(QVector3D(0, 0, 0))
        else:
            print(f"Model yükleme hatası: {status}")

    def mousePressEvent(self, event):
        self.mousePos = event.position()

    def mouseMoveEvent(self, event):
        delta = event.position() - self.mousePos
        self.camera().setPosition(self.camera().position() + QVector3D(delta.x(), delta.y(), 0))
        self.mousePos = event.position()

    def wheelEvent(self, event):
        zoom = event.angleDelta().y() * 0.1
        self.camera().setPosition(self.camera().position() + QVector3D(0, 0, zoom)) 

def check_opengl_support():
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    QSurfaceFormat.setDefaultFormat(fmt) 