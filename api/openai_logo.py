import os
import openai
from dotenv import load_dotenv
from io import BytesIO
import base64

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def create_logo(show):
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in .env file")
    prompt = f"Generate a unique, modern TV show logo for '{show}'. Transparent background. No words, just a clever graphic. Vaporwave/cyberpunk flavor. Realistic, professional, bold, suitable for an actual streaming service."
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }
            ],
            text={"format": {"type": "text"}},
            reasoning={},
            tools=[
                {
                    "type": "image_generation",
                    "size": "1024x1024",
                    "quality": "high",
                    "output_format": "png",
                    "background": "transparent",
                    "moderation": "auto",
                }
            ],
            temperature=1,
            max_output_tokens=2048,
            top_p=1,
            store=True,
        )
        image_b64 = response.output[0].result
        img_bytes = BytesIO(base64.b64decode(image_b64))
        logo_file = f"data/media/show_logos/{show}_logo.png"
        with open(logo_file, "wb") as f:
            f.write(img_bytes.getbuffer())
        img_bytes.seek(0)
        return img_bytes, logo_file
    except Exception as e:
        return None, None
