from langchain.memory import ConversationBufferMemory
from langchain_aws import ChatBedrock

# メモリを作成
memory = ConversationBufferMemory()


def chat_claude(user_prompt: str):

    # LLMモデルの定義
    chat = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs={"temperature": 0.1},
        region_name="ap-northeast-1",
    )

    # モデルにプロンプトを送信し、応答を取得
    res = chat.invoke(user_prompt)

    # メモリにユーザープロンプトとモデルの応答を追加
    memory.save_context({"input": user_prompt}, {"output": res.content})

    # メモリの履歴を取得
    conversation_history = memory.load_memory_variables({})

    # メモリの履歴を表示（デバッグ用、またはGUIで表示）
    print("会話履歴:")
    print(conversation_history)

    return res.content
