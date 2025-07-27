#!/usr/bin/env python3
"""
Test script for text extraction functionality
"""

import os
import tempfile
import unittest
from pathlib import Path
import pandas as pd
import sys

# Add the current directory to path to import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_text import extract_text_from_excel, extract_text_from_pdf

class TestTextExtraction(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        
    def test_excel_extraction(self):
        """Test Excel text extraction"""
        # Create a simple test Excel file
        test_data = pd.DataFrame({
            'Question': ['What is the capital of France?', 'What is 2+2?'],
            'Answer': ['Paris', '4'],
            'Topic': ['Geography', 'Math']
        })
        
        test_file = os.path.join(self.test_dir, 'test.xlsx')
        test_data.to_excel(test_file, index=False)
        
        # Extract text
        extracted_text = extract_text_from_excel(test_file)
        
        # Verify content
        self.assertIn('Question', extracted_text)
        self.assertIn('Paris', extracted_text)
        self.assertIn('Geography', extracted_text)
        self.assertNotIn('[ERROR', extracted_text)
        
    def test_csv_extraction(self):
        """Test CSV text extraction"""
        # Create a simple test CSV file
        test_data = pd.DataFrame({
            'Patient_ID': [1, 2, 3],
            'Diagnosis': ['Hypertension', 'Diabetes', 'Asthma'],
            'Treatment': ['ACE inhibitors', 'Metformin', 'Inhaler']
        })
        
        test_file = os.path.join(self.test_dir, 'test.csv')
        test_data.to_csv(test_file, index=False)
        
        # Extract text
        extracted_text = extract_text_from_excel(test_file)
        
        # Verify content
        self.assertIn('Patient_ID', extracted_text)
        self.assertIn('Hypertension', extracted_text)
        self.assertIn('Metformin', extracted_text)
        self.assertNotIn('[ERROR', extracted_text)
        
    def test_processed_files_exist(self):
        """Test that processed files exist and have content"""
        processed_dir = Path('processed')
        
        if processed_dir.exists():
            txt_files = list(processed_dir.glob('**/*.txt'))
            self.assertGreater(len(txt_files), 0, "No processed text files found")
            
            # Check that files have content
            for txt_file in txt_files[:3]:  # Check first 3 files
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertGreater(len(content), 100, f"File {txt_file} has very little content")
                    self.assertNotIn('[ERROR', content, f"File {txt_file} contains extraction errors")
        else:
            self.skipTest("No processed directory found - run extract_text.py first")
    
    def test_error_handling(self):
        """Test error handling for invalid files"""
        # Test with non-existent file
        result = extract_text_from_pdf('/nonexistent/file.pdf')
        self.assertIn('[ERROR', result)
        
        result = extract_text_from_excel('/nonexistent/file.xlsx')
        self.assertIn('[ERROR', result)

if __name__ == '__main__':
    print("🧪 Testing Text Extraction Functionality")
    print("=" * 50)
    unittest.main(verbosity=2)