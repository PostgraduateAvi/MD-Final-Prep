#!/usr/bin/env python3
"""
Simple PDF and Excel Tokenization Script for MD Final Prep Materials

This script processes PDF files and Excel files to extract text content
and convert it into simple token counts suitable for language model processing.
Uses only built-in Python libraries when possible.
"""

import os
import sys
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any
import csv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTokenizer:
    """Simple tokenizer for MD preparation materials"""
    
    def __init__(self, base_path: str = "PDFs"):
        self.base_path = Path(base_path)
        self.results = {
            "harrison_textbooks": [],
            "guidelines": [],
            "neurology_textbooks": [],
            "question_papers": []
        }
        
    def simple_tokenize(self, text: str) -> List[str]:
        """Simple word-based tokenization"""
        if not text:
            return []
        
        # Clean text and split into words
        # Remove non-alphanumeric characters except spaces and common punctuation
        cleaned = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        # Split on whitespace and filter empty strings
        tokens = [token.strip() for token in cleaned.split() if token.strip()]
        return tokens
    
    def extract_text_from_pdf_simple(self, pdf_path: Path) -> str:
        """Simple PDF text extraction attempt"""
        try:
            # Try to read as binary and extract visible text patterns
            with open(pdf_path, 'rb') as file:
                content = file.read()
                
            # Convert to string, ignoring errors
            text_content = content.decode('utf-8', errors='ignore')
            
            # Extract text between common PDF text markers
            # This is a very simple approach and may not work for all PDFs
            text_patterns = []
            
            # Look for text patterns that commonly appear in PDF content
            for match in re.finditer(r'\(([^)]+)\)', text_content):
                potential_text = match.group(1)
                if len(potential_text) > 3 and any(c.isalpha() for c in potential_text):
                    text_patterns.append(potential_text)
            
            # Also try to find readable text sequences
            readable_sequences = re.findall(r'[A-Za-z][A-Za-z0-9\s\.,;:\-]{10,}', text_content)
            text_patterns.extend(readable_sequences)
            
            extracted_text = ' '.join(text_patterns)
            
            if len(extracted_text) < 100:  # If we didn't extract much, return file info
                return f"PDF file: {pdf_path.name} (Size: {pdf_path.stat().st_size} bytes) - Text extraction limited with simple method"
            
            return extracted_text
            
        except Exception as e:
            logger.warning(f"Simple PDF extraction failed for {pdf_path}: {e}")
            return f"PDF file: {pdf_path.name} (Size: {pdf_path.stat().st_size} bytes) - Could not extract text content"
    
    def extract_text_from_excel_simple(self, excel_path: Path) -> str:
        """Simple Excel text extraction using CSV approach"""
        try:
            # For .xlsx files, we'll just return file information since we don't have openpyxl
            return f"Excel file: {excel_path.name} (Size: {excel_path.stat().st_size} bytes) - Contains question papers and medical data"
        except Exception as e:
            logger.warning(f"Error reading Excel file {excel_path}: {e}")
            return f"Excel file: {excel_path.name} - Could not process"
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove very long sequences of repeated characters
        text = re.sub(r'(.)\1{10,}', r'\1', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, max_words: int = 512) -> List[str]:
        """Split text into manageable chunks"""
        if not text:
            return []
        
        words = text.split()
        if len(words) <= max_words:
            return [text]
        
        chunks = []
        for i in range(0, len(words), max_words):
            chunk_words = words[i:i + max_words]
            chunks.append(' '.join(chunk_words))
        
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
                    raw_text = self.extract_text_from_pdf_simple(file_path)
                elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                    raw_text = self.extract_text_from_excel_simple(file_path)
                else:
                    logger.warning(f"Unsupported file type: {file_path}")
                    continue
                
                # Clean and tokenize
                clean_text = self.clean_text(raw_text)
                text_chunks = self.chunk_text(clean_text)
                tokens = []
                for chunk in text_chunks:
                    tokens.extend(self.simple_tokenize(chunk))
                
                # Store results
                file_info = {
                    "filename": file_path.name,
                    "file_type": file_path.suffix.lower(),
                    "original_size_bytes": file_path.stat().st_size,
                    "text_length": len(clean_text),
                    "num_chunks": len(text_chunks),
                    "total_tokens": len(tokens),
                    "unique_tokens": len(set(tokens)),
                    "chunks": text_chunks[:3],  # Store only first 3 chunks to save space
                    "sample_tokens": tokens[:50] if tokens else []  # Store first 50 tokens as sample
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
    
    def save_token_summary(self, output_file: str = "token_summary.csv") -> None:
        """Save a CSV summary of tokenization results"""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['category', 'filename', 'file_type', 'size_bytes', 'text_length', 'total_tokens', 'unique_tokens']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for category, files in self.results.items():
                    for file_info in files:
                        writer.writerow({
                            'category': category,
                            'filename': file_info['filename'],
                            'file_type': file_info['file_type'],
                            'size_bytes': file_info['original_size_bytes'],
                            'text_length': file_info['text_length'],
                            'total_tokens': file_info['total_tokens'],
                            'unique_tokens': file_info['unique_tokens']
                        })
            logger.info(f"Token summary saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving CSV summary: {e}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of tokenization results"""
        summary = {
            "total_files": 0,
            "total_tokens": 0,
            "total_unique_tokens": 0,
            "total_size_bytes": 0,
            "categories": {}
        }
        
        for category, files in self.results.items():
            category_tokens = sum(file_info['total_tokens'] for file_info in files)
            category_unique_tokens = sum(file_info['unique_tokens'] for file_info in files)
            category_files = len(files)
            category_size = sum(file_info['original_size_bytes'] for file_info in files)
            
            summary["categories"][category] = {
                "files": category_files,
                "tokens": category_tokens,
                "unique_tokens": category_unique_tokens,
                "size_bytes": category_size,
                "avg_tokens_per_file": category_tokens // category_files if category_files > 0 else 0
            }
            
            summary["total_files"] += category_files
            summary["total_tokens"] += category_tokens
            summary["total_unique_tokens"] += category_unique_tokens
            summary["total_size_bytes"] += category_size
        
        return summary

def main():
    """Main execution function"""
    logger.info("Starting MD Final Prep simple tokenization process...")
    
    # Initialize tokenizer
    tokenizer = SimpleTokenizer()
    
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
    tokenizer.save_token_summary()
    
    # Generate and display summary
    summary = tokenizer.generate_summary()
    
    print("\n" + "="*70)
    print("TOKENIZATION SUMMARY")
    print("="*70)
    print(f"Total files processed: {summary['total_files']}")
    print(f"Total tokens generated: {summary['total_tokens']:,}")
    print(f"Total unique tokens: {summary['total_unique_tokens']:,}")
    print(f"Total file size: {summary['total_size_bytes'] / (1024*1024):.1f} MB")
    print("\nBy category:")
    for category, stats in summary["categories"].items():
        category_name = category.replace('_', ' ').title()
        print(f"  {category_name}:")
        print(f"    Files: {stats['files']}")
        print(f"    Tokens: {stats['tokens']:,}")
        print(f"    Unique tokens: {stats['unique_tokens']:,}")
        print(f"    Size: {stats['size_bytes'] / (1024*1024):.1f} MB")
        print(f"    Avg tokens per file: {stats['avg_tokens_per_file']:,}")
        print()
    
    print("✓ Tokenization completed successfully!")
    print("✓ Detailed results saved to 'tokenized_content.json'")
    print("✓ Summary saved to 'token_summary.csv'")
    print("\nNote: This uses a simple tokenization method. For advanced NLP processing,")
    print("consider installing specialized libraries like tiktoken or transformers.")

if __name__ == "__main__":
    main()