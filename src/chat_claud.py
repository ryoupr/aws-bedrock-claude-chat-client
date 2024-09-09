from langchain_aws import ChatBedrock


def chat_claud(user_prompt: str):

    # LLMモデルの定義
    chat = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs={"temperature": 0.1, "max_tokens": 4096},
        region_name="ap-northeast-1",
    )
    res = chat.invoke(user_prompt)
    return res.content
