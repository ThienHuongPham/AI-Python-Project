import chainlit as cl
import requests
from openai import OpenAI
import os

openai_api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

@cl.on_chat_start
def on_chat_start():
    thread = client.beta.threads.create()
    cl.user_session.set("thread_id", thread.id)


@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")

    params = {
        "text": message.content,
        "thread_id": thread_id
    }

    url = 'http://localhost:4000/chat'

    x = requests.post(url, json=params)

    await cl.Message(content=x.text).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit("app.py")