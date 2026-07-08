import os
from flask import Flask, request, abort
from google import genai
from linebot.v2 import WebhookHandler
from linebot.v2.exceptions import InvalidSignatureError
from linebot.v2.webhooks import MessageEvent, TextMessageContent
from linebot.v2.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage

app = Flask(__name__)

# ★コードには何も書かない！実行時に環境変数を読み込む仕組み
TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
SECRET = os.environ.get("LINE_CHANNEL_SECRET")
API_KEY = os.environ.get("GEMINI_API_KEY")

configuration = Configuration(access_token=TOKEN)
handler = WebhookHandler(SECRET)
client = genai.Client(api_key=API_KEY)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_message
        )
        reply_text = response.text
    except Exception as e:
        reply_text = "分析中にエラーが発生しました。"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
