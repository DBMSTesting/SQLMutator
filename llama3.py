import openai
import pandas as pd
import os
import re
import time
import json


from openai import OpenAI
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

def llama_api(test_prompt):
    client = OpenAI(
        api_key='sk-SBROtPYFofllyAcp3dF7745b26D54bAbA9DaE174766fD493',
        base_url="https://gptgod.cloud/v1",
        )
    

    # print(prompt)
    response = client.chat.completions.create(
    model="codellama-70b-instruct",
    messages=[
        {
        "role": "user",
        "content": test_prompt
        }
    ]
    )
   

    print(response.choices[0].message.content)
    return response
