#!/usr/bin/env python3
"""
MD Final Prep - Text Extraction Tool
====================================

Automatically convert all PDFs and Excel files in this repository into plain text .txt files.
Extracts full readable text and saves output to /processed/ folder maintaining folder structure.
"""

import os
import json
from pdfminer.high_level import extract_text
import pandas as pd
from pathlib import Path

def extract_text_from_pdf(file_path):
    """Extract text from PDF using pdfminer.six"""
    try:
        return extract_text(file_path)
    except Exception as e:
        return f"[ERROR reading PDF] {e}"

def extract_text_from_excel(file_path):
    """Extract text from Excel/CSV files using pandas"""
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
            content = df.to_string(index=False)
        else:
            # For Excel files, read all sheets
            df_dict = pd.read_excel(file_path, sheet_name=None)
            content = ""
            for sheet_name, sheet_data in df_dict.items():
                content += f"\n--- Sheet: {sheet_name} ---\n"
                content += sheet_data.to_string(index=False)
        return content
    except Exception as e:
        return f"[ERROR reading Excel/CSV] {e}"

def process_files(source_dir=".", output_dir="processed"):
    """Process all PDF, Excel, and CSV files in the source directory"""
    processed_count = 0
    error_count = 0
    
    print(f"🔍 Scanning {source_dir} for PDF, Excel, and CSV files...")
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith((".pdf", ".xlsx", ".xls", ".csv")):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source_dir)
                out_path = os.path.join(output_dir, rel_path + ".txt")

                # Create output directory if it doesn't exist
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                print(f"📄 Processing: {rel_path}")
                
                # Extract text based on file type
                if file.lower().endswith(".pdf"):
                    text = extract_text_from_pdf(src_path)
                else:
                    text = extract_text_from_excel(src_path)

                # Write extracted text to output file
                try:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"  ✅ Saved: {out_path}")
                    processed_count += 1
                except Exception as e:
                    print(f"  ❌ Error saving {out_path}: {e}")
                    error_count += 1
    
    return processed_count, error_count

def main():
    """Main function to process all files in the repository"""
    print("🧠 MD Final Prep - Text Extraction Tool")
    print("=" * 50)
    
    # Process specific directories and root level files
    total_processed = 0
    total_errors = 0
    
    # Process PDFs directory
    if os.path.exists("PDFs"):
        print("\n📚 Processing PDFs directory...")
        processed, errors = process_files("PDFs", "processed/PDFs")
        total_processed += processed
        total_errors += errors
    
    # Process root level files (like "Previous year paper PDF.pdf")
    print("\n📋 Processing root level files...")
    root_files = [f for f in os.listdir(".") if f.lower().endswith((".pdf", ".xlsx", ".xls", ".csv"))]
    for file in root_files:
        if os.path.isfile(file):
            rel_path = file
            out_path = os.path.join("processed", file + ".txt")
            
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            
            print(f"📄 Processing: {rel_path}")
            
            if file.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file)
            else:
                text = extract_text_from_excel(file)
            
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"  ✅ Saved: {out_path}")
                total_processed += 1
            except Exception as e:
                print(f"  ❌ Error saving {out_path}: {e}")
                total_errors += 1
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"📊 PROCESSING SUMMARY")
    print(f"✅ Successfully processed: {total_processed} files")
    if total_errors > 0:
        print(f"❌ Errors encountered: {total_errors} files")
    print(f"\n🚀 Text files are now available in the 'processed/' directory")
    print(f"🌐 They can be accessed via GitHub raw URLs:")
    print(f"   https://raw.githubusercontent.com/<username>/MD-Final-Prep/main/processed/<path>.txt")

if __name__ == "__main__":
    main()