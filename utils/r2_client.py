

import os
from dotenv import load_dotenv
import aiohttp
import boto3
from botocore.config import Config
from termcolor import cprint
load_dotenv()
import mimetypes
import json
import asyncio
from tqdm import tqdm
import random
import time
from config import CACHE_DIR

class R2Client:
    def __init__(self, bucket_name: str = os.getenv('R2_BUCKET_NAME')):
        self.api_key = os.getenv("WAVESPEED_API_KEY")
        self.url = "https://api.wavespeed.ai/api/v3/bytedance/seedream-v4/edit"
        self.bucket_name = bucket_name
        self.r2_account_id = os.getenv('R2_ACCOUNT_ID')
        self.r2_access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        self.r2_secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.expires_in = 72000 
        self.r2_client = boto3.client(
            's3',
            endpoint_url=f'https://{self.r2_account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=self.r2_access_key_id,
            aws_secret_access_key=self.r2_secret_access_key,
            region_name='auto',
            config=Config(signature_version='s3v4')
        )
        self.cache_file = os.path.join(CACHE_DIR, 'r2_upload_cache.json')

    def _load_cache(self)->dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                cprint(f"Error loading cache: {e}", "red")
                return {}
        return {}
    
    def _save_cache(self, cache: dict):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            cprint(f"Error saving cache: {e}", "red")

    def _is_cache_valid(self, cache_entry: dict)->bool:
        if not cache_entry or 'timestamp' not in cache_entry or 'url' not in cache_entry:
            return False
        # get current time
        current_time = time.time()
        # when was the image uploaded?
        upload_time = cache_entry['timestamp']
        # when does it expire?
        expires_in = cache_entry.get('expires_in', self.expires_in)
        #  add a 5 minute buffer before expiration to be safe
        buffer = 300
        # check if time since uploaded is less than how long the image is supposed to be valid for
        return (current_time - upload_time) < (expires_in - buffer)
 
    async def get_presigned_url(self, file_name: str) -> bytes:
        try:
            return self.r2_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_name},
                ExpiresIn=self.expires_in
            )
        except Exception as e:
            cprint(f"Error downloading image: {e}", "red")
            raise Exception(str(e))

    async def upload_image(self, file_path: str)->str:
        try:
            file_name = os.path.basename(file_path)
            cache = self._load_cache()
            if file_name in cache and self._is_cache_valid(cache[file_name]):
                return cache[file_name]['url']
            file = open(file_path, "rb")
            content_type = mimetypes.guess_type(file_path)[0]

            self.r2_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    file_name,
                    ExtraArgs={
                        'ContentType': content_type
                    }
            )
            presigned_url = self.r2_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_name},
                ExpiresIn=self.expires_in
            )

            cache[file_name] = {
                'url': presigned_url,
                'timestamp': time.time(),
                'expires_in': self.expires_in
            }
            self._save_cache(cache)
            return presigned_url
        except Exception as e:
            cprint(f"Error uploading image: {e}", "red")
            raise Exception(str(e))
   

    
