import gradio as gr
import subprocess
import os

def run_pipeline():
    print("Executing pipeline...")
    # Run the rank.py script on the sample dataset
    result = subprocess.run(
        ["python", "rank.py", "--candidates", "sample_candidates.json"], 
        capture_output=True, 
        text=True
    )
    
    if result.returncode == 0:
        print("Pipeline execution successful.")
        # Serve the generated dashboard inside an iframe
        # Gradio hosts local files securely using the /file= prefix when allowed_paths is set
        iframe_html = """
        <iframe 
            src='/file=dashboard/index.html' 
            width='100%' 
            height='900px' 
            style='border:none; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);'>
        </iframe>
        """
        return iframe_html
    else:
        print("Pipeline failed.")
        error_html = f"""
        <div style='color:#ef4444; padding: 20px; background: #fef2f2; border-radius: 8px; font-family: monospace;'>
            <h3>🚨 Pipeline Execution Error</h3>
            <pre style='white-space: pre-wrap;'>{result.stderr}\n\n{result.stdout}</pre>
        </div>
        """
        return error_html

# Build the Gradio UI
with gr.Blocks(theme=gr.themes.Soft(), title="Redrob AI Ranker") as demo:
    gr.Markdown(
        """
        <div style="text-align: center; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h1 style="font-size: 2.5rem; font-weight: 800; color: #1e293b; margin-bottom: 10px;">🚀 Redrob AI Ranker</h1>
            <p style="font-size: 1.1rem; color: #64748b;">Interactive Hackathon Sandbox</p>
        </div>
        """
    )
    
    with gr.Card(elem_classes="container"):
        gr.Markdown("Click the button below to execute `rank.py` locally on the CPU. It will process the sample candidates, filter out honeypots, calculate semantic embeddings, and generate the reasoning. Once complete, the full UI Dashboard will load below.")
        run_btn = gr.Button("▶️ Execute AI Pipeline & Load Dashboard", variant="primary", size="lg")
    
    output_area = gr.HTML(
        """
        <div style='height: 800px; display: flex; align-items: center; justify-content: center; background: #f8fafc; border-radius: 12px; border: 2px dashed #cbd5e1; color: #94a3b8; margin-top: 20px;'>
            <h3>Waiting for execution...</h3>
        </div>
        """
    )
    
    # Connect button to function
    run_btn.click(fn=run_pipeline, inputs=[], outputs=[output_area])

# Launch the app and explicitly allow Gradio to serve files from the dashboard directory
if __name__ == "__main__":
    demo.launch(allowed_paths=["dashboard"])
