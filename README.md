# MD-Final-Prep
All data needed to pass my MD exam

## 🚀 Quick Start - New Users Start Here

**Get started in 5 minutes:**
1. Run: `python3 run_full_automation.py`
2. Access API: `http://localhost:8001/docs`
3. **Need help?** See [📚 Documentation Index](DOCUMENTATION_INDEX.md) for complete navigation

---

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

## 🤖 Complete Automation System

This repository now includes a comprehensive automation system that handles the entire MD Final Prep workflow with minimal user interaction.

### 🚀 Quick Start - One Command Automation

```bash
# Complete automation - just run this!
python3 run_full_automation.py
```

This single command will:
- ✅ Verify environment and install dependencies
- ✅ Process all PDF and Excel files 
- ✅ Generate comprehensive tokenization
- ✅ Create embeddings (if OpenAI API key available)
- ✅ Start API server for content access
- ✅ Provide detailed progress monitoring

### 📚 Automation Scripts

#### 1. `run_full_automation.py` - One-Command Solution
**The simplest way to run everything:**
```bash
python3 run_full_automation.py           # Complete automation
python3 run_full_automation.py --quick   # Setup only
python3 run_full_automation.py --server-only  # Start server only
```

#### 2. `md_final_prep_agent.py` - Master Automation Agent
**Comprehensive automation with detailed control:**
```bash
python3 md_final_prep_agent.py --mode full       # Full automation
python3 md_final_prep_agent.py --mode tokenize   # Tokenization only
python3 md_final_prep_agent.py --mode embeddings # Embeddings only
python3 md_final_prep_agent.py --mode server     # API server
python3 md_final_prep_agent.py --mode status     # Show status
```

#### 3. `quick_setup.py` - Environment Setup
**Automated setup and verification:**
```bash
python3 quick_setup.py --auto    # Automated setup
python3 quick_setup.py --check   # Check status
python3 quick_setup.py --repair  # Repair issues
```

#### 4. `automate.py` - Advanced Automation
**Advanced features with monitoring:**
```bash
python3 automate.py --full --parallel  # Parallel processing
python3 automate.py --backup           # Create backup
python3 automate.py --monitor          # Monitor processes
```

### ⚙️ Features

- **🔧 Automated Setup**: Dependency checking and installation
- **📊 Progress Monitoring**: Real-time progress with visual feedback
- **🔄 Parallel Processing**: Multi-threaded content processing
- **💾 Backup & Restore**: Automatic state management
- **🛠️ Error Recovery**: Robust error handling and retry mechanisms
- **📈 Performance Monitoring**: System resource tracking
- **🌐 API Integration**: RESTful API for content access
- **📝 Comprehensive Logging**: Detailed operation logs

## Traditional Processing (Manual)

For manual control, the individual scripts are still available:

### Tokenization

- `simple_tokenize.py` - Main tokenization script using built-in Python libraries
- `tokenize_content.py` - Advanced tokenization script (requires additional dependencies)
- `pdf_token_agent.py` - GitHub API-based PDF processing

### Manual Usage

```bash
# Manual tokenization
python3 simple_tokenize.py

# PDF agent processing
python3 pdf_token_agent.py

# Generate embeddings (requires OPENAI_API_KEY)
python3 generate_embeddings.py

# Start API server
python3 server.py

# Navigate content
python3 navigate_content.py
```

### Processing Results

Total processed: 56 files (278 MB)
- **19.2M tokens** generated across all materials
- **6.1M unique tokens** identified
- Organized by category for easy language model training/fine-tuning

### Output Files

After automation completes, you'll have:
- `tokenized_content.json` - Detailed tokenization results with text chunks
- `token_summary.csv` - Summary statistics for all processed files  
- `token_summary.txt` - Agent-generated comprehensive token summary
- `embeddings.jsonl` - OpenAI embeddings for semantic search (if API key provided)

### API Server

The FastAPI server (`server.py`) now ships the complete evidence explorer stack:

- `GET /` serves the front-end single page app from `frontend/`
- `GET /api/search` provides identifier-aware evidence cards with optional DOI verification
- `GET /api/topics` lists available topic filters for the UI
- Legacy automation endpoints for tokenization and embeddings remain available

To start the stack locally:

```bash
python3 -m pip install -r requirements.txt
uvicorn server:app --reload
```

Open `http://localhost:8000` to interact with the explorer UI or `http://localhost:8000/docs` for the interactive API documentation.

> **Tip:** Set `ENABLE_DOI_NETWORK_CHECKS=1` before launching the server to perform live HEAD requests against `doi.org`. When the variable is omitted, deterministic in-repo verification flags drive the DOI/PMID fallback logic so the UI stays responsive offline.

---

## 📚 Documentation

- **[📚 Documentation Index](DOCUMENTATION_INDEX.md)** - Complete navigation guide
- **[📊 Documentation Analysis](DOCUMENTATION_ANALYSIS.md)** - Comprehensive review of all documentation
- **[🚀 Usability Improvements](USABILITY_IMPROVEMENTS.md)** - Enhancement recommendations
