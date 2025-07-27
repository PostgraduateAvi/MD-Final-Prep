#!/usr/bin/env python3
"""
MD Final Prep - Content Navigator
Helps navigate the organized PDF structure and provides file information
"""

import os
from pathlib import Path
import json

def load_token_summary():
    """Load tokenization summary if available"""
    try:
        with open('tokenized_content.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def display_category_contents(category_path, category_name, token_data=None):
    """Display contents of a category with file information"""
    print(f"\n{'='*60}")
    print(f"{category_name.upper()}")
    print(f"{'='*60}")
    
    if not category_path.exists():
        print(f"Directory {category_path} not found.")
        return
    
    files = list(category_path.glob("*"))
    files.sort()
    
    if not files:
        print("No files found in this category.")
        return
    
    print(f"Total files: {len(files)}")
    
    # Get token data for this category if available
    category_key = category_name.lower().replace(' ', '_').replace('-', '_')
    category_tokens = None
    if token_data and category_key in token_data:
        category_tokens = {item['filename']: item for item in token_data[category_key]}
    
    for i, file_path in enumerate(files, 1):
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"\n{i:2d}. {file_path.name}")
        print(f"    Size: {size_mb:.1f} MB")
        
        # Add token information if available
        if category_tokens and file_path.name in category_tokens:
            token_info = category_tokens[file_path.name]
            print(f"    Tokens: {token_info['total_tokens']:,}")
            print(f"    Text length: {token_info['text_length']:,} characters")

def main():
    """Main navigation function"""
    base_path = Path("PDFs")
    
    if not base_path.exists():
        print("PDFs directory not found. Make sure you're in the correct directory.")
        return
    
    # Load tokenization data
    print("Loading tokenization data...")
    token_data = load_token_summary()
    if token_data:
        print("✓ Tokenization data loaded successfully")
    else:
        print("⚠ Tokenization data not found. Run simple_tokenize.py first for detailed info.")
    
    categories = [
        ("Harrison_Textbooks", "Harrison Textbooks"),
        ("Guidelines", "Medical Guidelines"),
        ("Neurology_Textbooks", "Neurology Textbooks"),
        ("Question_Papers", "Question Papers")
    ]
    
    print(f"\n{'='*60}")
    print("MD FINAL PREP - CONTENT NAVIGATOR")
    print(f"{'='*60}")
    
    for folder_name, display_name in categories:
        category_path = base_path / folder_name
        display_category_contents(category_path, display_name, token_data)
    
    # Display summary statistics
    if token_data:
        print(f"\n{'='*60}")
        print("SUMMARY STATISTICS")
        print(f"{'='*60}")
        
        total_files = 0
        total_tokens = 0
        total_size = 0
        
        for category_key in token_data:
            category_files = len(token_data[category_key])
            category_tokens = sum(item['total_tokens'] for item in token_data[category_key])
            category_size = sum(item['original_size_bytes'] for item in token_data[category_key])
            
            total_files += category_files
            total_tokens += category_tokens
            total_size += category_size
            
            print(f"{category_key.replace('_', ' ').title()}:")
            print(f"  Files: {category_files}")
            print(f"  Tokens: {category_tokens:,}")
            print(f"  Size: {category_size / (1024*1024):.1f} MB")
            print()
        
        print(f"TOTAL:")
        print(f"  Files: {total_files}")
        print(f"  Tokens: {total_tokens:,}")
        print(f"  Size: {total_size / (1024*1024):.1f} MB")
    
    print(f"\n{'='*60}")
    print("Use this structure to navigate and access your study materials!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()