# MD-Final-Prep
All data needed to pass my MD exam

## Repository Organization

This repository is organized following best practices for data science and ML projects, making it ideal for LLM-powered tools like CustomGPT to access and process content.

### 📁 Directory Structure

```
MD-Final-Prep/
├── scripts/                    # Python processing scripts
│   ├── simple_tokenize.py     # Main tokenization script (built-in libraries)
│   ├── tokenize_content.py    # Advanced tokenization with tiktoken
│   └── navigate_content.py    # Repository content navigator
├── data/                      # Processed outputs and structured data
│   ├── tokenized_content.json # Detailed tokenization results 
│   ├── token_summary.csv      # Summary statistics
│   ├── metadata.json          # Repository metadata and structure info
│   └── question_papers/       # Past exam papers (Excel format)
├── PDFs/                      # Medical study materials (PDF only)
│   ├── Harrison_Textbooks/    # Harrison's Internal Medicine sections
│   ├── Guidelines/            # Medical guidelines and protocols  
│   └── Neurology_Textbooks/   # Specialized neurology materials
└── .github/workflows/         # Automation and CI/CD
    └── organize_files.yml     # File organization validation
```

### 📚 Content Categories

#### PDFs/ (PDF files only)
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

#### data/ (Processed outputs and structured data)
- **question_papers/** - Past year question papers and exams (25 Excel files)
  - Basic Science papers (2016-2024)
  - Systemic Medicine papers (2017-2025)
  - Infectious Diseases papers (2019-2024)
  - Recent Advances papers (2020-2024)

## 🚀 Usage

### Content Processing
To tokenize all content and generate processed outputs:
```bash
# From repository root
python scripts/simple_tokenize.py

# Or for advanced tokenization (requires tiktoken)
python scripts/tokenize_content.py
```

### Content Navigation
To explore the repository structure:
```bash
python scripts/navigate_content.py
```

### Generated Outputs
All processed data is saved in the `data/` directory:
- `data/tokenized_content.json` - Detailed tokenization results with text chunks
- `data/token_summary.csv` - Summary statistics for all processed files
- `data/metadata.json` - Repository structure and metadata information

## 📊 Content Statistics

- **Total files**: 56 files (278 MB)
- **Tokenization output**: 19.2M tokens generated across all materials
- **Unique tokens**: 6.1M identified
- **Organization**: Structured by medical specialty for easy access

## 🔧 Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Required packages:
- PyPDF2==3.0.1 (PDF processing)
- pandas>=2.0.0 (Data manipulation)
- openpyxl>=3.1.0 (Excel file processing)  
- tiktoken>=0.5.0 (Advanced tokenization - optional)

## 🤖 LLM Integration

This repository structure is optimized for AI tools:
- **Modular organization**: Clear separation of scripts, data, and source materials
- **Metadata-rich**: `data/metadata.json` provides comprehensive structure information
- **Consistent paths**: All file references use proper relative/absolute pathing
- **Automated validation**: GitHub Actions ensure structure compliance

### For CustomGPT and Similar Tools:
1. Point to `data/` directory for processed content access
2. Use `data/metadata.json` for structure understanding
3. Reference `scripts/` for processing methodology
4. Access `PDFs/` for original source materials

## 🔄 Automation

GitHub Actions automatically validate repository organization on each push, ensuring:
- Python scripts remain in `scripts/` directory
- Processed outputs stay in `data/` directory  
- PDF directory contains only PDF files
- Repository structure follows best practices
