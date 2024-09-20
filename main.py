# -*- coding: utf-8 -*-

import logging
import os
import asyncio
import telegram
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters
import g4f

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

chat_language = os.getenv("INIT_LANGUAGE", default="zh")  # amend here to change your preset language
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default=20))
LANGUAGE_TABLE = {
    "zh": "哈囉！",
    "en": "Hello!",
    "jp": "こんにちは"
}

class Prompts:
    def __init__(self):
        self.msg_list = []
        self.msg_list.append(f"AI:{LANGUAGE_TABLE[chat_language]}")

    def add_msg(self, new_msg):
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.msg_list.append(new_msg)

    def remove_msg(self):
        self.msg_list.pop(0)

    def generate_prompt(self):
        return '\n'.join(self.msg_list)

class ChatGPT:
    def __init__(self):
        self.prompt = Prompts()
        self.model = "gpt-3.5-turbo"
        self.provider = g4f.Provider.Pizzagpt

    async def get_response(self):
        try:
            # Simulate typing effect
            await bot.send_chat_action(chat_id, 'typing')
            await asyncio.sleep(0.7)  # Simulate delay for typing effect

            chat_history = [{"role": "user", "content": msg} for msg in self.prompt.msg_list]
            response = await g4f.ChatCompletion.create_async(
                model=self.model,
                messages=chat_history,
                provider=self.provider,
            )

            chat_gpt_response = response
        except Exception as e:
            print(f"{self.provider.__name__}:", e)
            chat_gpt_response = "Извините, произошла ошибка."

        self.prompt.add_msg(chat_gpt_response)
        return chat_gpt_response

    def add_msg(self, text):
        self.prompt.add_msg(text)

telegram_bot_token = str(os.getenv("TELEGRAM_BOT_TOKEN"))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=telegram_bot_token)

@app.route('/callback', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
    return 'ok'

async def reply_handler(bot, update):
    """Reply message."""
    chatgpt = ChatGPT()
    chatgpt.add_msg(update.message.text)  # Human's question
    ai_reply_response = await chatgpt.get_response()  # ChatGPT's answer
    
    await update.message.reply_text(ai_reply_response)  # Reply with AI's text

# New a dispatcher for bot
dispatcher = Dispatcher(bot, None)

# Add handler for handling message, particularly handle text messages.
dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)
