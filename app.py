from flask import Flask, request, abort
from linebot.v3.webhooks import WebhookParser
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    ReplyMessageRequest,
)
from linebot.v3.webhooks.models import MessageEvent, TextMessageContent
from openai import OpenAI
import os
import json

# 讀取環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 初始化 LINE Messaging API 與 Webhook Parser
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 建立 Flask 應用
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        events = parser.parse(body, signature)
    except Exception as e:
        print(f"Webhook 解析錯誤：{e}")
        abort(400)

    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)

        for event in events:
            if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
                user_msg = event.message.text

                # 呼叫 OpenAI 取得回覆
                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "你是一個友善的 LINE 聊天機器人"},
                            {"role": "user", "content": user_msg}
                        ]
                    )
                    ai_reply = response.choices[0].message.content.strip()
                except Exception as e:
                    ai_reply = f"AI 回覆錯誤：{str(e)}"

                # 回覆用戶訊息
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=ai_reply)]
                    )
                )

    return "OK"

# 執行應用（Render 或本機）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
