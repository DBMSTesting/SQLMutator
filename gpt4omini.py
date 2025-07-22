import openai
import pandas as pd
import os
import re
import time


from openai import OpenAI
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

def gpt_api(prompt):
    client = OpenAI(
        api_key='sk-Op04f7VYp11zdZxSBbFcD5Cb4a7f4315A8C884AaC0D35c5e',
        base_url="https://gptgod.cloud/v1",
        )

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": prompt
        }
    ],
    temperature=0.7,
    max_tokens=4096,
    top_p=1
    )

    print(response.choices[0].message.content)
    return response

gpt_api("hello")
