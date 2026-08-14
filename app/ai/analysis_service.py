import json
from datetime import datetime

from openai import OpenAI


DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def analyze_sectors(
    api_key: str,
    model: str,
    sectors: list[str],
) -> dict:
    """
    完整板块事件分析流程：

    1. 使用 DeepSeek Responses API + Web Search 搜索近期事件
    2. 使用 Chat Completions JSON Output 将资料整理为结构化 JSON
    """

    if not sectors:
        raise ValueError("没有选择任何板块。")

    client = OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_BASE_URL,
        timeout=120.0,
    )

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    sector_text = "、".join(sectors)

    # =========================================================
    # 第一阶段：联网搜索事件
    # =========================================================

    research_prompt = f"""
当前时间：{current_time}

请联网搜索并研究最近3个交易日内，可能显著影响以下A股板块的重要事件：

{sector_text}

你的任务不是预测股价，而是建立“事件 → 逻辑 → 板块影响”的研究资料。

搜索规则：

1. 必须使用联网搜索。
2. 优先最近3个交易日发生或公布的信息。
3. 优先寻找真正可能影响行业基本面、估值或市场情绪的事件。
4. 优先使用可靠来源：
   - 中国政府部门
   - 交易所
   - 上市公司公告
   - 官方统计机构
   - Reuters
   - Bloomberg
   - CNBC
   - 主流财经媒体
   - 行业权威媒体
5. 尽量避免：
   - 自媒体二次转载
   - 内容农场
   - 无来源传闻
   - 单纯股价涨跌新闻
6. 同一事件被多个媒体报道时，请合并，不要重复计算。
7. 每个板块最多挑选3个最重要事件。
8. 如果某板块没有明显的新事件，要明确写“暂无明显重大新增事件”。
9. 尽可能保留：
   - 新闻标题
   - 日期
   - 来源
   - URL
10. 不得虚构新闻、日期或来源。

对每个事件解释：

事件发生了什么
→ 为什么重要
→ 影响产业链哪个环节
→ 为什么可能影响该A股板块
→ 影响更偏短期情绪还是基本面

请输出一份详细的中文研究资料。

注意：
这是金融信息研究，不构成任何投资建议。
"""

    try:
        research_response = client.responses.create(
            model=model,

            instructions=(
                "你是一名严谨的A股行业研究员。"
                "你必须优先依赖联网搜索得到的真实信息，"
                "不要凭模型记忆虚构近期新闻。"
            ),

            input=research_prompt,

            tools=[
                {
                    "type": "web_search"
                }
            ],

            # 强制本次任务必须联网搜索
            tool_choice={
                "type": "web_search"
            },
        )

    except Exception as exc:
        raise RuntimeError(
            f"联网搜索失败：{exc}"
        ) from exc

    research_text = (
        research_response.output_text or ""
    ).strip()

    if not research_text:
        raise RuntimeError(
            "DeepSeek 联网搜索没有返回有效内容。"
        )

    # =========================================================
    # 第二阶段：把研究资料整理成 JSON
    # =========================================================

    system_prompt = """
你是一名A股事件驱动研究分析师。

你的任务：

只根据用户提供的“联网搜索研究资料”进行分析，
不得自行添加资料中不存在的近期新闻。

必须输出合法 JSON。

JSON 顶层格式必须是：

{
  "generated_at": "生成时间",
  "market_summary": "整体消息面简述",
  "sectors": [
    {
      "sector": "板块名称",
      "score": 0,
      "direction": "中性",
      "confidence": 0,
      "summary": "板块综合判断",
      "events": [
        {
          "title": "事件标题",
          "date": "YYYY-MM-DD或未知",
          "source": "来源",
          "url": "URL或空字符串",
          "importance": 1,
          "impact": "利好/利空/中性",
          "impact_type": "情绪/基本面/情绪+基本面",
          "transmission": [
            "第一步",
            "第二步",
            "第三步"
          ],
          "analysis": "事件影响解释"
        }
      ],
      "risks": [
        "可能使当前逻辑失效的因素"
      ]
    }
  ]
}

字段要求：

score：
-100 到 +100

解释：
+80 ~ +100 = 强烈正面事件冲击
+40 ~ +79  = 偏正面
+10 ~ +39  = 略偏正面
-9 ~ +9    = 中性
-39 ~ -10  = 略偏负面
-79 ~ -40  = 偏负面
-100 ~ -80 = 强烈负面

direction 必须从以下选择：
强利好
偏利好
略偏利好
中性
略偏利空
偏利空
强利空

confidence：
0 到 100

importance：
1 到 5

特别注意：

score 代表“当前事件冲击方向”，
不是股票未来涨跌预测。

没有明显事件的板块：
events 输出空数组，
score 接近0，
direction 为中性。

必须输出 JSON。
不要输出 Markdown。
不要输出 ```json。
不要输出 JSON 之外的任何文字。
"""

    user_prompt = f"""
以下是刚刚通过联网搜索得到的研究资料。

需要分析的板块：

{sector_text}

研究资料：

--------------------
{research_text}
--------------------

请严格根据以上资料生成 JSON 分析结果。
"""

    try:
        structured_response = (
            client.chat.completions.create(
                model=model,

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],

                response_format={
                    "type": "json_object"
                },

                max_tokens=7000,

                stream=False,

                extra_body={
                    "thinking": {
                        "type": "disabled"
                    }
                },
            )
        )

    except Exception as exc:
        raise RuntimeError(
            f"结构化分析失败：{exc}"
        ) from exc

    content = (
        structured_response
        .choices[0]
        .message
        .content
    )

    if not content:
        raise RuntimeError(
            "AI 返回了空的分析结果。"
        )

    # =========================================================
    # JSON 解析
    # =========================================================

    try:
        result = json.loads(content)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "AI 返回的 JSON 无法解析。"
        ) from exc

    # 保留原始检索文本
    # 后面做“新闻详情页”会用到
    result["_research_text"] = research_text

    return result
