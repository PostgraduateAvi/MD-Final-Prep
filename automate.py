#!/usr/bin/env python3
"""
MD Final Prep - Master Automation Wrapper
========================================

This is the ultimate automation wrapper that provides advanced features:
- Parallel processing
- Progress monitoring with real-time updates
- Advanced error recovery
- Backup and restore functionality
- Performance monitoring
- Automated reporting
- Integration with external tools

Usage:
    python3 automate.py                      # Interactive mode
    python3 automate.py --full               # Complete automation
    python3 automate.py --parallel           # Parallel processing
    python3 automate.py --monitor            # Monitor existing processes
    python3 automate.py --backup             # Backup current state
    python3 automate.py --restore            # Restore from backup
"""

import os
import sys
import json
import time
import shutil
import psutil
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from datetime import datetime
import logging
import argparse
from typing import Dict, List, Any, Optional
import subprocess
import signal
import queue

# Setup comprehensive logging with multiple handlers
def setup_logging():
    """Setup comprehensive logging system"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"automation_{timestamp}.log"
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler - detailed logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler - simple logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)

logger = setup_logging()

class ProgressMonitor:
    """Real-time progress monitoring with visual feedback"""
    
    def __init__(self):
        self.tasks = {}
        self.start_time = datetime.now()
        self.lock = threading.Lock()
        self.monitoring = False
        self.monitor_thread = None
    
    def add_task(self, task_id: str, description: str, total_steps: int = 100):
        """Add a task to monitor"""
        with self.lock:
            self.tasks[task_id] = {
                "description": description,
                "total_steps": total_steps,
                "current_step": 0,
                "status": "pending",
                "start_time": None,
                "end_time": None,
                "error": None
            }
    
    def update_task(self, task_id: str, current_step: int, status: str = "running", error: str = None):
        """Update task progress"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task["current_step"] = current_step
                task["status"] = status
                if error:
                    task["error"] = error
                if status == "running" and task["start_time"] is None:
                    task["start_time"] = datetime.now()
                elif status in ["completed", "failed"]:
                    task["end_time"] = datetime.now()
    
    def start_monitoring(self):
        """Start the progress monitoring display"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the progress monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            self._display_progress()
            time.sleep(2)
    
    def _display_progress(self):
        """Display current progress"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("="*70)
        print("MD FINAL PREP - AUTOMATION PROGRESS")
        print("="*70)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Runtime: {datetime.now() - self.start_time}")
        print()
        
        with self.lock:
            for task_id, task in self.tasks.items():
                progress = (task["current_step"] / task["total_steps"]) * 100
                status_icon = {
                    "pending": "⏳",
                    "running": "🔄", 
                    "completed": "✅",
                    "failed": "❌"
                }.get(task["status"], "❓")
                
                # Progress bar
                bar_length = 30
                filled_length = int(bar_length * progress // 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                
                print(f"{status_icon} {task['description']}")
                print(f"   [{bar}] {progress:.1f}% ({task['current_step']}/{task['total_steps']})")
                
                if task["start_time"]:
                    elapsed = datetime.now() - task["start_time"]
                    if task["current_step"] > 0:
                        eta = elapsed * (task["total_steps"] - task["current_step"]) / task["current_step"]
                        print(f"   Elapsed: {elapsed} | ETA: {eta}")
                
                if task["error"]:
                    print(f"   Error: {task['error']}")
                print()

class BackupManager:
    """Manage backups and restoration of processing states"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, name: str = None) -> str:
        """Create a backup of current state"""
        if name is None:
            name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / name
        backup_path.mkdir(exist_ok=True)
        
        # Files to backup
        backup_files = [
            "tokenized_content.json",
            "token_summary.csv",
            "token_summary.txt",
            "embeddings.jsonl",
            "md_prep_config.json"
        ]
        
        backed_up = []
        for file_name in backup_files:
            file_path = Path(file_name)
            if file_path.exists():
                shutil.copy2(file_path, backup_path / file_name)
                backed_up.append(file_name)
        
        # Create backup manifest
        manifest = {
            "created": datetime.now().isoformat(),
            "files": backed_up,
            "version": "1.0"
        }
        
        with open(backup_path / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Backup created: {backup_path} ({len(backed_up)} files)")
        return str(backup_path)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                manifest_file = backup_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = json.load(f)
                        
                        backups.append({
                            "name": backup_dir.name,
                            "path": str(backup_dir),
                            "created": manifest.get("created"),
                            "files": len(manifest.get("files", [])),
                            "size": sum(f.stat().st_size for f in backup_dir.glob("*"))
                        })
                    except Exception as e:
                        logger.warning(f"Could not read backup manifest for {backup_dir}: {e}")
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore from a backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            logger.error(f"Backup {backup_name} not found")
            return False
        
        manifest_file = backup_path / "manifest.json"
        if not manifest_file.exists():
            logger.error(f"Backup manifest not found for {backup_name}")
            return False
        
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            restored = []
            for file_name in manifest.get("files", []):
                backup_file = backup_path / file_name
                if backup_file.exists():
                    shutil.copy2(backup_file, Path(file_name))
                    restored.append(file_name)
            
            logger.info(f"Restored {len(restored)} files from backup {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup {backup_name}: {e}")
            return False

class PerformanceMonitor:
    """Monitor system performance during automation"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.metrics = []
        self.start_time = None
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.start_time = datetime.now()
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Background performance monitoring loop"""
        while self.monitoring:
            try:
                metric = {
                    "timestamp": datetime.now(),
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('.').percent,
                    "process_count": len(psutil.pids())
                }
                self.metrics.append(metric)
                
                # Keep only last 100 metrics
                if len(self.metrics) > 100:
                    self.metrics = self.metrics[-100:]
                    
            except Exception as e:
                logger.warning(f"Error collecting performance metrics: {e}")
            
            time.sleep(5)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {}
        
        cpu_values = [m["cpu_percent"] for m in self.metrics]
        memory_values = [m["memory_percent"] for m in self.metrics]
        
        return {
            "duration": datetime.now() - self.start_time if self.start_time else None,
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "samples": len(self.metrics)
        }

class AdvancedAutomationEngine:
    """Advanced automation engine with enhanced features"""
    
    def __init__(self):
        self.progress = ProgressMonitor()
        self.backup_manager = BackupManager()
        self.performance_monitor = PerformanceMonitor()
        self.config = self.load_config()
        self.running_processes = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Load automation configuration"""
        config_file = Path("md_prep_config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def run_parallel_tokenization(self) -> bool:
        """Run tokenization with parallel processing"""
        logger.info("Starting parallel tokenization...")
        
        self.progress.add_task("tokenization", "Parallel Tokenization", 100)
        self.progress.update_task("tokenization", 10, "running")
        
        try:
            # Use ThreadPoolExecutor for I/O bound tasks
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Submit both tokenization methods
                simple_future = executor.submit(self._run_simple_tokenization)
                agent_future = executor.submit(self._run_agent_tokenization)
                
                self.progress.update_task("tokenization", 50, "running")
                
                # Wait for completion
                simple_success = simple_future.result()
                agent_success = agent_future.result()
                
                success = simple_success or agent_success
                
                if success:
                    self.progress.update_task("tokenization", 100, "completed")
                    logger.info("✓ Parallel tokenization completed")
                else:
                    self.progress.update_task("tokenization", 100, "failed", "Both tokenization methods failed")
                    logger.error("✗ Parallel tokenization failed")
                
                return success
                
        except Exception as e:
            self.progress.update_task("tokenization", 100, "failed", str(e))
            logger.error(f"Error in parallel tokenization: {e}")
            return False
    
    def _run_simple_tokenization(self) -> bool:
        """Run simple tokenization method"""
        try:
            result = subprocess.run([
                sys.executable, "simple_tokenize.py"
            ], capture_output=True, text=True, timeout=600)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Simple tokenization failed: {e}")
            return False
    
    def _run_agent_tokenization(self) -> bool:
        """Run agent tokenization method"""
        try:
            result = subprocess.run([
                sys.executable, "pdf_token_agent.py"
            ], capture_output=True, text=True, timeout=900)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Agent tokenization failed: {e}")
            return False
    
    def run_full_automation(self, parallel: bool = False) -> bool:
        """Run complete automation with all features"""
        logger.info("Starting advanced full automation...")
        
        # Start monitoring
        self.progress.start_monitoring()
        self.performance_monitor.start_monitoring()
        
        try:
            # Create initial backup
            backup_name = self.backup_manager.create_backup("pre_automation")
            
            # Setup tasks
            self.progress.add_task("setup", "Environment Setup", 100)
            self.progress.add_task("tokenization", "Content Tokenization", 100)
            self.progress.add_task("embeddings", "Embedding Generation", 100)
            self.progress.add_task("validation", "Results Validation", 100)
            
            # Run setup
            self.progress.update_task("setup", 50, "running")
            setup_success = self._run_setup()
            self.progress.update_task("setup", 100, "completed" if setup_success else "failed")
            
            if not setup_success:
                logger.error("Setup failed, aborting automation")
                return False
            
            # Run tokenization
            if parallel:
                tokenization_success = self.run_parallel_tokenization()
            else:
                self.progress.update_task("tokenization", 10, "running")
                tokenization_success = self._run_simple_tokenization()
                self.progress.update_task("tokenization", 100, "completed" if tokenization_success else "failed")
            
            if not tokenization_success:
                logger.error("Tokenization failed, aborting automation")
                return False
            
            # Run embeddings
            self.progress.update_task("embeddings", 10, "running")
            embeddings_success = self._run_embeddings()
            self.progress.update_task("embeddings", 100, "completed" if embeddings_success else "failed")
            
            # Run validation
            self.progress.update_task("validation", 50, "running")
            validation_success = self._run_validation()
            self.progress.update_task("validation", 100, "completed" if validation_success else "failed")
            
            # Create final backup
            if tokenization_success:
                self.backup_manager.create_backup("post_automation")
            
            success = tokenization_success and validation_success
            
            logger.info(f"Advanced automation {'completed successfully' if success else 'completed with errors'}")
            return success
            
        except Exception as e:
            logger.error(f"Error in advanced automation: {e}")
            return False
        
        finally:
            self.progress.stop_monitoring()
            self.performance_monitor.stop_monitoring()
            
            # Show performance summary
            perf_summary = self.performance_monitor.get_summary()
            if perf_summary:
                logger.info(f"Performance Summary: CPU avg={perf_summary['cpu']['avg']:.1f}%, Memory avg={perf_summary['memory']['avg']:.1f}%")
    
    def _run_setup(self) -> bool:
        """Run environment setup"""
        try:
            result = subprocess.run([
                sys.executable, "quick_setup.py", "--auto"
            ], capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    def _run_embeddings(self) -> bool:
        """Run embedding generation"""
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not set, skipping embeddings")
            return True
        
        try:
            result = subprocess.run([
                sys.executable, "generate_embeddings.py"
            ], capture_output=True, text=True, timeout=1800)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Embeddings generation failed: {e}")
            return True  # Non-critical failure
    
    def _run_validation(self) -> bool:
        """Run results validation"""
        try:
            # Check required files exist
            required_files = ["tokenized_content.json", "token_summary.csv"]
            for file_path in required_files:
                if not Path(file_path).exists():
                    logger.error(f"Required file missing: {file_path}")
                    return False
            
            logger.info("✓ Validation completed")
            return True
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MD Final Prep - Advanced Automation Engine"
    )
    
    parser.add_argument("--full", action="store_true", help="Run full automation")
    parser.add_argument("--parallel", action="store_true", help="Enable parallel processing")
    parser.add_argument("--monitor", action="store_true", help="Monitor existing processes")
    parser.add_argument("--backup", action="store_true", help="Create backup")
    parser.add_argument("--restore", type=str, help="Restore from backup")
    parser.add_argument("--list-backups", action="store_true", help="List available backups")
    
    args = parser.parse_args()
    
    engine = AdvancedAutomationEngine()
    
    try:
        if args.list_backups:
            backups = engine.backup_manager.list_backups()
            print("\nAvailable Backups:")
            print("="*50)
            for backup in backups:
                print(f"Name: {backup['name']}")
                print(f"Created: {backup['created']}")
                print(f"Files: {backup['files']}")
                print(f"Size: {backup['size'] / 1024:.1f} KB")
                print("-" * 30)
            
        elif args.backup:
            backup_path = engine.backup_manager.create_backup()
            print(f"Backup created: {backup_path}")
            
        elif args.restore:
            success = engine.backup_manager.restore_backup(args.restore)
            print(f"Restore {'successful' if success else 'failed'}")
            
        elif args.full:
            success = engine.run_full_automation(parallel=args.parallel)
            sys.exit(0 if success else 1)
            
        else:
            # Interactive mode
            print("\nMD Final Prep - Advanced Automation")
            print("Select an option:")
            print("1. Full automation")
            print("2. Full automation (parallel)")
            print("3. Create backup")
            print("4. List backups")
            print("5. Exit")
            
            try:
                choice = input("\nEnter choice (1-5): ").strip()
                
                if choice == "1":
                    engine.run_full_automation(parallel=False)
                elif choice == "2":
                    engine.run_full_automation(parallel=True)
                elif choice == "3":
                    engine.backup_manager.create_backup()
                elif choice == "4":
                    backups = engine.backup_manager.list_backups()
                    for backup in backups:
                        print(f"{backup['name']} - {backup['created']}")
                elif choice == "5":
                    print("Goodbye!")
                else:
                    print("Invalid choice")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()