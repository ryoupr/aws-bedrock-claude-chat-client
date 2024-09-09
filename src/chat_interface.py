import tkinter as tk
import tkinter.font as tkFont
from tkinter import scrolledtext

from chat_claude import chat_claude


# チャット画面を作るクラス
class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat")
        self.input_area = tk.Text(
            root, height=3, width=40, font=tkFont.Font(family="Arial", size=12)
        )

        # チャットエリア
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state="disabled", width=50, height=20
        )
        self.chat_area.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # プロンプト入力エリア
        self.input_area = tk.Text(root, height=3, width=40)
        self.input_area.grid(row=1, column=0, padx=10, pady=10)
        # フォントの設定

        # Ctrl + Enterでメッセージ送信をバインド
        self.input_area.bind("<Control-Return>", self.ctrl_enter_pressed)

        # 送信ボタン
        self.send_button = tk.Button(root, text="送信", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

    # チャットにメッセージを追加する関数
    def add_message(self, message, sender):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.config(state="disabled")
        self.chat_area.yview(tk.END)  # 自動スクロール

    # Ctrl + Enterが押されたときの処理
    def ctrl_enter_pressed(self, event):
        self.send_message()
        return "break"  # 通常の改行動作を防ぐ

    # メッセージ送信時の処理
    def send_message(self):
        user_message = self.input_area.get(
            "1.0", tk.END
        ).strip()  # 入力エリアのテキストを取得
        if user_message:
            self.add_message(user_message, "ユーザー")  # ユーザーのメッセージを追加
            self.input_area.delete("1.0", tk.END)  # 入力エリアをクリア

            # AIからの返答を取得
            ai_response = chat_claude(user_message)
            self.add_message(ai_response, "AI")  # AIのメッセージを追加


if __name__ == "__main__":
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()
