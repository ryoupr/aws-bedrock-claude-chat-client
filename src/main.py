import tkinter as tk

from chat_interface import ChatGUI


def main():
    root = tk.Tk()
    ChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
