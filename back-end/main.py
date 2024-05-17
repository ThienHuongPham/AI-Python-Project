import uvicorn
from fastapi import FastAPI
from openai import OpenAI
from setup.agents import submit_tool_outputs
import os
import time
from pydantic import BaseModel

openai_api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

assistant_id = "asst_Rgree1iEMtW0zImmE9mjjnNJ"

app = FastAPI()

class MessageInput(BaseModel):
    text: str
    thread_id: str


@app.post("/chat")
async def main(message_input: MessageInput):
    client.beta.threads.messages.create(
        thread_id=message_input.thread_id,
        role="user",
        content=message_input.text
    )
    run = client.beta.threads.runs.create(
        thread_id=message_input.thread_id,
        assistant_id=assistant_id
    )

    while run.status not in ['completed', 'failed']:
        print(run.status)
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=message_input.thread_id, run_id=run.id)
        if run.status == 'requires_action':
            run = submit_tool_outputs(message_input.thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)

    messages = client.beta.threads.messages.list(message_input.thread_id)
    return messages.data[0].content[0].text.value



if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=4000)
