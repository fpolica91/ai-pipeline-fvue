import gradio as gr
import tempfile
import asyncio
from pathlib import Path
from PIL import Image
from utils.image_generator import ImageProcessorPipeline
from dotenv import load_dotenv
from utils.grok import generate_seedream_prompt
from termcolor import cprint

load_dotenv()

async def generate_descriptions_with_grok(lia_image_path: str, target_image_paths: list[str]):
    """
    Generate descriptions for target images using Grok API
    """
    prompts = []
    for target_path in target_image_paths:
        prompt = await generate_seedream_prompt(target_path, lia_image_path)
        cprint(f"Prompt: {prompt}", "yellow")
        prompts.append(prompt)
    return prompts

async def process_images_pipeline(lia_image, target_images):
    """
    Main pipeline function that processes images
    """
    if not lia_image or not target_images:
        return "Error: Please upload both lia image and target images."
    
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary path for processing
            temp_path = Path(temp_dir)
            # Save lia image
            lia_path = temp_path / "lia.jpg"
            lia_image.save(lia_path)
            # Save target images (convert from file uploads to PIL Images)
            for i, target_file in enumerate(target_images):
                target_img = Image.open(target_file.name)
                img_name = f"target_{i:03d}"
                img_path = temp_path / f"{img_name}.jpg"
                target_img.save(img_path)

            # Generate all descriptions at once
            target_paths = [str(temp_path / f"target_{i:03d}.jpg") for i in range(len(target_images))]
            descriptions = await generate_descriptions_with_grok(str(lia_path), target_paths)
            
            # Write description files
            for i, description in enumerate(descriptions):
                img_name = f"target_{i:03d}"
                desc_path = temp_path / f"{img_name}.txt"
               
                with open(desc_path, 'w') as f:
                    f.write(description)
            
            # Initialize and run the pipeline
            pipeline = ImageProcessorPipeline(
                source_dir=str(temp_path),
                lia_image_path=str(lia_path)
            )
            
            await pipeline.process_images()
            
            return f"Successfully processed {len(target_images)} images!"
            
    except Exception as e:
        return f"Error processing images: {str(e)}"

def run_pipeline(lia_image, target_images):
    """
    Wrapper function to run async pipeline in Gradio
    """
    return asyncio.run(process_images_pipeline(lia_image, target_images))

# Create Gradio interface
with gr.Blocks(title="AI Image Processing Pipeline") as demo:
    gr.Markdown("""
    # 🎨 AI Image Processing Pipeline
    
    Upload a lia image and multiple target images to generate face-swapped results using AI.
    
    ## How it works:
    1. **Upload Lia Image**: The face from this image will be swapped into target images
    2. **Upload Target Images**: Multiple images that will receive the lia face
    3. **Generate Descriptions**: Use Grok AI to generate descriptions automatically
    4. **Process**: Run the Wavespeed AI pipeline to generate results
    """)
    
    with gr.Row():
        with gr.Column():
            lia_input = gr.Image(
                label="Lia Image", 
                type="pil",
                height=300
            )
            
            target_inputs = gr.File(
                label="Target Images", 
                file_count="multiple",
                file_types=["image"]
            )
            
            process_btn = gr.Button("🚀 Start Processing", variant="primary", size="lg")
        
        with gr.Column():
            output_text = gr.Textbox(
                label="Processing Results",
                lines=10,
                max_lines=20
            )
    
    # Event handlers
    process_btn.click(
        fn=run_pipeline,
        inputs=[lia_input, target_inputs],
        outputs=[output_text]
    )
    
    # Example section
    gr.Markdown("""
    ## 💡 Tips:
    - Use high-quality lia images for better results
    - Target images should be portraits for best face swapping results
    - Descriptions are automatically generated using Grok AI
    - Processing time depends on number of images and Wavespeed API response
    - Results will be processed through the Wavespeed AI service
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False, # Set to True for public sharing
    )