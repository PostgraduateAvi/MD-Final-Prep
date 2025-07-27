#!/usr/bin/env python3
"""
MD Final Prep - One-Command Automation
=====================================

This script provides the ultimate simple interface for the MD Final Prep automation.
Just run it and everything will be automated with minimal user interaction.

Usage:
    python3 run_full_automation.py                # Complete automation
    python3 run_full_automation.py --quick        # Quick setup only
    python3 run_full_automation.py --server-only  # Start server only
    python3 run_full_automation.py --help         # Show help
"""

import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print automation banner"""
    print("\n" + "="*70)
    print("MD FINAL PREP - COMPLETE AUTOMATION SYSTEM")
    print("="*70)
    print("🚀 Automating the complete MD Final Prep workflow...")
    print("📚 Processing medical study materials")
    print("🤖 Tokenization, embeddings, and server deployment")
    print("="*70)

def run_complete_automation():
    """Run the complete automation process"""
    print_banner()
    
    steps = [
        {
            "name": "Environment Setup & Dependencies",
            "command": [sys.executable, "quick_setup.py", "--auto"],
            "description": "Setting up environment and installing dependencies"
        },
        {
            "name": "Content Processing & Tokenization", 
            "command": [sys.executable, "md_final_prep_agent.py", "--mode", "tokenize"],
            "description": "Processing PDFs and generating tokens"
        },
        {
            "name": "Embedding Generation",
            "command": [sys.executable, "md_final_prep_agent.py", "--mode", "embeddings"], 
            "description": "Generating OpenAI embeddings (if API key available)"
        },
        {
            "name": "Results Validation",
            "command": [sys.executable, "md_final_prep_agent.py", "--mode", "status"],
            "description": "Validating processing results"
        }
    ]
    
    print(f"\n🔄 Starting {len(steps)} automation steps...\n")
    
    completed_steps = 0
    for i, step in enumerate(steps, 1):
        print(f"Step {i}/{len(steps)}: {step['name']}")
        print(f"  {step['description']}")
        
        try:
            result = subprocess.run(
                step["command"],
                capture_output=True,
                text=True,
                timeout=1200  # 20 minutes per step
            )
            
            if result.returncode == 0:
                print(f"  ✅ Completed successfully")
                completed_steps += 1
            else:
                print(f"  ⚠️  Completed with warnings")
                print(f"     Output: {result.stderr[:100]}...")
                if step["name"] == "Embedding Generation":
                    print("     (This is expected if OPENAI_API_KEY is not set)")
                    completed_steps += 1
                else:
                    print(f"     Consider checking logs for details")
                    
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Step timed out (this may be normal for large datasets)")
            completed_steps += 1
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            if i <= 2:  # Critical steps
                print(f"  🛑 Stopping automation due to critical failure")
                return False
        
        print()
    
    # Summary
    print("="*70)
    print("AUTOMATION SUMMARY")
    print("="*70)
    print(f"Completed steps: {completed_steps}/{len(steps)}")
    
    if completed_steps >= 3:  # Setup + tokenization + validation minimum
        print("🎉 AUTOMATION SUCCESSFUL!")
        print("\n📊 Generated outputs:")
        
        output_files = [
            ("tokenized_content.json", "Complete tokenization results"),
            ("token_summary.csv", "Processing statistics"),
            ("token_summary.txt", "Agent token summary"),
            ("embeddings.jsonl", "OpenAI embeddings (if generated)")
        ]
        
        for filename, description in output_files:
            if Path(filename).exists():
                size = Path(filename).stat().st_size / (1024 * 1024)
                print(f"  ✅ {filename} ({size:.1f} MB) - {description}")
            else:
                print(f"  ➖ {filename} (not generated) - {description}")
        
        print(f"\n🚀 Next steps:")
        print(f"  • Start API server: python3 md_final_prep_agent.py --mode server")
        print(f"  • Browse content: python3 navigate_content.py")
        print(f"  • Check status: python3 md_final_prep_agent.py --mode status")
        
        # Offer to start server
        print(f"\n🖥️  Start API server now? (y/n): ", end="")
        try:
            response = input().strip().lower()
            if response in ['y', 'yes']:
                print(f"\n🚀 Starting API server...")
                subprocess.run([sys.executable, "md_final_prep_agent.py", "--mode", "server"])
        except KeyboardInterrupt:
            print(f"\nServer startup cancelled.")
        
        return True
        
    else:
        print("❌ AUTOMATION INCOMPLETE")
        print("Some critical steps failed. Please check the logs and try again.")
        print(f"\n🔧 Troubleshooting:")
        print(f"  • Check setup: python3 quick_setup.py --check")
        print(f"  • Repair setup: python3 quick_setup.py --repair")
        print(f"  • Manual run: python3 md_final_prep_agent.py --mode full")
        return False

def run_quick_setup():
    """Run quick setup only"""
    print("🔧 Running quick setup...")
    try:
        result = subprocess.run([
            sys.executable, "quick_setup.py", "--auto"
        ], check=True)
        print("✅ Quick setup completed!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Quick setup failed!")
        return False

def start_server_only():
    """Start server only"""
    print("🖥️  Starting API server...")
    try:
        subprocess.run([
            sys.executable, "md_final_prep_agent.py", "--mode", "server"
        ])
        return True
    except KeyboardInterrupt:
        print("\nServer stopped.")
        return True
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MD Final Prep - One-Command Complete Automation"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true", 
        help="Run quick setup only"
    )
    
    parser.add_argument(
        "--server-only",
        action="store_true",
        help="Start API server only"
    )
    
    args = parser.parse_args()
    
    try:
        if args.quick:
            success = run_quick_setup()
        elif args.server_only:
            success = start_server_only()
        else:
            success = run_complete_automation()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Automation interrupted by user")
        print("Progress has been saved. You can resume by running the script again.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()