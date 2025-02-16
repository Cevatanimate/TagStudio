from PySide6.Qt3DExtras import Qt3DWindow, Qt3DWindow, QOrbitCameraController
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QVector3D, QColor, QRgb
from PySide6.QtCore import QUrl
from PySide6.QtGui import QSurfaceFormat
from PIL import Image, ImageDraw
import io
from PySide6.QtCore import QByteArray

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
        
        # Varsayılan dama tahtası texture'ı oluştur
        self.default_texture = self.create_checker_texture()
        
    def create_checker_texture(self):
        # 128x128 dama tahtası deseni
        img = Image.new('RGB', (128, 128), color='white')
        draw = ImageDraw.Draw(img)
        for y in range(0, 128, 32):
            for x in range(0, 128, 32):
                if (x//32 + y//32) % 2 == 0:
                    draw.rectangle([x, y, x+32, y+32], fill='#404040')
        
        # PIL Image'ı Qt'ye uygun formata çevir
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        texture_data = QByteArray(byte_arr.getvalue())
        
        # Texture ve materyal ayarları
        texture = Qt3DRender.QTexture2D(self.rootEntity)
        textureImage = Qt3DRender.QTextureImage(texture)
        textureImage.setData(texture_data)
        texture.addTextureImage(textureImage)
        
        return Qt3DExtras.QDiffuseMapMaterial(self.rootEntity)
        self.default_texture.setDiffuse(Qt3DRender.QTexture2D(texture))
        self.default_texture.setShininess(100.0)
        self.default_texture.setSpecular(QColor(100, 100, 100))
        return self.default_texture

    def load_model(self, file_path):
        # Önceki modeli temizle
        if hasattr(self, 'modelEntity'):
            self.modelEntity.deleteLater()
        
        self.sceneLoader = Qt3DRender.QSceneLoader(self.rootEntity)
        self.sceneLoader.setSource(QUrl.fromLocalFile(file_path))
        
        # Otomatik kamera ayarlama
        self.camController.setCamera(self.camera())
        self.camera().setPosition(QVector3D(0, 5, 10))
        self.camera().setViewCenter(QVector3D(0, 0, 0))
        
        # Model transform ayarları
        self.transform = Qt3DCore.QTransform()
        self.transform.setScale(0.1)
        
        self.modelEntity = Qt3DCore.QEntity(self.rootEntity)
        self.modelEntity.addComponent(self.sceneLoader)
        self.modelEntity.addComponent(self.transform)
        
        # Model yüklenme durumunu kontrol et
        self.sceneLoader.statusChanged.connect(self.on_scene_loaded)
        
        # Materyal ayarları
        self.material = Qt3DExtras.QPhongMaterial(self.rootEntity)
        self.material.setDiffuse(QColor(200, 200, 200))
        
        # Texture koordinatları için gerekli component'ler
        self.tex_coord = Qt3DRender.QAttribute()
        self.tex_coord.setAttributeType(Qt3DRender.QAttribute.AttributeType.TextureCoordinateAttribute)
        self.tex_coord.setVertexBaseType(Qt3DRender.QAttribute.VertexBaseType.Float)
        self.tex_coord.setVertexSize(2)
        
        # Entity oluştur ve bileşenleri ekle
        self.modelEntity = Qt3DCore.QEntity(self.rootEntity)
        self.modelEntity.addComponent(self.sceneLoader)
        self.modelEntity.addComponent(self.material)
        self.modelEntity.addComponent(self.tex_coord)
        self.modelEntity.addComponent(self.default_texture)  # Varsayılan texture
        
        # Texture kontrolü
        self.sceneLoader.statusChanged.connect(self.check_textures)
        
    def on_scene_loaded(self, status):
        if status == Qt3DRender.QSceneLoader.Ready:
            print("Model başarıyla yüklendi")
            # Model merkezini kamera görüşüne ayarla
            self.camera().setViewCenter(QVector3D(0, 0, 0))
        else:
            print(f"Model yükleme hatası: {status}")

    def check_textures(self, status):
        if status == Qt3DRender.QSceneLoader.Ready:
            if not self.sceneLoader.entity().componentsOfType(Qt3DRender.QTexture):
                # Modelde texture yoksa varsayılanı uygula
                self.modelEntity.addComponent(self.default_texture)
                self.modelEntity.removeComponent(self.material)

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