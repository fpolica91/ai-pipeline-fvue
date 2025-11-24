

import os
from dotenv import load_dotenv
import aiohttp
from termcolor import cprint
load_dotenv()
from .r2_client import R2Client
from database.client import DatabaseClient, Job
import tempfile
import aiofiles
import asyncio


class ImageProcessorPipeline:
    """
    Class for swapping face of lia into target image
    """

    def __init__(self, source_dir: str, lia_image_path: str) -> None:
        self.api_key = os.getenv("WAVESPEED_API_KEY")
        self.url = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4/edit"
        self.source_dir = source_dir
        self.r2_client = R2Client()
        self.lia_image_path = lia_image_path
        self.database_client = DatabaseClient()
        


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
        
        # Get lia image filename to exclude it from target processing
        lia_filename = os.path.basename(self.lia_image_path)
        
        dataset_list = []
        for image_file in image_files:
            # Skip the lia image - it's not a target image
            if image_file == lia_filename:
                continue
                
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



    async def create_job(self, job: Job) -> str:
        try:
            return await self.database_client.create_job(job)
        except Exception as e:
            print(f"Error creating job: {e}")
            return None

    async def download_and_upload_result(self, completed_data: dict) -> str:
        try:
            outputs = completed_data.get("data", {}).get("outputs", [])
            if not outputs:
                cprint(f"No outputs found", "red")
                return None, None
            output = outputs[0]


            async with aiohttp.ClientSession() as session:
                async with session.get(output) as response:
                    if response.status == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as temp_file:
                            temp_path = temp_file.name
                            async with aiofiles.open(temp_path, "wb") as f:
                                await f.write(await response.read())
                        r2_url = await self.r2_client.upload_image(temp_path)
                        r2_key = os.path.basename(temp_path)
                        os.unlink(temp_path)
                        return r2_key, r2_url
                    else:
                        print(f"Error downloading result: {response.status}")
                        return None

        except Exception as e:
            print(f"Error downloading and uploading result: {e}")
            return None

    async def update_job(self, job_id: str, job: Job) -> bool:
        try:

            return await self.database_client.update_job(job_id, job)
        except Exception as e:
            print(f"Error updating job: {e}")
            return False


    async def poll_result(self, url: str, job_id: str) -> tuple[str, str]:
        while True:
            await asyncio.sleep(3)
            async with aiohttp.ClientSession() as poll_session:
                async with poll_session.get(url, headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }) as poll_response:
                    if poll_response.status == 200:
                        data = await poll_response.json()
                        status = data.get("data", {}).get("status", None)
                        cprint(f"Status: {status}", "yellow")
                        if status == "completed":
                            cprint(f"Result completed", "green")
                            r2_key, r2_url = await self.download_and_upload_result(data)
                            await self.update_job(job_id, {
                                "wavespeed_result_url": url,
                                "r2_image_key": r2_key,
                                "r2_presigned_url": r2_url,
                                "status": "completed"
                            })
                            return r2_key, r2_url
                    else:
                        text = await poll_response.text()
                        print(f"Error: {poll_response.status} {text}")



    async def process_single_image(self, file_name: str, image: str, description: str, lia_image: str, lia_image_key: str) -> tuple[str, str]:
        try:
            payload = {
                    "enable_base64_output": False,
                    "enable_sync_mode": False,
                    "images": [
                        image,
                        lia_image
                    ],
                    "prompt": description,
                    "size": "3072*4096"
                }
            job_id = await self.create_job({
                    "lia_image_key": lia_image_key,
                    "target_image_key": file_name,
                    "wavespeed_result_url": None,
                    "r2_image_key": None,
                    "r2_presigned_url": None,
                    "status": "pending"
                })
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=payload, headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                }) as response:
                    if response.status == 200:
                        resp_data = await response.json()
                        url = resp_data.get("data", {}).get("urls", {}).get("get", None)
                        await self.poll_result(url, job_id)
                
            return job_id
        except Exception as e:
            print(f"Error processing single image: {e}")
            return None

    async def process_images(self) -> list[str]:
        lia_image = await self.upload_file(self.lia_image_path)
        lia_image_key = os.path.basename(self.lia_image_path)
        tasks = []
        files = await self.get_files()
        for file_name, image, description in files:
            cprint(f"Processing {file_name}...", "yellow")
            try:
                tasks.append(self.process_single_image(file_name, image, description, lia_image, lia_image_key))
            except Exception as e:
                print(f"Error processing image: {e}")
        results = await asyncio.gather(*tasks)
        return results




                