from openai import (
    OpenAI,
    AuthenticationError,
    APIConnectionError,
    APIStatusError,
    RateLimitError,
)


DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def test_connection(api_key, model):
    """
    测试 DeepSeek API 是否可以正常连接。

    成功：
        返回模型回复的文本

    失败：
        抛出更容易理解的错误
    """

    client = OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL,
        timeout=20.0,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是 API 连接测试助手。",
                },
                {
                    "role": "user",
                    "content": "只回复 OK",
                },
            ],
            max_tokens=16,
            stream=False,

            # 测试连接没必要开启思考模式
            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            },
        )

        content = response.choices[0].message.content

        return (content or "OK").strip()

    except AuthenticationError:
        raise RuntimeError(
            "API Key 无效，请检查是否复制完整。"
        )

    except APIConnectionError:
        raise RuntimeError(
            "无法连接 DeepSeek，请检查网络连接。"
        )

    except RateLimitError:
        raise RuntimeError(
            "API 请求过于频繁，请稍后再试。"
        )

    except APIStatusError as exc:
        raise RuntimeError(
            f"DeepSeek API 返回错误：HTTP {exc.status_code}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"连接失败：{exc}"
        )
