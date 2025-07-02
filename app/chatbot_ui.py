import gradio as gr
import requests
import os
import glob
from datetime import datetime

def get_latest_files():
    """Get the latest generated image and GLB files"""
    output_dir = os.path.join(os.path.dirname(__file__), "output_3d_model")
    
    latest_image = None
    latest_glb = None
    
    if os.path.exists(output_dir):
        # Get all PNG files and find the latest one
        png_files = glob.glob(f"{output_dir}/*.png")
        if png_files:
            latest_image = max(png_files, key=os.path.getmtime)
        
        # Get all GLB files and find the latest one
        glb_files = glob.glob(f"{output_dir}/*.glb")
        if glb_files:
            latest_glb = max(glb_files, key=os.path.getmtime)
    
    return latest_image, latest_glb

def process_text_to_3d(username, input_text):
    """Process the text to 3D model request"""
    
    # Validation
    if not input_text.strip():
        return "Please enter some text.", None, None
    
    if not username.strip():
        return "Please enter a username.", None, None
    
    try:
        # Prepare the request payload
        payload = {
            "attachments": [],
            "prompt": input_text,
            "username": username
        }
        
        # Make request to the server
        response = requests.post(
            "http://localhost:8888/execution",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            # Get the latest generated files
            latest_image, latest_glb = get_latest_files()
            
            status_msg = f"✅ Generated successfully for {username}"
            if latest_image:
                status_msg += f"\n🖼️ Image: {os.path.basename(latest_image)}"
            if latest_glb:
                status_msg += f"\n📦 Model: {os.path.basename(latest_glb)}"
            
            return status_msg, latest_image, latest_glb
        else:
            return f"❌ Error {response.status_code}: {response.text}", None, None
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to server (localhost:8888)", None, None
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Try a simpler description.", None, None
    except Exception as e:
        return f"❌ Error: {str(e)}", None, None

# Create minimal Gradio interface
with gr.Blocks(title="3D Generator", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("# 🎨 3D Model Generator")
    
    with gr.Row():
        username_input = gr.Textbox(
            label="Username",
            placeholder="Your name",
            value="user",
            scale=1
        )
        
        input_text = gr.Textbox(
            label="Describe your 3D model",
            placeholder="A glowing dragon on a cliff...",
            lines=2,
            scale=3
        )
    
    generate_btn = gr.Button("Generate", variant="primary", size="lg")
    
    status_output = gr.Textbox(
        label="Status",
        interactive=False,
        lines=3
    )
    
    with gr.Row():
        output_image = gr.Image(
            label="Preview",
            height=300,
            interactive=False
        )
        
        output_file = gr.File(
            label="3D Model (.glb)",
            interactive=False
        )
    
    generate_btn.click(
        fn=process_text_to_3d,
        inputs=[username_input, input_text],
        outputs=[status_output, output_image, output_file]
    )

# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )