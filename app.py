#!/usr/bin/env python3
"""
MD Final Prep - Web Interface
============================

Gradio-based web interface for the MD Final Prep study assistant.
Provides easy access to study content, topic summaries, and exam predictions.
"""

import gradio as gr
import requests
import json
import subprocess
import threading
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8001"
API_PROCESS = None

def start_api_server():
    """Start the FastAPI server in background."""
    global API_PROCESS
    try:
        API_PROCESS = subprocess.Popen([
            "python", "md_exam_prep_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # Wait for server to start
        return "✅ API server started successfully"
    except Exception as e:
        return f"❌ Failed to start API server: {e}"

def check_api_status():
    """Check if the API server is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return "✅ API server is running"
        else:
            return f"⚠️ API server returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ API server is not reachable"
    except Exception as e:
        return f"❌ Error checking API: {e}"

def get_exam_predictions(limit=5):
    """Get exam topic predictions."""
    try:
        response = requests.get(f"{API_BASE_URL}/predict?limit={limit}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            predictions = data.get("predictions", [])
            
            result = "📊 **Predicted Exam Topics:**\n\n"
            for i, pred in enumerate(predictions, 1):
                topic = pred.get("topic", "Unknown")
                score = pred.get("score", 0)
                result += f"{i}. **{topic.replace('_', ' ').title()}** (Score: {score:.2f})\n"
            
            return result if predictions else "No predictions available"
        else:
            return f"Error: API returned status {response.status_code}"
    except Exception as e:
        return f"Error getting predictions: {e}"

def summarize_topic(topic):
    """Get summary for a specific topic."""
    if not topic.strip():
        return "Please enter a topic to summarize"
    
    try:
        data = {"topic": topic.lower().replace(" ", "_")}
        response = requests.post(f"{API_BASE_URL}/summarize", json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            summary_points = result.get("summary", [])
            
            if summary_points:
                formatted_summary = f"📝 **Summary for '{topic}':**\n\n"
                for i, point in enumerate(summary_points, 1):
                    formatted_summary += f"{i}. {point}\n"
                return formatted_summary
            else:
                return f"No summary available for '{topic}'"
        else:
            return f"Error: API returned status {response.status_code}"
    except Exception as e:
        return f"Error summarizing topic: {e}"

def get_topic_content(topic):
    """Get detailed content for a topic."""
    if not topic.strip():
        return "Please enter a topic to search"
    
    try:
        topic_formatted = topic.lower().replace(" ", "_")
        response = requests.get(f"{API_BASE_URL}/content/{topic_formatted}", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("content", "")
            
            if content:
                # Truncate content if too long for display
                if len(content) > 2000:
                    content = content[:2000] + "...\n\n[Content truncated - full content available via API]"
                
                return f"📚 **Content for '{topic}':**\n\n{content}"
            else:
                return f"No detailed content found for '{topic}'"
        elif response.status_code == 404:
            return f"Topic '{topic}' not found in the database"
        else:
            return f"Error: API returned status {response.status_code}"
    except Exception as e:
        return f"Error getting content: {e}"

def get_system_status():
    """Get overall system status."""
    status = []
    
    # Check API
    api_status = check_api_status()
    status.append(f"**API Status:** {api_status}")
    
    # Check data files
    files_to_check = [
        "tokenized_content.json",
        "token_summary.csv", 
        "md_prep_config.json"
    ]
    
    status.append("\n**Data Files:**")
    for file in files_to_check:
        if Path(file).exists():
            status.append(f"✅ {file}")
        else:
            status.append(f"❌ {file}")
    
    return "\n".join(status)

# Create Gradio interface
def create_interface():
    """Create the Gradio web interface."""
    
    with gr.Blocks(
        title="MD Final Prep Assistant",
        theme=gr.themes.Soft(),
    ) as demo:
        
        gr.Markdown("""
        # 🩺 MD Final Prep Assistant
        
        Your comprehensive study companion for MD final exam preparation.
        Access study content, get topic summaries, and view exam predictions.
        """)
        
        with gr.Tabs():
            
            # System Status Tab
            with gr.Tab("🔧 System Status"):
                gr.Markdown("### System Status Overview")
                
                with gr.Row():
                    start_btn = gr.Button("🚀 Start API Server", variant="primary")
                    status_btn = gr.Button("🔍 Check Status", variant="secondary")
                
                status_output = gr.Textbox(
                    label="System Status",
                    lines=8,
                    value="Click 'Check Status' to see system information"
                )
                
                start_btn.click(start_api_server, outputs=status_output)
                status_btn.click(get_system_status, outputs=status_output)
            
            # Exam Predictions Tab
            with gr.Tab("📊 Exam Predictions"):
                gr.Markdown("### Get predictions for likely exam topics")
                
                with gr.Row():
                    limit_slider = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=5,
                        step=1,
                        label="Number of predictions"
                    )
                    predict_btn = gr.Button("🎯 Get Predictions", variant="primary")
                
                predictions_output = gr.Textbox(
                    label="Exam Topic Predictions",
                    lines=10,
                    placeholder="Click 'Get Predictions' to see likely exam topics..."
                )
                
                predict_btn.click(
                    get_exam_predictions,
                    inputs=limit_slider,
                    outputs=predictions_output
                )
            
            # Topic Summary Tab
            with gr.Tab("📝 Topic Summary"):
                gr.Markdown("### Get concise summaries of medical topics")
                
                with gr.Row():
                    topic_input = gr.Textbox(
                        label="Enter Topic",
                        placeholder="e.g., heart failure, diabetes, hypertension",
                        lines=1
                    )
                    summarize_btn = gr.Button("📋 Summarize", variant="primary")
                
                summary_output = gr.Textbox(
                    label="Topic Summary",
                    lines=10,
                    placeholder="Enter a topic and click 'Summarize' to get key points..."
                )
                
                # Examples
                gr.Examples(
                    examples=[
                        ["heart failure"],
                        ["diabetes mellitus"],
                        ["hypertension"],
                        ["myocardial infarction"],
                        ["chronic kidney disease"]
                    ],
                    inputs=topic_input
                )
                
                summarize_btn.click(
                    summarize_topic,
                    inputs=topic_input,
                    outputs=summary_output
                )
            
            # Content Search Tab
            with gr.Tab("📚 Content Search"):
                gr.Markdown("### Search detailed content on medical topics")
                
                with gr.Row():
                    content_topic_input = gr.Textbox(
                        label="Search Topic",
                        placeholder="e.g., cardiology, nephrology, endocrinology",
                        lines=1
                    )
                    search_btn = gr.Button("🔍 Search Content", variant="primary")
                
                content_output = gr.Textbox(
                    label="Topic Content",
                    lines=15,
                    placeholder="Enter a topic and click 'Search Content' to get detailed information..."
                )
                
                # Examples for content search
                gr.Examples(
                    examples=[
                        ["cardiology"],
                        ["nephrology"], 
                        ["endocrinology"],
                        ["neurology"],
                        ["infectious diseases"]
                    ],
                    inputs=content_topic_input
                )
                
                search_btn.click(
                    get_topic_content,
                    inputs=content_topic_input,
                    outputs=content_output
                )
        
        gr.Markdown("""
        ---
        ### 💡 Quick Start Tips:
        1. **Start Here:** Go to 'System Status' and click 'Start API Server'
        2. **Get Predictions:** Use 'Exam Predictions' to see likely exam topics
        3. **Study Topics:** Use 'Topic Summary' for quick overviews
        4. **Deep Dive:** Use 'Content Search' for detailed information
        
        **Need help?** Check the [Documentation](README.md) for more details.
        """)
    
    return demo

if __name__ == "__main__":
    print("🚀 Starting MD Final Prep Web Interface...")
    
    # Auto-start API server
    print("🔧 Starting API server...")
    start_api_server()
    
    # Create and launch interface
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )