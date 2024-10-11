import os
import configparser
from flask import Flask, request, abort
import sys
import os
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    PostbackAction,
    MessageAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction     
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent
)

config = configparser.ConfigParser()
config.read('config.ini')

token = config['Line']['TOKEN']      
if token is None:
    print("Specify ['Line']['TOKEN']   as environment variable.")
    sys.exit(1)
secret = config['Line']['SECRET']      
if token is None:
    print("Specify ['Line']['SECRET']   as environment variable.")
    sys.exit(1)

user_action = {}
# configuration = Configuration(access_token=os.getenv('token'))
# line_handler = WebhookHandler(os.getenv('secret'))

configuration = Configuration(access_token=token)
handler = WebhookHandler(secret)

app = Flask(__name__)

# LINE BOT的 Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    # 確認請求來自LINE伺服器
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

import llm_test

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global user_action

    with ApiClient(configuration) as api_client:        
        line_bot_api = MessagingApi(api_client)  
    user_message = event.message.text
    print(user_message)
    llm=llm_test.LLMOperation()
    if event.source.user_id in user_action:
        if user_action[event.source.user_id] == '1':
            print("Action: ", user_action)
            resp=llm.domath(user_message)['answer'].replace('Answer: ','').replace('*','')
            if resp is not None:     
                try:
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=resp)]
                        )
                    )
                except Exception as e:
                    app.logger.error(f"Error replying message: {str(e)}")
            user_action.update({event.source.user_id: ''})
        elif user_action[event.source.user_id] == '2':
            print("Action: ", user_action)
            resp=llm.translate2eng(user_message)
            if resp is not None:     
                try:
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=resp)]
                        )
                    )
                except Exception as e:
                    app.logger.error(f"Error replying message: {str(e)}")
            user_action.update({event.source.user_id: ''})
        elif user_action[event.source.user_id] == '3':
            print("Action: ", user_action)
            resp=llm.japan_sappro(user_message).replace('*','')
            if resp is not None:     
                try:
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text=resp)]
                        )
                    )
                except Exception as e:
                    app.logger.error(f"Error replying message: {str(e)}")
            user_action.update({event.source.user_id: ''})
        elif  user_action[event.source.user_id] == '4':
            print("Action: ", user_action)
            resp=llm.normalqry(user_message).replace('*','')
            try:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=resp)]
                    )
                )
            except Exception as e:
                app.logger.error(f"Error replying message: {str(e)}")
            user_action.update({event.source.user_id: ''})
        else:
            SendMyDefaulQuickReply(event)
            
    else:
        SendMyDefaulQuickReply(event)


@handler.add(PostbackEvent)
def handle_postback(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        postback_data = event.postback.data
        if postback_data == '1':
            user_action[event.source.user_id] = '1'
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='請輸入數學運算式，即可得到計算結果。例如：18的平方根是多少？')]
                )
            )
        elif postback_data == '2':
            user_action[event.source.user_id] = '2'
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='請輸入您想翻譯成英文的中文句子')]
                )
            )
        elif postback_data == '3':
            user_action[event.source.user_id] = '3'
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='我是北海道的自助旅行小幫手,有什麼能幫上您的嗎？')]
                )
            )
        elif postback_data == '4':
            user_action[event.source.user_id] = '4'
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='您想聊啥呢?')]
                )
            )

def SendMyDefaulQuickReply(event):
    quickReply = QuickReply(
        items=[
            QuickReplyItem(
                action=PostbackAction(
                    label="數學問題",
                    data="1",
                    display_text="數學問題"
                ),
                # image_url=postback_icon
            ),
            QuickReplyItem(
                action=PostbackAction(
                    label="中翻英",
                    data="2",
                    display_text="中翻英"
                ),
                # image_url=message_icon
            ),
            QuickReplyItem(
                action=PostbackAction(
                    label="北海道自由行諮詢",
                    data="3",
                    display_text="北海道自由行諮詢"
                ),
                # image_url=date_icon
            ),
            QuickReplyItem(
                action=PostbackAction(
                    label="純閒聊,亂哈拉",
                    data="4",
                    display_text="純閒聊,亂哈拉"
                ),
                #  image_url=time_icon
            ),
        ]
    )
    with ApiClient(configuration) as api_client:        
        line_bot_api = MessagingApi(api_client)  
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text='您好,我是國生家的AI小幫手,需什麼樣的協助呢? 請選擇項目: ',
                        quick_reply=quickReply
                    )]
                )
            )
        except Exception as e:
            app.logger.error(f"Error replying message: {str(e)}")



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
