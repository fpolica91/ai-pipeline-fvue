from openai import AsyncOpenAI
from config import GROK_API_KEY
from termcolor import cprint
import base64

client = AsyncOpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

async def generate_seedream_prompt(reference_image_path: str, lia_target_path: str) -> str:
    reference_b64 = encode_image(reference_image_path)  # ← this is the POSE donor
    lia_b64       = encode_image(lia_target_path)      # ← this is the FACE donor

    response = await client.chat.completions.create(
        model="grok-4",
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are an expert Seedream 4.0 img2img prompt writer. The FIRST image is the REFERENCE (keep pose, clothing, lighting, background 100%). The SECOND image is LIA TARGET (only take her face and specific traits). NEVER describe the target image's pose or outfit."},
            {"role": "user", "content": [
                {"type": "text", "text": """
Image 1 = REFERENCE → keep 100% pose, exact clothing, lighting, background, body proportions.
Image 2 = LIA TARGET → only replace with these exact traits:
• 21 year old woman
• striking light blue eyes
• fair flawless skin no freckles
• subtle natural makeup, neutral lips
• long dark brown hair (high messy bun ONLY if reference already has one)
• detailed rose tattoo sleeve on left forearm + rose tattoo on right upper arm
• gold bangles and rings
• long white nails
• very large full round breasts
• oiled glistening skin
• perfect symmetrical youthful face

Output ONLY the final Seedream img2img prompt. End with: photorealistic, ultra-detailed skin and tattoo texture, 8k fashion portrait
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{reference_b64}"}},  # ← POSE
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{lia_b64}"}},       # ← FACE
            ]}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()