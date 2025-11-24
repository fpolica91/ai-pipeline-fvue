from imp import reload
import gradio as gr
import os
import tempfile
import asyncio
from pathlib import Path
from utils.image_generator import ImageProcessorPipeline
from dotenv import load_dotenv

load_dotenv()

async def generate_descriptions_with_grok(image_files):
    """
    TODO: Implement Grok API call to generate descriptions for images
    For now, returns placeholder descriptions
    """
    descriptions = []
    for i, image_file in enumerate(image_files):
        # Placeholder - replace with actual Grok API call
        desc = f"A beautiful portrait of a person in image {i+1}"
        descriptions.append(desc)
    return descriptions

async def process_images_pipeline(reference_image, target_images, use_grok=False):
    """
    Main pipeline function that processes images
    """
    if not reference_image or not target_images:
        return "Error: Please upload both reference image and target images."
    
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save reference image
            ref_path = temp_path / "reference.jpg"
            reference_image.save(ref_path)
            
            # Save target images and create description files
            for i, target_img in enumerate(target_images):
                # Save image
                img_name = f"target_{i:03d}"
                img_path = temp_path / f"{img_name}.jpg"
                target_img.save(img_path)
                
                # Create description file
                desc_path = temp_path / f"{img_name}.txt"
                if use_grok:
                    # Generate description with Grok
                    descriptions = await generate_descriptions_with_grok([target_img])
                    description = descriptions[0]
                else:
                    # Use default description
                    description = "Portrait of a young woman with long straight jet-black hair parted in the center, piercing ice-blue eyes with sharp reflections, long dark lashes, and subtle liner, smooth flawless tanned skin with natural pores, subtle glossy nude-pink lips slightly parted, high cheekbones, confident direct gaze at viewer. Clean seamless white studio background, soft even frontal key light, subtle rim light, high-key lighting, no shadows on face."
                
                with open(desc_path, 'w') as f:
                    f.write(description)
            
            # Initialize and run the pipeline
            pipeline = ImageProcessorPipeline(
                source_dir=str(temp_path),
                reference_image_path=str(ref_path)
            )
            
            await pipeline.process_images()
            
            return f"Successfully processed {len(target_images)} images!"
            
    except Exception as e:
        return f"Error processing images: {str(e)}"

def run_pipeline(reference_image, target_images, use_grok):
    """
    Wrapper function to run async pipeline in Gradio
    """
    return asyncio.run(process_images_pipeline(reference_image, target_images, use_grok))

# Create Gradio interface
with gr.Blocks(title="AI Image Processing Pipeline") as demo:
    gr.Markdown("""
    # 🎨 AI Image Processing Pipeline
    
    Upload a reference image and multiple target images to generate face-swapped results using AI.
    
    ## How it works:
    1. **Upload Reference Image**: The face from this image will be swapped into target images
    2. **Upload Target Images**: Multiple images that will receive the reference face
    3. **Generate Descriptions**: Optionally use Grok AI to generate descriptions (or use default)
    4. **Process**: Run the Wavespeed AI pipeline to generate results
    """)
    
    with gr.Row():
        with gr.Column():
            reference_input = gr.Image(
                label="Reference Image", 
                type="pil",
                height=300
            )
            
            target_inputs = gr.File(
                label="Target Images", 
                file_count="multiple",
                file_types=["image"]
            )
            
            use_grok_checkbox = gr.Checkbox(
                label="Generate descriptions with Grok AI", 
                value=False
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
        inputs=[reference_input, target_inputs, use_grok_checkbox],
        outputs=[output_text]
    )
    
    # Example section
    gr.Markdown("""
    ## 💡 Tips:
    - Use high-quality reference images for better results
    - Target images should be portraits for best face swapping results
    - Processing time depends on number of images and Wavespeed API response
    - Results will be processed through the Wavespeed AI service
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False, # Set to True for public sharing
        reload=True,
    )