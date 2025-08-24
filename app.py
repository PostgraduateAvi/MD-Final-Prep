#!/usr/bin/env python3
"""
MD Final Prep Web Interface
===========================

A Gradio-based web interface for the MD Final Prep study assistant.
Provides easy access to medical content, topic summaries, and exam predictions
through an intuitive web interface that connects to the FastAPI backend.
"""

import gradio as gr
import requests
import json
import threading
import time
import subprocess
import sys
from typing import Dict, List, Tuple, Optional

# Configuration
API_BASE_URL = "http://localhost:8001"
API_TIMEOUT = 30

class MDPrepAPI:
    """Interface to the MD Prep FastAPI backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self._server_process = None
        
    def start_api_server(self) -> bool:
        """Start the FastAPI server if not already running"""
        try:
            # Check if server is already running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        # Start the server
        try:
            self._server_process = subprocess.Popen([
                sys.executable, "md_exam_prep_api.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            for _ in range(10):
                time.sleep(2)
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    if response.status_code == 200:
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"Error starting API server: {e}")
            return False
    
    def get_content(self, topic: str) -> Tuple[str, str]:
        """Get content for a specific topic"""
        try:
            response = requests.get(
                f"{self.base_url}/content/{topic}",
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return "success", data.get("content", "No content available")
            elif response.status_code == 404:
                return "not_found", f"Topic '{topic}' not found. Please try a different topic or check spelling."
            else:
                return "error", f"Server error (Status: {response.status_code})"
                
        except requests.exceptions.ConnectionError:
            return "connection_error", "Cannot connect to API server. Please ensure the server is running."
        except requests.exceptions.Timeout:
            return "timeout", "Request timed out. Please try again."
        except Exception as e:
            return "error", f"Unexpected error: {str(e)}"
    
    def summarize_topic(self, topic: str) -> Tuple[str, List[str]]:
        """Get high-yield summary points for a topic"""
        try:
            response = requests.post(
                f"{self.base_url}/summarize",
                json={"topic": topic},
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return "success", data.get("summary", [])
            else:
                return "error", [f"Server error (Status: {response.status_code})"]
                
        except requests.exceptions.ConnectionError:
            return "connection_error", ["Cannot connect to API server. Please ensure the server is running."]
        except requests.exceptions.Timeout:
            return "timeout", ["Request timed out. Please try again."]
        except Exception as e:
            return "error", [f"Unexpected error: {str(e)}"]
    
    def predict_exam_topics(self, limit: int = 5) -> Tuple[str, List[Dict]]:
        """Get predicted exam topics"""
        try:
            response = requests.get(
                f"{self.base_url}/predict?limit={limit}",
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return "success", data.get("predictions", [])
            else:
                return "error", [{"topic": "Error", "score": 0.0, "message": f"Server error (Status: {response.status_code})"}]
                
        except requests.exceptions.ConnectionError:
            return "connection_error", [{"topic": "Connection Error", "score": 0.0, "message": "Cannot connect to API server"}]
        except requests.exceptions.Timeout:
            return "timeout", [{"topic": "Timeout", "score": 0.0, "message": "Request timed out"}]
        except Exception as e:
            return "error", [{"topic": "Error", "score": 0.0, "message": f"Unexpected error: {str(e)}"}]

# Initialize API client
api = MDPrepAPI()

def search_content(topic: str) -> str:
    """Search for content on a specific medical topic"""
    if not topic.strip():
        return "Please enter a topic to search for."
    
    status, content = api.get_content(topic.strip())
    
    if status == "success":
        # Truncate very long content for better display
        if len(content) > 3000:
            content = content[:3000] + "\n\n... (content truncated for display)"
        return f"📚 **Content for '{topic}':**\n\n{content}"
    elif status == "not_found":
        return f"❌ {content}\n\n💡 **Suggestions:**\n- Try broader terms (e.g., 'heart' instead of 'heart failure')\n- Check spelling\n- Try related terms (e.g., 'diabetes', 'cardiology', 'neurology')"
    else:
        return f"⚠️ {content}"

def get_topic_summary(topic: str) -> str:
    """Get high-yield summary points for a topic"""
    if not topic.strip():
        return "Please enter a topic to summarize."
    
    status, summary_points = api.summarize_topic(topic.strip())
    
    if status == "success" and summary_points:
        summary_text = f"📋 **High-Yield Summary for '{topic}':**\n\n"
        for i, point in enumerate(summary_points, 1):
            summary_text += f"**{i}.** {point}\n\n"
        return summary_text
    elif status == "success":
        return f"📋 **Summary for '{topic}':**\n\nNo specific high-yield points available for this topic."
    else:
        return f"⚠️ Error getting summary: {summary_points[0] if summary_points else 'Unknown error'}"

def get_exam_predictions(num_topics: int) -> str:
    """Get predicted exam topics"""
    num_topics = max(1, min(num_topics, 10))  # Limit between 1-10
    
    status, predictions = api.predict_exam_topics(num_topics)
    
    if status == "success" and predictions:
        result = f"🎯 **Top {num_topics} Predicted Exam Topics:**\n\n"
        for i, pred in enumerate(predictions, 1):
            topic = pred.get("topic", "Unknown")
            score = pred.get("score", 0.0)
            # Convert score to percentage and add visual indicator
            percentage = score * 100
            if percentage >= 80:
                indicator = "🔥"
            elif percentage >= 60:
                indicator = "⭐"
            else:
                indicator = "📌"
            
            result += f"**{i}. {topic.replace('_', ' ').title()}** {indicator}\n"
            result += f"   Likelihood: {percentage:.1f}%\n\n"
        
        result += "\n💡 **Study Tips:**\n"
        result += "- Focus on high-likelihood topics (🔥) first\n"
        result += "- Review recent guidelines and updates\n"
        result += "- Practice case-based questions\n"
        
        return result
    else:
        error_msg = predictions[0].get("message", "Unknown error") if predictions else "No predictions available"
        return f"⚠️ Error getting predictions: {error_msg}"

def server_status() -> str:
    """Check and display server status"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"✅ **Server Status:** {data.get('status', 'Unknown')}\n📊 **API Version:** {data.get('version', 'Unknown')}"
        else:
            return f"⚠️ **Server Status:** Error (HTTP {response.status_code})"
    except:
        return "❌ **Server Status:** Not reachable\n\n🔧 **Troubleshooting:**\n- Ensure the API server is running\n- Check if port 8001 is available\n- Try restarting the server"

# Create Gradio interface
with gr.Blocks(
    title="MD Final Prep Assistant",
    theme=gr.themes.Soft(),
    css=".gradio-container {max-width: 1200px !important}"
) as app:
    
    gr.Markdown("""
    # 🩺 MD Final Prep Assistant
    
    Welcome to your comprehensive MD exam preparation tool! This interface connects to your local study content 
    and provides intelligent access to medical materials, summaries, and exam predictions.
    
    ## 🚀 Quick Start
    1. **Search Content**: Find specific medical topics and content
    2. **Get Summaries**: Generate high-yield study points
    3. **Exam Predictions**: See likely exam topics based on content analysis
    """)
    
    with gr.Tabs():
        # Content Search Tab
        with gr.Tab("📚 Search Content"):
            gr.Markdown("### Search for Medical Topics")
            gr.Markdown("Enter a medical topic to find relevant content from your study materials.")
            
            with gr.Row():
                with gr.Column(scale=3):
                    content_input = gr.Textbox(
                        label="Topic",
                        placeholder="e.g., diabetes, heart failure, pneumonia, neurology",
                        lines=1
                    )
                with gr.Column(scale=1):
                    content_btn = gr.Button("🔍 Search", variant="primary")
            
            content_output = gr.Markdown(label="Content Results")
            
            # Example searches
            gr.Markdown("### 💡 Example Searches")
            example_buttons = []
            examples = ["diabetes", "heart_failure", "pneumonia", "neurology", "hypertension"]
            
            with gr.Row():
                for example in examples:
                    btn = gr.Button(f"Try: {example}", size="sm")
                    btn.click(lambda x=example: search_content(x), outputs=content_output)
        
        # Topic Summary Tab  
        with gr.Tab("📋 Topic Summaries"):
            gr.Markdown("### Generate High-Yield Study Points")
            gr.Markdown("Get focused, high-yield summary points for any medical topic.")
            
            with gr.Row():
                with gr.Column(scale=3):
                    summary_input = gr.Textbox(
                        label="Topic for Summary",
                        placeholder="e.g., acute coronary syndrome, diabetic ketoacidosis",
                        lines=1
                    )
                with gr.Column(scale=1):
                    summary_btn = gr.Button("📋 Summarize", variant="primary")
            
            summary_output = gr.Markdown(label="Summary Results")
        
        # Exam Predictions Tab
        with gr.Tab("🎯 Exam Predictions"):
            gr.Markdown("### Predicted Exam Topics")
            gr.Markdown("Get AI-powered predictions of likely exam topics based on content analysis.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    predictions_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Number of predictions"
                    )
                with gr.Column(scale=1):
                    predictions_btn = gr.Button("🎯 Predict", variant="primary")
            
            predictions_output = gr.Markdown(label="Prediction Results")
        
        # Server Status Tab
        with gr.Tab("🔧 Server Status"):
            gr.Markdown("### API Server Information")
            
            status_btn = gr.Button("🔄 Check Status", variant="secondary")
            status_output = gr.Markdown(label="Server Status")
            
            gr.Markdown("""
            ### 🛠️ Troubleshooting
            
            **If the server is not running:**
            1. Open a terminal in your MD-Final-Prep directory
            2. Run: `python3 md_exam_prep_api.py`
            3. Wait for "Application startup complete"
            4. The server should be available at http://localhost:8001
            
            **Common Issues:**
            - Port 8001 already in use: Try stopping other services or restarting
            - Missing dependencies: Run `pip install -r requirements.txt`
            - Permission errors: Check file permissions in the directory
            """)
    
    # Event handlers
    content_btn.click(search_content, inputs=content_input, outputs=content_output)
    content_input.submit(search_content, inputs=content_input, outputs=content_output)
    
    summary_btn.click(get_topic_summary, inputs=summary_input, outputs=summary_output)
    summary_input.submit(get_topic_summary, inputs=summary_input, outputs=summary_output)
    
    predictions_btn.click(get_exam_predictions, inputs=predictions_slider, outputs=predictions_output)
    
    status_btn.click(server_status, outputs=status_output)
    
    # Auto-load server status on startup
    app.load(server_status, outputs=status_output)

def main():
    """Main function to start the web interface"""
    print("🩺 Starting MD Final Prep Web Interface...")
    print("=" * 50)
    
    # Try to start the API server
    print("🔧 Checking API server status...")
    if not api.start_api_server():
        print("⚠️  Warning: Could not start API server automatically.")
        print("   Please start it manually: python3 md_exam_prep_api.py")
    else:
        print("✅ API server is running")
    
    print("\n🌐 Starting web interface...")
    print("   Access the app at: http://localhost:7860")
    print("   API documentation: http://localhost:8001/docs")
    print("\n🛑 Press Ctrl+C to stop the application")
    
    # Launch Gradio app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()