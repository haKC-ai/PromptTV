import openai
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def compose_scene(scene_context):
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": scene_context}],
                }
            ],
            text={"format": {"type": "text"}},
            temperature=1,
            max_output_tokens=1024,
            top_p=1,
            store=False,
        )
        #print("DEBUG:", response)
        #print("DEBUG OUTPUT:", response.output)
        #return str(response.output[0])
        return response.output[0].content[0].text.strip()


    except Exception as e:
        return f"[Error composing scene: {e}]"
