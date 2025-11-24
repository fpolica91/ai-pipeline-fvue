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
    reference_b64 = encode_image(reference_image_path)  # ← POSE donor
    lia_b64       = encode_image(lia_target_path)      # ← FACE donor

    response = await client.chat.completions.create(
        model="grok-4",
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are a strict Seedream 4.0 img2img prompt writer. FIRST image = REFERENCE (keep 100% pose, exact clothing, lighting, background). SECOND image = LIA TARGET (only swap face + traits that are actually visible in the reference). NEVER invent or force hidden features."},
            {"role": "user", "content": [
                {"type": "text", "text": """
Image 1 = REFERENCE → keep 100% pose, exact clothing, lighting, background, body proportions.
Image 2 = LIA TARGET → ONLY apply these traits IF they are visible in the reference image:
• 21 year old woman
• striking light blue eyes
• fair flawless skin with no freckles
• subtle natural makeup, neutral lips
• long dark brown hair (high messy bun ONLY if reference already has one)
• detailed rose tattoo sleeve on left forearm ONLY if left forearm is visible
• rose tattoo on right upper arm ONLY if right upper arm/shoulder is visible
• gold bangles and rings ONLY if wrists/hands are visible
• long white nails ONLY if hands are visible
• very large full round breasts (always apply)
• oiled glistening skin (always apply)
• perfect symmetrical youthful face (always apply)

If any tattoo/jewelry area is covered by clothing, DO NOT mention it at all.
Output ONLY the final Seedream img2img prompt. End with: photorealistic, ultra-detailed skin and tattoo texture, 8k fashion portrait
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{reference_b64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{lia_b64}"}},
            ]}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()