import sys

from langchain.memory import ConversationBufferMemory
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from chat_claude import chat_claude

memory = ConversationBufferMemory()


class WorkerThread(QtCore.QThread):
    update_signal = QtCore.pyqtSignal(str)

    def __init__(self, user_message):
        super().__init__()
        self.user_message = user_message
        self.response_buffer = ""

    def run(self):
        chat_claude(self.user_message, memory, self.stream_response_update)
        # レスポンスが途中で途切れないよう、最後の残りのバッファを送信
        if self.response_buffer:
            self.update_signal.emit(self.response_buffer)

    def stream_response_update(self, response_chunk):
        self.response_buffer += response_chunk
        if len(self.response_buffer) > 10 or "\n" in response_chunk:
            self.update_signal.emit(self.response_buffer)
            self.response_buffer = ""  # バッファをクリア


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Chat with Claude - PyQt5")
        self.setGeometry(100, 100, 600, 400)

        # メッセージ送信中かどうかのフラグ
        self.is_sending = False

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # モダンなスタイルシートを定義
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2c3e50;
            }
            QTextEdit {
                background-color: #34495e;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1abc9c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """
        )

        # フォント設定
        self.user_font = QtGui.QFont("Helvetica Neue", 12)
        self.ai_font = QtGui.QFont("Helvetica Neue", 12)
        self.input_font = QtGui.QFont("Helvetica Neue", 12)

        # Scroll area for messages
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(self.ai_font)
        self.layout.addWidget(self.chat_area)

        # Input field for the user's message
        self.input_area = QTextEdit(self)
        self.input_area.setFont(self.input_font)
        self.input_area.setFixedHeight(30)
        self.input_area.textChanged.connect(self.adjust_input_area_height)
        self.layout.addWidget(self.input_area)

        # Send button
        self.send_button = QPushButton("Send", self)
        self.send_button.setFont(self.input_font)
        self.send_button.clicked.connect(self.start_worker_thread)
        self.layout.addWidget(self.send_button)

        self.input_area.setPlaceholderText(
            "Type your message here and press Ctrl + Enter to send..."
        )
        self.input_area.setFocus()

    def keyPressEvent(self, event):
        if (
            event.key() == QtCore.Qt.Key_Return
            and event.modifiers() == QtCore.Qt.ControlModifier
        ):
            self.start_worker_thread()
        elif event.key() == QtCore.Qt.Key_Return:
            cursor = self.input_area.textCursor()
            cursor.insertText("\n")
        else:
            super().keyPressEvent(event)

    def adjust_input_area_height(self):
        document_height = self.input_area.document().size().height()
        self.input_area.setFixedHeight(int(document_height) + 10)

    def start_worker_thread(self):
        if self.is_sending:  # 送信中は処理を行わない
            return

        user_message = self.input_area.toPlainText().strip()
        if user_message:
            self.is_sending = True  # 送信中フラグをセット
            self.send_button.setEnabled(False)  # 送信ボタンを無効化
            self.input_area.setEnabled(False)  # 入力エリアを無効化
            self.add_message(user_message, "User")
            self.input_area.clear()
            self.input_area.setFixedHeight(30)
            self.add_message("", "AI")
            self.worker = WorkerThread(user_message)
            self.worker.update_signal.connect(self.stream_response_update)
            self.worker.finished.connect(self.on_worker_finished)  # 終了時の処理
            self.worker.start()

    def add_message(self, message, sender):
        if sender == "User":
            self.chat_area.append(f"User: {message}")
        else:
            self.chat_area.append(f"AI: {message}")

    def stream_response_update(self, response_chunk):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(response_chunk.strip())
        self.chat_area.ensureCursorVisible()

    def on_worker_finished(self):
        """AIの返答が完了したときに呼ばれる関数"""
        self.is_sending = False  # 送信中フラグをリセット
        self.send_button.setEnabled(True)  # 送信ボタンを再び有効化
        self.input_area.setEnabled(True)  # 入力エリアを再び有効化
        self.input_area.setFocus()  # フォーカスを入力エリアに戻す


def launch_gui_window():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch_gui_window()
