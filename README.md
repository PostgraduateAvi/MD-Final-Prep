# MD-Final-Prep
All data needed to pass my MD exam

## Repository Organization

This repository contains organized medical study materials with the following structure:

### PDFs/
- **Harrison_Textbooks/** - Harrison's Internal Medicine textbook sections (10 PDFs)
  - Cardiology, Nephrology, Endocrinology, Gastroenterology, Neurology
  - Haematology, Rheumatology, Respiratory System, General Medicine
  - Infectious Diseases

- **Guidelines/** - Medical guidelines and protocols (13 PDFs)
  - ADA (American Diabetes Association) guidelines
  - KDIGO (Kidney Disease: Improving Global Outcomes) guidelines
  - IDSA (Infectious Diseases Society of America) guidelines

- **Neurology_Textbooks/** - Specialized neurology study materials (8 PDFs)
  - Motor System, Cranial Nerves, Cortical Functions
  - Brainstem and Cranial Nerve Syndromes, Autonomous Nervous System
  - Coordination and Gait, General Neurology, Archit Neurology Section

- **Question_Papers/** - Past year question papers and exams (25 Excel files)
  - Basic Science papers (2016-2024)
  - Systemic Medicine papers (2017-2025)
  - Infectious Diseases papers (2019-2024)
  - Recent Advances papers (2020-2024)

## Tokenization

The repository includes scripts to convert PDF and Excel content into tokens suitable for language model processing:

- `simple_tokenize.py` - Main tokenization script using built-in Python libraries
- `tokenize_content.py` - Advanced tokenization script (requires additional dependencies)
- `requirements.txt` - Python package dependencies

### Usage

To tokenize all content:
```bash
python3 simple_tokenize.py
```

This generates:
- `tokenized_content.json` - Detailed tokenization results with text chunks
- `token_summary.csv` - Summary statistics for all processed files

### Tokenization Summary

Total processed: 56 files (278 MB)
- **19.2M tokens** generated across all materials
- **6.1M unique tokens** identified
- Organized by category for easy language model training/fine-tuning
