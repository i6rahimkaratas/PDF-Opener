import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QScrollArea, QLabel, QFileDialog,
                             QMessageBox, QStatusBar, QToolBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFont
import fitz  # PyMuPDF


class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_document = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.total_pages = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        self.setWindowTitle("PDF Açıcı - Python")
        self.setGeometry(100, 100, 1000, 700)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Araç çubuğu oluştur
        self.create_toolbar()
        
        # Buton paneli
        button_layout = QHBoxLayout()
        
        # PDF Aç butonu
        self.open_button = QPushButton("PDF Aç")
        self.open_button.setFont(QFont("Arial", 10))
        self.open_button.clicked.connect(self.open_pdf)
        button_layout.addWidget(self.open_button)
        
        # Sayfa navigasyon butonları
        self.prev_button = QPushButton("◀ Önceki")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)
        button_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Sonraki ▶")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        button_layout.addWidget(self.next_button)
        
        button_layout.addStretch()
        
        # Zoom butonları
        self.zoom_out_button = QPushButton("🔍-")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setEnabled(False)
        button_layout.addWidget(self.zoom_out_button)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setMinimumWidth(50)
        button_layout.addWidget(self.zoom_label)
        
        self.zoom_in_button = QPushButton("🔍+")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setEnabled(False)
        button_layout.addWidget(self.zoom_in_button)
        
        self.fit_width_button = QPushButton("Genişliğe Sığdır")
        self.fit_width_button.clicked.connect(self.fit_to_width)
        self.fit_width_button.setEnabled(False)
        button_layout.addWidget(self.fit_width_button)
        
        main_layout.addLayout(button_layout)
        
        # Scroll area ve PDF görüntü alanı
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #f0f0f0; }")
        
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setText("PDF açmak için 'PDF Aç' butonuna tıklayın")
        self.pdf_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px dashed #cccccc;
                color: #666666;
                font-size: 16px;
                padding: 50px;
            }
        """)
        
        self.scroll_area.setWidget(self.pdf_label)
        main_layout.addWidget(self.scroll_area)
        
        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
    def create_toolbar(self):
        """Araç çubuğu oluştur"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Dosya işlemleri
        open_action = toolbar.addAction("📁 Aç")
        open_action.triggered.connect(self.open_pdf)
        
    def open_pdf(self):
        """PDF dosyası seç ve aç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDF Dosyası Seç",
            "",
            "PDF Dosyaları (*.pdf);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            try:
                self.pdf_document = fitz.open(file_path)
                self.total_pages = len(self.pdf_document)
                self.current_page = 0
                self.zoom_level = 1.0
                
                # Butonları etkinleştir
                self.zoom_in_button.setEnabled(True)
                self.zoom_out_button.setEnabled(True)
                self.fit_width_button.setEnabled(True)
                
                if self.total_pages > 1:
                    self.next_button.setEnabled(True)
                
                self.display_page()
                self.status_bar.showMessage(f"Dosya açıldı: {os.path.basename(file_path)} - {self.total_pages} sayfa")
                
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF dosyası açılamadı:\n{str(e)}")
                
    def display_page(self):
        """Mevcut sayfayı görüntüle"""
        if not self.pdf_document:
            return
            
        try:
            # Sayfayı al
            page = self.pdf_document[self.current_page]
            
            # Zoom faktörünü uygula
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            
            # PyQt5 pixmap'e dönüştür
            img_data = pix.tobytes("ppm")
            qpixmap = QPixmap()
            qpixmap.loadFromData(img_data)
            
            # Label'da göster
            self.pdf_label.setPixmap(qpixmap)
            self.pdf_label.resize(qpixmap.size())
            
            # Durum çubuğunu güncelle
            self.status_bar.showMessage(
                f"Sayfa {self.current_page + 1} / {self.total_pages} - Zoom: {int(self.zoom_level * 100)}%"
            )
            
            # Navigasyon butonlarını güncelle
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.total_pages - 1)
            
            # Zoom etiketini güncelle
            self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sayfa görüntülenirken hata oluştu:\n{str(e)}")
            
    def previous_page(self):
        """Önceki sayfaya git"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            
    def next_page(self):
        """Sonraki sayfaya git"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page()
            
    def zoom_in(self):
        """Yakınlaştır"""
        if self.zoom_level < 3.0:  # Maksimum %300 zoom
            self.zoom_level += 0.25
            self.display_page()
            
    def zoom_out(self):
        """Uzaklaştır"""
        if self.zoom_level > 0.25:  # Minimum %25 zoom
            self.zoom_level -= 0.25
            self.display_page()
            
    def fit_to_width(self):
        """Genişliğe sığdır"""
        if not self.pdf_document:
            return
            
        # Mevcut sayfa boyutlarını al
        page = self.pdf_document[self.current_page]
        page_rect = page.rect
        
        # Scroll area genişliğini al (scroll bar için biraz yer bırak)
        scroll_width = self.scroll_area.viewport().width() - 20
        
        # Zoom seviyesini hesapla
        self.zoom_level = scroll_width / page_rect.width
        
        # Çok küçük veya çok büyük zoom seviyelerini sınırla
        self.zoom_level = max(0.25, min(3.0, self.zoom_level))
        
        self.display_page()
        
    def keyPressEvent(self, event):
        """Klavye kısayolları"""
        if event.key() == Qt.Key_Right or event.key() == Qt.Key_Space:
            self.next_page()
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_Backspace:
            self.previous_page()
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()
        elif event.key() == Qt.Key_0:
            self.zoom_level = 1.0
            self.display_page()
        elif event.key() == Qt.Key_F:
            self.fit_to_width()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern görünüm için
    
    viewer = PDFViewer()
    viewer.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
