import time

from langchain.memory import ConversationBufferMemory
from langchain_aws import ChatBedrock


def chat_claude(user_prompt: str, memory: ConversationBufferMemory, update_function):
    # LLMモデルの定義
    chat = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs={"temperature": 0.1},
        region_name="ap-northeast-1",
        streaming=True,  # ストリームを有効にする
    )

    # これまでの会話履歴を取得
    conversation_history = memory.load_memory_variables({})

    # モデルに送信するプロンプトに履歴を含める
    full_prompt = f"# 会話履歴\n{conversation_history}" + f"\nユーザー: {user_prompt}"

    # モデルにプロンプトを送信し、ストリーム応答を逐次取得
    response_stream = chat.stream(full_prompt)

    # ストリーム出力を少しずつ取得してGUIに反映
    full_response = ""
    for chunk in response_stream:
        chunk_text = chunk.content  # chunk.contentで文字列を取得
        update_function(chunk_text)  # GUIのテキストエリアに追加
        full_response += chunk_text
        time.sleep(0.1)  # ストリーム表示に間を持たせる（必要なら）

    # メモリにユーザープロンプトと最終的なモデルの応答を追加
    memory.save_context({"input": user_prompt}, {"output": full_response})

    return full_response
