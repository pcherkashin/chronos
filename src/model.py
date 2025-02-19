import os
from dotenv import load_dotenv
import dashscope
from http import HTTPStatus
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


def query_model(model: str, raw_prompt: str):
    if 'qwen' in model:
        responses = query_qwen(model, raw_prompt)
    elif 'gpt' in model:
        responses = query_gpt(model, raw_prompt)
    return responses


def query_qwen(model: str, raw_prompt: str):
    response = dashscope.Generation.call(
        api_key=DASHSCOPE_API_KEY,
        model=model,
        prompt=raw_prompt,
        result_format='message',
        use_raw_prompt=True
    )
    if response.status_code == HTTPStatus.OK:
        return response.output.choices[0].message.content
    else:
        err = 'Error code: %s, error message: %s' % (
            response.code,
            response.message,
        )
        return err


def query_gpt(model: str, raw_prompt: str):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": raw_prompt}]
    )
    return response.choices[0].message.content