import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QIcon, QPixmap, QRegion
from ollama_service import get_ollama_response  

class OOPChat(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setup_main_window()
        self.create_header()
        self.create_chat_area()
        self.create_input_area()

    def setup_main_window(self):
        self.setWindowTitle("deepseek-r1")
        self.resize(500, 400)
        self.setWindowIcon(QIcon('logo/images.png'))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

    def create_header(self):
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(10, 5, 10, 5)

        header_layout.addStretch()  # ✅ ดันให้รูปไปขวาสุด
        self.profile_label = QLabel(self)
        self.set_profile_picture('logo/df36998926ae39b879f530ffed16593d.jpg', size=32)
        header_layout.addWidget(self.profile_label, alignment=Qt.AlignRight)

        self.layout.addWidget(header_container)

    def create_chat_area(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_container)

        self.layout.addWidget(self.scroll_area)

    def create_input_area(self):
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setFixedHeight(40)
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("SEND")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.setContentsMargins(50, 20, 30, 10)

        self.layout.addLayout(input_layout)

    def set_profile_picture(self, image_path, size=80):
        pixmap = QPixmap(image_path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        mask = QRegion(QRect(0, -1, size, size), QRegion.Ellipse)
        self.profile_label.setPixmap(pixmap)
        self.profile_label.setFixedSize(size, size)
        self.profile_label.setMask(mask)

    def send_message(self):
        user_message = self.input_field.text().strip()
        if user_message:
            self.add_message(f"User: {user_message}", alignment=Qt.AlignRight)
            self.input_field.clear()

            # เรียกใช้ Ollama จาก `ollama_service.py`
            response = get_ollama_response(user_message)

            # แสดงข้อความตอบกลับ
            self.add_message(f"OOP Chat: {response}", alignment=Qt.AlignLeft)

    def add_message(self, text, alignment=Qt.AlignLeft):
        label = QLabel(text)
        label.setWordWrap(True)
        label.adjustSize()
        content_width = label.sizeHint().width()

        max_width = 300
        min_width = 100
        actual_width = min(max(content_width, min_width), max_width)
        
        label.setMinimumWidth(actual_width)
        label.setMaximumWidth(actual_width)

        if alignment == Qt.AlignRight:
            label.setStyleSheet("color: white; background: #3f3a3a; padding: 8px 12px; border-radius: 12px; font-size: 14px;")
        else:
            label.setStyleSheet("color: white; padding: 8px 12px; font-size: 14px;")

        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.addWidget(label)
        container_layout.setAlignment(alignment)
        container_layout.setContentsMargins(10, 5, 10, 5)

        self.chat_layout.addWidget(container)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OOPChat()
    window.show()
    sys.exit(app.exec())