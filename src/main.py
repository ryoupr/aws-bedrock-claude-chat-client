from chat_claude import chat_claud


def main():
    user_prompt = input("> ")
    res = chat_claud(user_prompt=user_prompt)
    print(res)


if __name__ == "__main__":
    main()
