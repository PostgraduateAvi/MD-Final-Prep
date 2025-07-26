#!/usr/bin/env python3
"""
PDF and Excel Tokenization Script for MD Final Prep Materials

This script processes PDF files and Excel files to extract text content
and convert it into tokens suitable for language model processing.
It organizes the tokenized content by file type and source folder.
"""

import os
import sys
from pathlib import Path
import json
import logging
from typing import Dict, List, Any
import re

try:
    import PyPDF2
    import pandas as pd
    import tiktoken
except ImportError as e:
    print(f"Missing required packages. Please install: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MDTokenizer:
    """Tokenizer for MD preparation materials"""
    
    def __init__(self, base_path: str = "PDFs"):
        self.base_path = Path(base_path)
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        self.results = {
            "harrison_textbooks": [],
            "guidelines": [],
            "neurology_textbooks": [],
            "question_papers": []
        }
        
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text content from a PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num} from {pdf_path}: {e}")
                        continue
                return text
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            return ""
    
    def extract_text_from_excel(self, excel_path: Path) -> str:
        """Extract text content from an Excel file"""
        try:
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(excel_path)
            all_text = []
            
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    # Convert all data to string and join
                    sheet_text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep='\n')
                    all_text.append(f"Sheet: {sheet_name}\n{sheet_text}")
                except Exception as e:
                    logger.warning(f"Error reading sheet {sheet_name} from {excel_path}: {e}")
                    continue
            
            return "\n\n".join(all_text)
        except Exception as e:
            logger.error(f"Error reading Excel file {excel_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text for tokenization"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters except newlines
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        # Remove very long sequences of repeated characters
        text = re.sub(r'(.)\1{10,}', r'\1', text)
        
        return text.strip()
    
    def tokenize_text(self, text: str, max_tokens: int = 8192) -> List[str]:
        """Convert text to tokens with chunking for large texts"""
        if not text:
            return []
        
        tokens = self.encoding.encode(text)
        
        # If text is within token limit, return as single chunk
        if len(tokens) <= max_tokens:
            return [text]
        
        # Split into chunks
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def process_folder(self, folder_name: str, category: str) -> None:
        """Process all files in a specific folder"""
        folder_path = self.base_path / folder_name
        
        if not folder_path.exists():
            logger.warning(f"Folder {folder_path} does not exist")
            return
        
        logger.info(f"Processing {folder_name} folder...")
        
        for file_path in folder_path.glob("*"):
            if file_path.is_file():
                logger.info(f"Processing: {file_path.name}")
                
                # Extract text based on file type
                if file_path.suffix.lower() == '.pdf':
                    raw_text = self.extract_text_from_pdf(file_path)
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    raw_text = self.extract_text_from_excel(file_path)
                else:
                    logger.warning(f"Unsupported file type: {file_path}")
                    continue
                
                if not raw_text:
                    logger.warning(f"No text extracted from {file_path}")
                    continue
                
                # Clean and tokenize
                clean_text = self.clean_text(raw_text)
                text_chunks = self.tokenize_text(clean_text)
                
                # Store results
                file_info = {
                    "filename": file_path.name,
                    "file_type": file_path.suffix.lower(),
                    "original_size_bytes": file_path.stat().st_size,
                    "text_length": len(clean_text),
                    "num_chunks": len(text_chunks),
                    "total_tokens": sum(len(self.encoding.encode(chunk)) for chunk in text_chunks),
                    "chunks": text_chunks
                }
                
                self.results[category].append(file_info)
                logger.info(f"✓ {file_path.name}: {file_info['num_chunks']} chunks, {file_info['total_tokens']} tokens")
    
    def save_results(self, output_file: str = "tokenized_content.json") -> None:
        """Save tokenized results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of tokenization results"""
        summary = {
            "total_files": 0,
            "total_tokens": 0,
            "categories": {}
        }
        
        for category, files in self.results.items():
            category_tokens = sum(file_info['total_tokens'] for file_info in files)
            category_files = len(files)
            
            summary["categories"][category] = {
                "files": category_files,
                "tokens": category_tokens,
                "avg_tokens_per_file": category_tokens // category_files if category_files > 0 else 0
            }
            
            summary["total_files"] += category_files
            summary["total_tokens"] += category_tokens
        
        return summary

def main():
    """Main execution function"""
    logger.info("Starting MD Final Prep tokenization process...")
    
    # Initialize tokenizer
    tokenizer = MDTokenizer()
    
    # Process each category
    folder_mappings = {
        "Harrison_Textbooks": "harrison_textbooks",
        "Guidelines": "guidelines", 
        "Neurology_Textbooks": "neurology_textbooks",
        "Question_Papers": "question_papers"
    }
    
    for folder_name, category in folder_mappings.items():
        try:
            tokenizer.process_folder(folder_name, category)
        except Exception as e:
            logger.error(f"Error processing {folder_name}: {e}")
            continue
    
    # Save results
    tokenizer.save_results()
    
    # Generate and display summary
    summary = tokenizer.generate_summary()
    
    print("\n" + "="*60)
    print("TOKENIZATION SUMMARY")
    print("="*60)
    print(f"Total files processed: {summary['total_files']}")
    print(f"Total tokens generated: {summary['total_tokens']:,}")
    print("\nBy category:")
    for category, stats in summary["categories"].items():
        print(f"  {category.replace('_', ' ').title()}: {stats['files']} files, {stats['tokens']:,} tokens (avg: {stats['avg_tokens_per_file']:,})")
    
    print("\n✓ Tokenization completed successfully!")
    print("✓ Results saved to 'tokenized_content.json'")

if __name__ == "__main__":
    main()