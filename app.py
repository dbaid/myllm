import os

from flask import Flask, request, abort
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
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)



user_action = {}
configuration = Configuration(access_token=os.getenv('token'))
line_handler = WebhookHandler(os.getenv('secret'))

app = Flask(__name__)

# LINE BOT的 Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    # 確認請求來自LINE伺服器
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

import llm_test
def get_line_bot_api():  
    with ApiClient(configuration) as api_client:        
        line_bot_api = MessagingApi(api_client) 
    return line_bot_api  

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global user_action
    # line_bot_api = get_line_bot_api() 
    with ApiClient(configuration) as api_client:        
        line_bot_api = MessagingApi(api_client)  
    user_message = event.message.text
    print(user_message)
    llm=llm_test.LLMOperation()
    if user_message=='@math':
        # action = '1'
        user_action[event.source.user_id] = '1'
        # print("Action: ", user_action)
        showmath(event)
    elif user_message=='@translate2eng':
        user_action.update({event.source.user_id: '2'})
        # print("Action: ", user_action)
        showtrans2eng(event)
    elif user_message=='@sappro':
        user_action.update({event.source.user_id: '3'})
        # print("Action: ", user_action)
        showtsappro(event)    
    else:
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
            else:
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
                    app.logger.error(f"Error replying message--final: {str(e)}")
        else:
            user_action.update({event.source.user_id: ''})
            print("Without 圖文選單: ", user_action)
            resp=llm.normalqry(user_message).replace('*','')
            try:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=resp)]
                    )
                )
            except Exception as e:
                app.logger.error(f"Error replying message--final: {str(e)}")

def showmath(event):
    global user_action
    line_bot_api = get_line_bot_api()
    print("Action: ", user_action)
    text1 = '請輸入數學運算式，即可得到計算結果。例如：18的平方根是多少？'
    try:
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text1)]
            )
        )
    except Exception as e:
        app.logger.error(f"Error replying message: {str(e)}")

def showtrans2eng(event):
    global user_action
    line_bot_api = get_line_bot_api()
    print("Action: ", user_action)
    text1 = '請輸入您想翻譯成英文的中文句子'
    try:
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text1)]
            )
        )
    except Exception as e:
        app.logger.error(f"Error replying message: {str(e)}")

def showtsappro(event):
    global user_action
    line_bot_api = get_line_bot_api()
    print("Action: ", user_action)
    text1 = '我是北海道的自助旅行小幫手,有什麼能幫上您的嗎？'
    try:
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text1)]
            )
        )
    except Exception as e:
        app.logger.error(f"Error replying message: {str(e)}")

# def get_line_bot_api():  
#     with ApiClient(configuration) as api_client:  
#         line_bot_api = MessagingApi(api_client)  
      
#     return line_bot_api  

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
