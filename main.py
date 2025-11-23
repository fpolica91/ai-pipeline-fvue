from utils.image_generator import ImageGenerator
import asyncio
from pathlib import Path
from argparse import ArgumentParser

BASE_DIR = Path(__file__).resolve().parent.parent


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--source_dir", type=str, required=True)
