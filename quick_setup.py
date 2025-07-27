#!/usr/bin/env python3
"""
MD Final Prep - Automated Setup and Quick Start Script
=====================================================

This script provides automated setup, dependency management, and quick start
options for the MD Final Prep system. It's designed to get users up and
running with minimal effort.

Usage:
    python3 quick_setup.py                    # Interactive setup
    python3 quick_setup.py --auto             # Automated setup
    python3 quick_setup.py --check            # Check current status
    python3 quick_setup.py --repair           # Repair broken components
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickSetup:
    """Quick setup and automation helper for MD Final Prep"""
    
    def __init__(self):
        self.required_files = [
            "requirements.txt",
            "simple_tokenize.py", 
            "pdf_token_agent.py",
            "generate_embeddings.py",
            "server.py",
            "navigate_content.py",
            "md_final_prep_agent.py"
        ]
        
        self.required_dirs = [
            "PDFs",
            "PDFs/Harrison_Textbooks",
            "PDFs/Guidelines", 
            "PDFs/Neurology_Textbooks",
            "PDFs/Question_Papers"
        ]
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check system prerequisites"""
        logger.info("Checking system prerequisites...")
        
        checks = {}
        
        # Python version
        checks["python_version"] = sys.version_info >= (3, 8)
        if checks["python_version"]:
            logger.info(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
        else:
            logger.error(f"✗ Python version too old: {sys.version_info.major}.{sys.version_info.minor}")
        
        # Required files
        checks["required_files"] = all(Path(f).exists() for f in self.required_files)
        missing_files = [f for f in self.required_files if not Path(f).exists()]
        if missing_files:
            logger.error(f"✗ Missing files: {missing_files}")
        else:
            logger.info("✓ All required files present")
        
        # Required directories
        checks["required_dirs"] = all(Path(d).exists() for d in self.required_dirs)
        missing_dirs = [d for d in self.required_dirs if not Path(d).exists()]
        if missing_dirs:
            logger.warning(f"⚠ Missing directories: {missing_dirs}")
            logger.info("Note: Some directories may be created during processing")
        else:
            logger.info("✓ All required directories present")
        
        # Write permissions
        checks["write_permissions"] = os.access(".", os.W_OK)
        if checks["write_permissions"]:
            logger.info("✓ Write permissions available")
        else:
            logger.error("✗ No write permissions in current directory")
        
        # Pip available
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         capture_output=True, check=True)
            checks["pip_available"] = True
            logger.info("✓ Pip package manager available")
        except subprocess.CalledProcessError:
            checks["pip_available"] = False
            logger.error("✗ Pip package manager not available")
        
        return checks
    
    def install_dependencies(self) -> bool:
        """Install required dependencies"""
        logger.info("Installing dependencies...")
        
        try:
            # First, upgrade pip
            logger.info("Upgrading pip...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            if Path("requirements.txt").exists():
                logger.info("Installing from requirements.txt...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✓ Dependencies installed successfully")
                    return True
                else:
                    logger.error(f"✗ Dependency installation failed: {result.stderr}")
                    return False
            else:
                logger.error("requirements.txt not found")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
            return False
    
    def create_missing_directories(self):
        """Create any missing directories"""
        logger.info("Creating missing directories...")
        
        for directory in self.required_dirs:
            dir_path = Path(directory)
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"✓ Created directory: {directory}")
                except Exception as e:
                    logger.error(f"✗ Could not create directory {directory}: {e}")
    
    def setup_configuration(self):
        """Setup default configuration if not exists"""
        config_file = Path("md_prep_config.json")
        
        if not config_file.exists():
            logger.info("Creating default configuration...")
            
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
                }
            }
            
            try:
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"✓ Configuration saved to {config_file}")
            except Exception as e:
                logger.error(f"✗ Could not save configuration: {e}")
        else:
            logger.info("✓ Configuration file already exists")
    
    def create_gitignore(self):
        """Create/update .gitignore for automation outputs"""
        gitignore_file = Path(".gitignore")
        
        automation_entries = [
            "# MD Prep Automation outputs",
            "md_prep_automation_*.log",
            "embeddings.jsonl",
            "*.tmp",
            "__pycache__/",
            "*.pyc",
            ".env",
            "# OpenAI API key files",
            "openai_key.txt"
        ]
        
        if gitignore_file.exists():
            with open(gitignore_file, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = ""
        
        # Add entries that don't already exist
        new_entries = []
        for entry in automation_entries:
            if entry not in existing_content:
                new_entries.append(entry)
        
        if new_entries:
            with open(gitignore_file, 'a') as f:
                f.write("\n" + "\n".join(new_entries) + "\n")
            logger.info(f"✓ Updated .gitignore with {len(new_entries)} new entries")
        else:
            logger.info("✓ .gitignore already up to date")
    
    def verify_setup(self) -> bool:
        """Verify the setup is working"""
        logger.info("Verifying setup...")
        
        # Test import of key modules
        test_imports = [
            ("PyPDF2", "PyPDF2"),
            ("pandas", "pandas"), 
            ("openpyxl", "openpyxl"),
            ("tiktoken", "tiktoken"),
            ("fastapi", "fastapi"),
            ("uvicorn", "uvicorn")
        ]
        
        failed_imports = []
        for name, module in test_imports:
            try:
                __import__(module)
                logger.info(f"✓ {name} import successful")
            except ImportError as e:
                logger.error(f"✗ {name} import failed: {e}")
                failed_imports.append(name)
        
        if failed_imports:
            logger.error(f"Setup verification failed. Missing modules: {failed_imports}")
            return False
        
        # Test script execution
        try:
            result = subprocess.run([
                sys.executable, "md_final_prep_agent.py", "--mode", "status"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✓ Main automation script working")
                return True
            else:
                logger.error(f"✗ Main automation script failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error testing main script: {e}")
            return False
    
    def interactive_setup(self):
        """Run interactive setup with user prompts"""
        print("\n" + "="*70)
        print("MD FINAL PREP - INTERACTIVE SETUP")
        print("="*70)
        
        # Check prerequisites
        checks = self.check_prerequisites()
        critical_failed = not all([
            checks.get("python_version", False),
            checks.get("required_files", False), 
            checks.get("write_permissions", False),
            checks.get("pip_available", False)
        ])
        
        if critical_failed:
            print("\n❌ Critical prerequisites failed. Cannot continue.")
            print("Please ensure you have:")
            print("- Python 3.8 or later")
            print("- All required script files")
            print("- Write permissions in current directory") 
            print("- Pip package manager")
            return False
        
        print(f"\n✅ Prerequisites check passed!")
        
        # Ask about dependency installation
        print(f"\nInstall dependencies? (y/n): ", end="")
        try:
            if input().strip().lower() in ['y', 'yes']:
                if not self.install_dependencies():
                    print("❌ Dependency installation failed")
                    return False
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            return False
        
        # Create directories and configuration
        self.create_missing_directories()
        self.setup_configuration()
        self.create_gitignore()
        
        # Verify setup
        print(f"\nVerify setup? (y/n): ", end="")
        try:
            if input().strip().lower() in ['y', 'yes']:
                if not self.verify_setup():
                    print("❌ Setup verification failed")
                    return False
        except KeyboardInterrupt:
            print("\nVerification skipped.")
        
        print(f"\n✅ Setup completed successfully!")
        print(f"\nNext steps:")
        print(f"1. Run: python3 md_final_prep_agent.py --mode full")
        print(f"2. Or run: python3 md_final_prep_agent.py --mode tokenize")
        print(f"3. For embeddings, set OPENAI_API_KEY environment variable")
        
        return True
    
    def auto_setup(self):
        """Run automated setup without prompts"""
        logger.info("Running automated setup...")
        
        # Check prerequisites
        checks = self.check_prerequisites()
        if not all(checks.values()):
            logger.error("Prerequisites check failed. Cannot continue automated setup.")
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            logger.error("Dependency installation failed")
            return False
        
        # Setup environment
        self.create_missing_directories()
        self.setup_configuration()
        self.create_gitignore()
        
        # Verify setup
        if not self.verify_setup():
            logger.error("Setup verification failed")
            return False
        
        logger.info("✅ Automated setup completed successfully!")
        return True
    
    def repair_setup(self):
        """Repair broken components"""
        logger.info("Attempting to repair setup...")
        
        # Re-install dependencies
        logger.info("Re-installing dependencies...")
        if not self.install_dependencies():
            logger.error("Could not repair dependencies")
            return False
        
        # Recreate missing files/directories
        self.create_missing_directories()
        self.setup_configuration()
        
        # Verify repair
        if self.verify_setup():
            logger.info("✅ Setup repair completed successfully!")
            return True
        else:
            logger.error("❌ Setup repair failed")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MD Final Prep - Quick Setup and Automation Helper"
    )
    
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run automated setup without prompts"
    )
    
    parser.add_argument(
        "--check",
        action="store_true", 
        help="Check current setup status"
    )
    
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Repair broken setup components"
    )
    
    args = parser.parse_args()
    
    setup = QuickSetup()
    
    try:
        if args.check:
            checks = setup.check_prerequisites()
            setup.verify_setup()
            print(f"\nSetup status: {'✅ Good' if all(checks.values()) else '❌ Issues found'}")
            
        elif args.repair:
            success = setup.repair_setup()
            sys.exit(0 if success else 1)
            
        elif args.auto:
            success = setup.auto_setup()
            sys.exit(0 if success else 1)
            
        else:
            success = setup.interactive_setup()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()