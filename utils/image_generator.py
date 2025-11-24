

import os
from dotenv import load_dotenv
import aiohttp
from termcolor import cprint
load_dotenv()
from .r2_client import R2Client




class ImageProcessorPipeline:
    """
    Class for swapping face of reference into target image
    """

    def __init__(self, source_dir: str, reference_image_path: str) -> None:
        self.api_key = os.getenv("WAVESPEED_API_KEY")
        self.url = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4/edit"
        self.source_dir = source_dir
        self.r2_client = R2Client()
        self.reference_image_path = reference_image_path
        


    async def upload_file(self, file_path: str) -> str:
        try:
            return await self.r2_client.upload_image(file_path)
        except Exception as e:
            print(str(e))
            raise Exception(str(e))
            

    async def get_files(self) -> list[str]:
        dataset = sorted(os.listdir(self.source_dir))
        txt_files = set(f for f in dataset if f.endswith(".txt"))
        image_files = set(f for f in dataset if f.endswith((".jpg", ".jpeg", ".png")))
        dataset_list = []
        for image_file in image_files:
            file_name = image_file.split(".")[0]
            description_file = f"{file_name}.txt"
            if description_file not in txt_files:
                cprint(f"Skipping {image_file} because it does not have a description file", "red")
                continue
            dataset_list.append((
                file_name,
                await self.upload_file(os.path.join(self.source_dir, image_file)),
                open(os.path.join(self.source_dir, description_file), "r").read()
            ))
        return dataset_list


    async def process_images(self) -> None:
        responses = []
        reference_image = await self.upload_file(self.reference_image_path)
        files = await self.get_files()
        for file_name, image, description in files:
            cprint(f"Processing {file_name}...", "yellow")
            try:
                payload = {
                    "enable_base64_output": False,
                    "enable_sync_mode": False,
                    "images": [
                        image,
                        reference_image
                    ],
                    "prompt": description,
                    "size": "3072*4096"
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.url, json=payload, headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    }) as response:
                        if response.status == 200:
                            resp_data = await response.json()
                            responses.append({
                                "data": resp_data,
                                "file_name": file_name,
                            })
                        else:
                            text = await response.text()
                            print(f"Error: {response.status} {text}")
                
                            
            
            except Exception as e:
                print(f"Error processing image: {e}")
             




                