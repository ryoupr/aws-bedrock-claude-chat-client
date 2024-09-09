import asyncio
import tkinter as tk
import tkinter.font as tkFont
from threading import Thread
from tkinter import scrolledtext, ttk

import pyperclip  # クリップボードにコピーするためのライブラリ
from langchain.memory import ConversationBufferMemory

from chat_claude import chat_claude  # ここでstreamバージョンをインポート

memory = ConversationBufferMemory()


# チャット画面を作るクラス
class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Chat")

        # モダンなテーマを設定
        style = ttk.Style()
        style.theme_use("clam")  # clam, alt, defaultなど他のテーマも試せます

        # ウィンドウのリサイズを許可
        self.root.resizable(True, True)

        # フォント設定
        font_style = tkFont.Font(family="Helvetica", size=12)

        # チャットエリア
        self.chat_area = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state="disabled",
            width=50,
            height=20,
            font=font_style,
            bg="#f0f0f0",
            relief="flat",
        )
        self.chat_area.grid(
            row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew"
        )

        # プロンプト入力エリア (ttkを使ったよりモダンなスタイル)
        self.input_area = tk.Text(
            root,
            height=3,
            width=40,
            font=font_style,
            bg="#ffffff",
            relief="solid",
            bd=1,
        )
        self.input_area.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # 入力エリアに初期フォーカスをセット
        self.input_area.focus_set()

        # Ctrl + Enterでメッセージ送信をバインド
        self.input_area.bind("<Control-Return>", self.ctrl_enter_pressed)

        # 送信ボタン (ttk.Buttonでスタイルを改善)
        self.send_button = ttk.Button(
            root,
            text="送信",
            command=self.start_async_send_message,
            style="Accent.TButton",
        )
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # ウィンドウ内のグリッドのサイズを柔軟に
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    # チャットにメッセージを追加する関数（区切り線追加）
    def add_message(self, message, sender):
        self.chat_area.config(state="normal")
        # 発言の前に区切り線を挿入
        self.chat_area.insert(tk.END, f"\n{'-'*50}\n")
        self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        self.chat_area.config(state="disabled")
        self.chat_area.yview(tk.END)  # 自動スクロール

    # ストリームの部分的な応答を追加する関数
    def stream_response_update(self, chunk):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, chunk)  # 部分的な応答を追加
        self.chat_area.config(state="disabled")
        self.chat_area.yview(tk.END)

    # コードブロックを表示する関数
    def add_code_block(self, code):
        self.code_text = code  # コードブロックのテキストを保存
        self.chat_area.config(state="normal")
        self.chat_area.insert(
            tk.END, f"\n```{code}```\n", "code_block"
        )  # コードブロック表示
        self.chat_area.tag_configure(
            "code_block",
            background="#f0f0f0",
            foreground="black",
            font=("Consolas", 10),
        )
        self.chat_area.config(state="disabled")
        self.chat_area.yview(tk.END)

    # Ctrl + Enterが押されたときの処理
    def ctrl_enter_pressed(self, event):
        self.start_async_send_message()
        return "break"  # 通常の改行動作を防ぐ

    # メッセージ送信時の非同期処理を開始する
    def start_async_send_message(self):
        # 送信ボタンを無効化
        self.send_button.config(state="disabled")
        Thread(target=self.async_send_message).start()

    # 非同期でメッセージ送信処理を実行する
    def async_send_message(self):
        asyncio.run(self.send_message())

    # メッセージ送信時の処理
    async def send_message(self):
        user_message = self.input_area.get(
            "1.0", tk.END
        ).strip()  # 入力エリアのテキストを取得
        if user_message:
            self.add_message(user_message, "ユーザー")  # ユーザーのメッセージを追加
            self.input_area.delete("1.0", tk.END)  # 入力エリアをクリア

            # "読み込み中..."メッセージを追加
            self.add_message("読み込み中...", "AI")

            # 非同期でAIからの返答を取得 (ストリーム対応)
            await asyncio.to_thread(
                chat_claude, user_message, memory, self.stream_response_update
            )

            # "読み込み中..."を削除
            self.chat_area.config(state="normal")
            self.chat_area.delete("end-2l", "end-1l")  # 読み込み中...の行を削除
            self.chat_area.config(state="disabled")

        # 全ての処理が終わった後に送信ボタンを再度有効化
        self.send_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()
