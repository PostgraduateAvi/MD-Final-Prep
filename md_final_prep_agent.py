#!/usr/bin/env python3
"""
MD Final Prep Agent - Complete Automation System
===============================================

This is the master automation agent that orchestrates the entire MD Final Prep
workflow from content processing to deployment. It provides a single command
interface to run the complete process or specific components.

Features:
- Automated dependency checking and installation
- Complete content processing pipeline
- Progress tracking and comprehensive logging
- Error handling and recovery
- Multiple execution modes (full, components, server)
- Configuration management
- Automated validation and quality checks

Usage:
    python3 md_final_prep_agent.py --mode full          # Complete automation
    python3 md_final_prep_agent.py --mode tokenize      # Just tokenization
    python3 md_final_prep_agent.py --mode embeddings    # Just embeddings
    python3 md_final_prep_agent.py --mode server        # Start API server
    python3 md_final_prep_agent.py --mode status        # Show current status
    python3 md_final_prep_agent.py --mode setup         # Setup and verify environment
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
import queue

# Setup comprehensive logging
log_file = f"md_prep_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MDFinalPrepAgent:
    """Master automation agent for MD Final Prep workflow"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.config = self.load_configuration()
        self.progress = {
            "setup": False,
            "dependencies": False,
            "tokenization": False,
            "embeddings": False,
            "server": False,
            "validation": False
        }
        self.errors = []
        self.stats = {}
        self.server_process = None
        
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration with sensible defaults"""
        default_config = {
            "base_path": "PDFs",
            "output_files": {
                "tokenized": "tokenized_content.json",
                "embeddings": "embeddings.jsonl",
                "token_summary": "token_summary.csv",
                "agent_token_summary": "token_summary.txt"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "auto_restart": True
            },
            "processing": {
                "max_retries": 3,
                "chunk_size": 512,
                "embedding_model": "text-embedding-ada-002"
            },
            "validation": {
                "min_tokens_per_file": 10,
                "max_file_size_mb": 500,
                "required_categories": ["harrison_textbooks", "guidelines", "neurology_textbooks", "question_papers"]
            }
        }
        
        # Try to load custom config if it exists
        config_file = Path("md_prep_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
                    logger.info("Loaded custom configuration")
            except Exception as e:
                logger.warning(f"Could not load custom config: {e}")
        
        return default_config
    
    def save_configuration(self):
        """Save current configuration"""
        config_file = Path("md_prep_config.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Could not save configuration: {e}")
    
    def check_dependencies(self) -> bool:
        """Check and install required dependencies"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            "PyPDF2==3.0.1",
            "pandas>=2.0.0", 
            "openpyxl>=3.1.0",
            "tiktoken>=0.5.0",
            "openai>=1.0.0",
            "fastapi>=0.110",
            "uvicorn>=0.23"
        ]
        
        try:
            # Check if requirements.txt exists and install
            if Path("requirements.txt").exists():
                logger.info("Installing dependencies from requirements.txt...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"Dependency installation failed: {result.stderr}")
                    return False
                else:
                    logger.info("✓ Dependencies installed successfully")
                    self.progress["dependencies"] = True
                    return True
            else:
                logger.error("requirements.txt not found")
                return False
                
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return False
    
    def verify_environment(self) -> bool:
        """Verify the environment setup"""
        logger.info("Verifying environment setup...")
        
        checks = [
            ("PDFs directory", Path("PDFs").exists()),
            ("Python version >= 3.8", sys.version_info >= (3, 8)),
            ("Write permissions", os.access(".", os.W_OK))
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                logger.info(f"✓ {check_name}")
            else:
                logger.error(f"✗ {check_name}")
                all_passed = False
        
        if all_passed:
            self.progress["setup"] = True
            logger.info("✓ Environment verification passed")
        else:
            logger.error("Environment verification failed")
            
        return all_passed
    
    def run_tokenization(self) -> bool:
        """Run the tokenization process"""
        logger.info("Starting tokenization process...")
        
        try:
            # Run simple tokenization first
            logger.info("Running simple tokenization...")
            result = subprocess.run([
                sys.executable, "simple_tokenize.py"
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                logger.error(f"Simple tokenization failed: {result.stderr}")
                # Try the PDF token agent as fallback
                logger.info("Trying PDF token agent as fallback...")
                result = subprocess.run([
                    sys.executable, "pdf_token_agent.py"
                ], capture_output=True, text=True, timeout=900)
                
                if result.returncode != 0:
                    logger.error(f"PDF token agent also failed: {result.stderr}")
                    return False
            
            # Verify tokenization output
            tokenized_file = Path(self.config["output_files"]["tokenized"])
            if tokenized_file.exists():
                logger.info("✓ Tokenization completed successfully")
                self.progress["tokenization"] = True
                
                # Load and log stats
                with open(tokenized_file, 'r') as f:
                    data = json.load(f)
                    total_files = sum(len(files) for files in data.values())
                    total_tokens = sum(
                        sum(file_info.get('total_tokens', 0) for file_info in files)
                        for files in data.values()
                    )
                    self.stats["tokenization"] = {
                        "total_files": total_files,
                        "total_tokens": total_tokens
                    }
                    logger.info(f"Processed {total_files} files, generated {total_tokens:,} tokens")
                
                return True
            else:
                logger.error("Tokenization output file not found")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Tokenization process timed out")
            return False
        except Exception as e:
            logger.error(f"Error during tokenization: {e}")
            return False
    
    def run_embeddings(self) -> bool:
        """Run the embedding generation process"""
        logger.info("Starting embedding generation...")
        
        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not set, skipping embedding generation")
            logger.info("To enable embeddings, set: export OPENAI_API_KEY=your_api_key")
            return True  # Not a failure, just skipped
        
        try:
            logger.info("Generating embeddings with OpenAI API...")
            result = subprocess.run([
                sys.executable, "generate_embeddings.py"
            ], capture_output=True, text=True, timeout=1800)  # 30 minutes timeout
            
            if result.returncode != 0:
                logger.error(f"Embedding generation failed: {result.stderr}")
                return False
            
            # Verify embeddings output
            embeddings_file = Path(self.config["output_files"]["embeddings"])
            if embeddings_file.exists():
                logger.info("✓ Embeddings generated successfully")
                self.progress["embeddings"] = True
                
                # Count embeddings
                with open(embeddings_file, 'r') as f:
                    embedding_count = sum(1 for line in f)
                    self.stats["embeddings"] = {"total_embeddings": embedding_count}
                    logger.info(f"Generated {embedding_count} embeddings")
                
                return True
            else:
                logger.error("Embeddings output file not found")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Embedding generation timed out")
            return False
        except Exception as e:
            logger.error(f"Error during embedding generation: {e}")
            return False
    
    def start_server(self, background=False) -> bool:
        """Start the API server"""
        logger.info("Starting API server...")
        
        try:
            if background:
                # Start server in background
                self.server_process = subprocess.Popen([
                    sys.executable, "server.py"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Give it a moment to start
                time.sleep(3)
                
                if self.server_process.poll() is None:
                    logger.info(f"✓ API server started in background (PID: {self.server_process.pid})")
                    logger.info(f"Server accessible at http://{self.config['server']['host']}:{self.config['server']['port']}")
                    self.progress["server"] = True
                    return True
                else:
                    logger.error("Server failed to start")
                    return False
            else:
                # Start server in foreground
                logger.info(f"Starting server at http://{self.config['server']['host']}:{self.config['server']['port']}")
                logger.info("Press Ctrl+C to stop the server")
                
                result = subprocess.run([
                    sys.executable, "server.py"
                ])
                
                return result.returncode == 0
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the API server"""
        if self.server_process:
            logger.info("Stopping API server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
                logger.info("✓ Server stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Server didn't stop gracefully, forcing termination")
                self.server_process.kill()
                self.server_process.wait()
            finally:
                self.server_process = None
    
    def validate_results(self) -> bool:
        """Validate the processing results"""
        logger.info("Validating processing results...")
        
        validation_passed = True
        
        # Check required output files
        required_files = [
            self.config["output_files"]["tokenized"],
            self.config["output_files"]["token_summary"]
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                logger.info(f"✓ {file_path} exists")
            else:
                logger.error(f"✗ {file_path} missing")
                validation_passed = False
        
        # Validate tokenization data
        try:
            tokenized_file = Path(self.config["output_files"]["tokenized"])
            if tokenized_file.exists():
                with open(tokenized_file, 'r') as f:
                    data = json.load(f)
                
                # Check required categories
                for category in self.config["validation"]["required_categories"]:
                    if category in data:
                        logger.info(f"✓ Category '{category}' found")
                    else:
                        logger.warning(f"⚠ Category '{category}' missing")
                
                # Check token counts
                min_tokens = self.config["validation"]["min_tokens_per_file"]
                low_token_files = []
                for category, files in data.items():
                    for file_info in files:
                        if file_info.get('total_tokens', 0) < min_tokens:
                            low_token_files.append(f"{category}/{file_info['filename']}")
                
                if low_token_files:
                    logger.warning(f"Files with low token counts: {low_token_files}")
                else:
                    logger.info("✓ All files have adequate token counts")
                    
        except Exception as e:
            logger.error(f"Error validating tokenization data: {e}")
            validation_passed = False
        
        if validation_passed:
            self.progress["validation"] = True
            logger.info("✓ Validation passed")
        else:
            logger.error("Validation failed")
            
        return validation_passed
    
    def show_status(self):
        """Show current status and statistics"""
        print("\n" + "="*70)
        print("MD FINAL PREP AGENT - STATUS REPORT")
        print("="*70)
        
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Runtime: {datetime.now() - self.start_time}")
        print(f"Log file: {log_file}")
        
        print(f"\nProgress:")
        for step, completed in self.progress.items():
            status = "✓" if completed else "✗"
            print(f"  {status} {step.replace('_', ' ').title()}")
        
        if self.stats:
            print(f"\nStatistics:")
            for category, stats in self.stats.items():
                print(f"  {category.title()}:")
                for key, value in stats.items():
                    print(f"    {key.replace('_', ' ').title()}: {value:,}")
        
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors[-5:]:  # Show last 5 errors
                print(f"  • {error}")
        
        # Check file status
        print(f"\nOutput Files:")
        for file_type, file_path in self.config["output_files"].items():
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {file_type}: {file_path} ({size:.1f} MB)")
            else:
                print(f"  ✗ {file_type}: {file_path} (missing)")
        
        print("="*70)
    
    def run_full_automation(self) -> bool:
        """Run the complete automation pipeline"""
        logger.info("Starting full MD Final Prep automation...")
        
        steps = [
            ("Environment Setup", self.verify_environment),
            ("Dependencies", self.check_dependencies),
            ("Tokenization", self.run_tokenization),
            ("Embeddings", self.run_embeddings),
            ("Validation", self.validate_results)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n{'='*50}")
            logger.info(f"STEP: {step_name}")
            logger.info("="*50)
            
            try:
                success = step_func()
                if not success:
                    logger.error(f"Step '{step_name}' failed")
                    self.errors.append(f"Step '{step_name}' failed")
                    
                    # Ask if user wants to continue
                    if step_name not in ["Embeddings"]:  # Embeddings is optional
                        logger.error("Critical step failed. Stopping automation.")
                        return False
                    else:
                        logger.warning("Optional step failed. Continuing...")
                        
            except Exception as e:
                logger.error(f"Error in step '{step_name}': {e}")
                self.errors.append(f"Error in step '{step_name}': {e}")
                return False
        
        logger.info("\n" + "="*70)
        logger.info("AUTOMATION COMPLETED SUCCESSFULLY!")
        logger.info("="*70)
        
        self.show_status()
        
        # Offer to start server
        print(f"\nWould you like to start the API server? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                return self.start_server(background=False)
        except KeyboardInterrupt:
            print("\nServer startup cancelled.")
        
        return True
    
    def cleanup(self):
        """Cleanup resources"""
        if self.server_process:
            self.stop_server()
        logger.info("Cleanup completed")

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\nReceived interrupt signal. Cleaning up...")
    if hasattr(signal_handler, 'agent'):
        signal_handler.agent.cleanup()
    sys.exit(0)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MD Final Prep Agent - Complete Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode full          # Run complete automation
  %(prog)s --mode setup         # Setup and verify environment
  %(prog)s --mode tokenize      # Run tokenization only
  %(prog)s --mode embeddings    # Generate embeddings only
  %(prog)s --mode server        # Start API server
  %(prog)s --mode status        # Show current status
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["full", "setup", "tokenize", "embeddings", "server", "status"],
        default="full",
        help="Automation mode to run"
    )
    
    parser.add_argument(
        "--background",
        action="store_true",
        help="Run server in background (only for server mode)"
    )
    
    args = parser.parse_args()
    
    # Setup signal handling
    agent = MDFinalPrepAgent()
    signal_handler.agent = agent
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.mode == "full":
            success = agent.run_full_automation()
        elif args.mode == "setup":
            success = agent.verify_environment() and agent.check_dependencies()
        elif args.mode == "tokenize":
            success = agent.run_tokenization()
        elif args.mode == "embeddings":
            success = agent.run_embeddings()
        elif args.mode == "server":
            success = agent.start_server(background=args.background)
        elif args.mode == "status":
            agent.show_status()
            success = True
        
        if success:
            logger.info(f"Mode '{args.mode}' completed successfully")
            sys.exit(0)
        else:
            logger.error(f"Mode '{args.mode}' failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        agent.cleanup()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        agent.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()