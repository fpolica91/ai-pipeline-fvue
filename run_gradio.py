#!/usr/bin/env python3
"""
Simple script to run the Gradio app
"""
import os
import sys
from gradio_app import demo

if __name__ == "__main__":
    print("🚀 Starting AI Image Processing Pipeline...")
    print("📝 Make sure your .env file has the following variables:")
    print("   - WAVESPEED_API_KEY")
    print("   - R2_BUCKET_NAME")
    print("   - R2_ACCOUNT_ID") 
    print("   - R2_ACCESS_KEY_ID")
    print("   - R2_SECRET_ACCESS_KEY")
    print()
    
    # Check for required environment variables
    required_vars = [
        "WAVESPEED_API_KEY",
        "R2_BUCKET_NAME", 
        "R2_ACCOUNT_ID",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file before running.")
        sys.exit(1)
    
    print("✅ All environment variables found!")
    print("🌐 Launching Gradio app...")
    print("📱 Access at: http://localhost:7860")
    print()
    
    demo.launch()