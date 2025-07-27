#!/usr/bin/env python3
"""
PDF Token Agent - GitHub API-based PDF Text Extraction and Tokenization

This agent script automatically scans every PDF file in the PDFs/Harrison_Textbooks 
directory of this repository via GitHub API, extracts all text, tokenizes every 
individual word, builds a token summary covering all unique words found, and outputs 
the complete token summary to token_summary.txt at the repository root.

Requirements:
- PyPDF2>=3.0.1 (for PDF text extraction)
- requests (for GitHub API access, usually pre-installed)

Installation:
    pip install PyPDF2==3.0.1

Usage:
    python3 pdf_token_agent.py
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Set, List
import requests
import base64
from io import BytesIO

try:
    import PyPDF2
except ImportError:
    print("ERROR: PyPDF2 is required but not installed.")
    print("Please install it with: pip install PyPDF2==3.0.1")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFTokenAgent:
    """Agent to extract and tokenize PDF content via GitHub API"""
    
    def __init__(self, repo_owner: str = "PostgraduateAvi", repo_name: str = "MD-Final-Prep"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_api_base = "https://api.github.com"
        self.harrison_path = "PDFs/Harrison_Textbooks"
        self.all_tokens = set()  # Use set to automatically handle uniqueness
        
    def get_github_repo_contents(self, path: str) -> List[dict]:
        """Get repository contents via GitHub API"""
        url = f"{self.github_api_base}/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error accessing GitHub API: {e}")
            return []
    
    def download_file_content(self, download_url: str) -> bytes:
        """Download file content from GitHub"""
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading file: {e}")
            return b''
    
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes, filename: str) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num} from {filename}: {e}")
                    continue
            
            return text
        except Exception as e:
            logger.error(f"Error reading PDF {filename}: {e}")
            return ""
    
    def tokenize_words(self, text: str) -> Set[str]:
        """Extract individual words from text"""
        if not text:
            return set()
        
        # Convert to lowercase for consistent tokenization
        text = text.lower()
        
        # Extract words using regex - only alphabetic characters
        # This matches the requirement for "individual words"
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Filter out very short words (less than 2 characters) and very long ones (likely noise)
        words = [word for word in words if 2 <= len(word) <= 50]
        
        return set(words)
    
    def process_harrison_pdfs(self) -> None:
        """Process all PDF files in Harrison_Textbooks directory"""
        logger.info(f"Accessing GitHub repository: {self.repo_owner}/{self.repo_name}")
        logger.info(f"Scanning directory: {self.harrison_path}")
        
        # Get directory contents from GitHub API
        contents = self.get_github_repo_contents(self.harrison_path)
        
        if not contents:
            logger.error(f"Could not access {self.harrison_path} directory via GitHub API")
            return
        
        pdf_files = [item for item in contents if item['name'].lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.harrison_path}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            filename = pdf_file['name']
            download_url = pdf_file['download_url']
            
            logger.info(f"Processing: {filename}")
            
            # Download PDF content
            pdf_bytes = self.download_file_content(download_url)
            
            if not pdf_bytes:
                logger.warning(f"Could not download {filename}")
                continue
            
            # Extract text from PDF
            text = self.extract_text_from_pdf_bytes(pdf_bytes, filename)
            
            if not text:
                logger.warning(f"No text extracted from {filename}")
                continue
            
            # Tokenize words
            words = self.tokenize_words(text)
            
            if words:
                self.all_tokens.update(words)
                logger.info(f"✓ {filename}: extracted {len(words)} unique words")
            else:
                logger.warning(f"No words extracted from {filename}")
    
    def save_token_summary(self, output_file: str = "token_summary.txt") -> None:
        """Save token summary to text file"""
        try:
            # Sort tokens alphabetically for consistent output
            sorted_tokens = sorted(self.all_tokens)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Token Summary - Harrison's Textbooks PDF Collection\n")
                f.write(f"# Generated by PDF Token Agent\n")
                f.write(f"# Total unique words: {len(sorted_tokens)}\n")
                f.write(f"# Repository: {self.repo_owner}/{self.repo_name}\n")
                f.write(f"# Source directory: {self.harrison_path}\n")
                f.write(f"#\n")
                f.write(f"# Unique words (alphabetically sorted):\n")
                f.write(f"#\n\n")
                
                # Write each unique word on a separate line
                for token in sorted_tokens:
                    f.write(f"{token}\n")
            
            logger.info(f"Token summary saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving token summary: {e}")
    
    def generate_summary_stats(self) -> dict:
        """Generate summary statistics"""
        return {
            "total_unique_words": len(self.all_tokens),
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "source_directory": self.harrison_path
        }

def main():
    """Main execution function"""
    print("="*70)
    print("PDF TOKEN AGENT - Harrison's Textbooks")
    print("="*70)
    print("GitHub API-based PDF text extraction and word tokenization")
    print()
    
    # Check if we're in the right directory
    if not Path("PDFs").exists():
        logger.error("PDFs directory not found. Please run this script from the repository root.")
        sys.exit(1)
    
    # Initialize agent
    agent = PDFTokenAgent()
    
    try:
        # Process PDFs via GitHub API
        agent.process_harrison_pdfs()
        
        # Generate summary statistics
        stats = agent.generate_summary_stats()
        
        if stats["total_unique_words"] == 0:
            logger.error("No words were extracted. Please check the PDF files and GitHub API access.")
            sys.exit(1)
        
        # Save token summary
        agent.save_token_summary()
        
        # Display results
        print("\n" + "="*70)
        print("PROCESSING COMPLETED")
        print("="*70)
        print(f"Repository: {stats['repository']}")
        print(f"Source directory: {stats['source_directory']}")
        print(f"Total unique words extracted: {stats['total_unique_words']:,}")
        print(f"Output file: token_summary.txt")
        print()
        print("✓ Token summary successfully generated!")
        print("✓ All unique words from Harrison's Textbooks PDFs have been saved.")
        print()
        print("The token_summary.txt file contains all unique words found in the PDF collection,")
        print("sorted alphabetically for easy reference and further processing.")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()