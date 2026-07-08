import os
from flask import Flask, request, abort
from google import genai
from google.genai import types
from linebot.v2 import WebhookHandler
from linebot.v2.exceptions import InvalidSignatureError
from linebot.v2.webhooks import MessageEvent, TextMessageContent
from linebot.v2.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

# ==========================================
# 👑 【設定エリア】暗号を貼り付ける
# ==========================================
LINE_CHANNEL_ACCESS_TOKEN = "あなたのLINEチャネルアクセストークン"
LINE_CHANNEL_SECRET = "あなたのLINEチャネルシークレット"
GEMINI_API_KEY = "あなたのGEMINIのAPIキー"

# ==========================================
# ⚙️ システム初期化
# ==========================================
app = Flask(__name__)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
あなたはユーザーに仕える優秀なAI軍師団（クロエとエルムの2人体制）です。
以下の掛け合いを意識して、一つの返信文を作ってください。

【クロエ（18才・ツンデレ軍師）】
・口調：少し強気、ツンデレ、〜よ、〜なさい、フン。
・役割：真面目に戦術を分析し、ユーザーを叱咤激励する。根は優しい。

【エルム（17才・ギャル副官）】
・口調：ギャル風、〜じゃん、〜だよー☆、ウケる。
・役割：場を盛り上げる、ポジティブ、クロエをからかう。
"""

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
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=800
            )
        )
        reply_text = response.text
    except Exception as e:
        reply_text = f"【軍師団伝令】本陣通信エラー: {str(e)}"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

# Supabase Compute用（Gunicornが自動で呼び出します）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
