import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QIcon, QPixmap, QRegion
from ollama_service import get_ollama_response  

class OllamaWorker(QThread):
    """ เธรดสำหรับเรียกใช้ Ollama API โดยไม่ให้ UI ค้าง """
    response_ready = Signal(str)  # ส่งข้อความตอบกลับไปยัง UI

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        response = get_ollama_response(self.message)  # เรียก API ของ Ollama
        self.response_ready.emit(response)  # ส่งข้อความตอบกลับไปยัง UI


class OOPChat(QMainWindow):
    """ คลาสหลักของแอปพลิเคชันแชท """
    
    def __init__(self):
        super().__init__()
        self.setup_main_window()
        self.create_chat_area()
        self.create_input_area()

    def setup_main_window(self):
        """ ตั้งค่าหน้าต่างหลักของแอปพลิเคชัน """
        self.setWindowTitle("DeepSeek-R1 Chat")
        self.resize(600, 500)
        self.setWindowIcon(QIcon('pyside-project-naza/logo/images.png'))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

    def create_chat_area(self):
        """ สร้างพื้นที่แชท """
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_container)

        self.layout.addWidget(self.scroll_area)

    def create_input_area(self):
        """ สร้างช่องป้อนข้อความ และปุ่มส่ง """
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setFixedHeight(40)
        self.input_field.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("SEND")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.layout.addLayout(input_layout)

    def send_message(self):
        """ ส่งข้อความของผู้ใช้ และปิดการป้อนข้อความจนกว่าจะได้รับผลลัพธ์ """
        user_message = self.input_field.text().strip()
        if user_message:
            self.add_message(f"User: {user_message}", alignment=Qt.AlignRight)
            self.input_field.clear()

            # ปิดช่องป้อนข้อความ และปุ่มส่ง เพื่อป้องกันการกดซ้ำ
            self.input_field.setDisabled(True)
            self.send_button.setDisabled(True)

            # สร้างและรันเธรดสำหรับการประมวลผลข้อความ
            self.worker = OllamaWorker(user_message)
            self.worker.response_ready.connect(self.display_response)
            self.worker.start()

    def display_response(self, response):
        """ แสดงข้อความตอบกลับจาก DeepSeek-R1 และเปิดการใช้งานช่องป้อนข้อความอีกครั้ง """
        self.add_message(f"DeepSeek-R1: {response}", alignment=Qt.AlignLeft)

        # เปิดช่องป้อนข้อความและปุ่มส่งเมื่อได้รับผลลัพธ์
        self.input_field.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_field.setFocus()  # ให้โฟกัสกลับไปที่ช่องป้อนข้อความ

        # 📌 เลื่อนลงล่างสุดเมื่อข้อความของ DeepSeek-R1 ถูกเพิ่ม
        QTimer.singleShot(0, self.scroll_to_bottom)

    def add_message(self, text, alignment=Qt.AlignLeft):
        """ เพิ่มข้อความลงในพื้นที่แชท และปรับขนาดกล่องข้อความให้พอดีกับเนื้อหา """
        label = QLabel(text)
        label.setWordWrap(True)
        label.adjustSize()

        # คำนวณขนาดของ QLabel ตามข้อความ
        content_width = label.sizeHint().width() + 20  # +20 เพื่อเผื่อ padding
        max_width = self.scroll_area.width() - 50  # จำกัดขนาดไม่ให้เกิน ScrollArea
        actual_width = min(content_width, max_width)

        label.setMinimumWidth(actual_width)
        label.setMaximumWidth(actual_width)

        # กำหนดสไตล์กล่องข้อความ
        if alignment == Qt.AlignRight:
            label.setStyleSheet("""
                color: white;
                background: #3f3a3a;
                padding: 8px 12px;
                border-radius: 12px;
                font-size: 14px;
            """)
        else:
            label.setStyleSheet("""
                color: white;
                background: #525252;
                padding: 8px 12px;
                border-radius: 12px;
                font-size: 14px;
            """)

        # สร้าง container สำหรับข้อความ
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.addWidget(label)
        container_layout.setAlignment(alignment)
        container_layout.setContentsMargins(10, 5, 10, 5)

        self.chat_layout.addWidget(container)

        # 📌 เลื่อน ScrollBar ไปด้านล่างสุดเสมอ
        QTimer.singleShot(0, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """ เลื่อน ScrollBar ไปด้านล่างสุดของ QScrollArea """
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OOPChat()
    window.show()
    sys.exit(app.exec())
