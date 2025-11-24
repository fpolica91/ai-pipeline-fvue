from openai import OpenAI
from config import GROK_API_KEY
import base64

client = OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
)

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_seedream_prompt(lia_target_path: str, reference_image_path: str) -> str:
    reference_b64 = encode_image(reference_image_path)
    lia_target_b64 = encode_image(lia_target_path)

    response = client.chat.completions.create(
    model="grok-4",
    temperature=0.3,
    messages=[
        {"role": "system", "content": "You are an expert at writing perfect Seedream 4.0 img2img prompts. Always keep the exact pose, clothing, lighting, and background from the reference image. Only replace the face and body traits with the exact traits from the target image."},
        {"role": "user", "content": [
        {"type": "text", "text": """
        Generate a concise Seedream 4.0 img2img prompt that:
        - Keeps 100% of the pose, outfit, lighting, background, and body proportions from the first image
        - Swaps ONLY the face and these exact traits from the second image:
        • 21 year old woman
        • striking light blue eyes
        • fair flawless skin with no freckles
        • subtle natural makeup, neutral lips
        • long dark brown hair (high messy bun ONLY if reference already has one)
        • detailed rose tattoo sleeve on left forearm + rose tattoo on right upper arm
        • gold bangles and rings
        • long white nails
        • very large full round breasts
        • oiled glistening skin
        • perfect symmetrical youthful face
        End with: photorealistic, ultra-detailed skin and tattoo texture, 8k fashion portrait
        """},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{reference_b64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{lia_target_b64}"}},
                ]}
            ],
            max_tokens=500
        )

    return response.choices[0].message.content.strip()