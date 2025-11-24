import sqlite3
from config import DB_PATH
from uuid import uuid4
from termcolor import cprint
import aiosqlite
from typing import Optional, TypedDict


class Job(TypedDict):
    lia_image_key: str
    target_image_key: str
    wavespeed_result_url: Optional[str]
    r2_image_key: Optional[str]
    r2_presigned_url: Optional[str]
    status: str


class DatabaseClient:
    async def create_job(self, job: Job) -> str:
        try:
            job_id = str(uuid4())
            async with aiosqlite.connect(DB_PATH) as conn:
                await conn.execute('''
                    INSERT INTO jobs (id, lia_image_key, target_image_key, wavespeed_result_url, r2_image_key, r2_presigned_url, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending')
                ''', (job_id, job.get('lia_image_key'), job.get('target_image_key'), job.get('wavespeed_result_url'), job.get('r2_image_key'), job.get('r2_presigned_url')))
                await conn.commit()
            return job_id
        except Exception as e:
            cprint(f"Error creating job: {e}", "red")
            return None
    
    async def update_job(self, job_id: str, job: Job) -> bool:
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                await conn.execute('''
                    UPDATE jobs SET wavespeed_result_url = ?, r2_image_key = ?, r2_presigned_url = ?, status = ? WHERE id = ?
                ''', (job.get('wavespeed_result_url'), job.get('r2_image_key'), job.get('r2_presigned_url'), job.get('status'), job_id))
                await conn.commit()
            return True
        except Exception as e:
            cprint(f"Error updating job: {e}", "red")
            return False

    async def get_job(self, job_id: str) -> Optional[Job]:
        try:
            async with aiosqlite.connect(DB_PATH) as conn:
                result = await conn.execute('''
                    SELECT * FROM jobs WHERE id = ?
                ''', (job_id,))
                row = await result.fetchone()
                return row    
        except Exception as e:
            cprint(f"Error getting job: {e}", "red")
            return None
