from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import openai

# 設定 API key（從 Render 環境變數讀取）
openai.api_key = os.environ.get("OPENAI_API_KEY")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text

    # 呼叫 GPT 模型生成回覆
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 或 gpt-4
            messages=[
                {"role": "system", "content": "你是個友善的 LINE 機器人。"},
                {"role": "user", "content": user_msg}
            ]
        )
        ai_reply = response.choices[0].message['content']
    except Exception as e:
        ai_reply = f"AI 回覆時出錯：{str(e)}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply)
    )
    
app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"你說了：{msg}")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
