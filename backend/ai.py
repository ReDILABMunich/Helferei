import os
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

load_dotenv()

# Client for groq
# client = Groq(
#     api_key=os.environ["GROQ_API_KEY"]
# )

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

# Function for groq ai
# def askAI(prompt: str) -> str:
#     response = client.chat.completions.create(
#         model="openai/gpt-oss-20b",
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt,
#             }
#         ],
#     )
#
#     return response.choices[0].message.content

def askAI(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text