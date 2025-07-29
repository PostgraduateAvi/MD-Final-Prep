# MD-Final-Prep
All data needed to pass my MD exam

## 🚀 Quick Start - New Users Start Here

**Get started in 5 minutes:**
1. **Install dependencies:** `pip install -r requirements.txt`
2. **Run automation:** `python3 run_full_automation.py`
3. **Launch web app:** `python3 app.py`
4. **Access interfaces:**
   - 🌐 **Web Interface:** `http://localhost:7860` (User-friendly study interface)
   - 📊 **API Documentation:** `http://localhost:8001/docs` (Developer API)
5. **Need help?** See [📚 Documentation Index](DOCUMENTATION_INDEX.md) for complete navigation

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

## 🌐 Web Interface

**NEW: User-Friendly Study Interface**

Launch the intuitive web interface for easy access to your study materials:

```bash
# Start the web app (automatically starts API server)
python3 app.py
```

**Access at:** `http://localhost:7860`

### 🎯 Web App Features

- **📚 Content Search**: Find medical topics and relevant study materials
- **📋 Topic Summaries**: Generate high-yield study points automatically  
- **🎯 Exam Predictions**: AI-powered predictions of likely exam topics
- **🔧 Server Status**: Monitor system health and troubleshoot issues
- **📱 Mobile-Friendly**: Responsive design works on all devices

### 🛠️ Web App Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the app:**
   ```bash
   python3 app.py
   ```

3. **Access the interface:**
   - Open browser to `http://localhost:7860`
   - The API server will start automatically
   - If issues occur, manually start API: `python3 md_exam_prep_api.py`

---

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

## 🧪 Testing

### Automated Testing (CI/CD)

This repository includes automated testing via GitHub Actions that runs on every push and pull request:

- **Component Tests**: Verify all automation scripts work correctly
- **API Tests**: Validate FastAPI endpoints and responses  
- **Integration Tests**: Test complete workflow functionality
- **Cross-Platform**: Tests run on Python 3.11 and 3.12

### Manual Testing

Run tests locally to verify everything works:

```bash
# Test automation components
python3 test_automation.py

# Test API endpoints  
python3 test_md_exam_prep_api.py

# Test text extraction (may have known issues)
python3 test_extract_text.py

# Run with pytest (optional)
pytest test_*.py
```

### Expected Test Results

- ✅ **Automation Tests**: Should pass (3/3 component tests, 4/4 file tests)
- ✅ **API Tests**: Should pass (5/5 endpoint tests) 
- ⚠️ **Text Extraction**: May have some failures due to PDF parsing issues (this is expected)

---

## 🎯 Features

- **🔧 Automated Setup**: Dependency checking and installation
- **🌐 Web Interface**: User-friendly Gradio app for easy content access
- **📊 Progress Monitoring**: Real-time progress with visual feedback
- **🔄 Parallel Processing**: Multi-threaded content processing
- **💾 Backup & Restore**: Automatic state management
- **🛠️ Error Recovery**: Robust error handling and retry mechanisms
- **📈 Performance Monitoring**: System resource tracking
- **🌐 API Integration**: RESTful API for content access
- **📝 Comprehensive Logging**: Detailed operation logs
- **🧪 Automated Testing**: GitHub Actions CI/CD pipeline

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

The FastAPI server (`server.py`) exposes endpoints for:
- File listing and categorization
- Tokenization data retrieval
- Embedding generation
- Content navigation

API documentation available at `http://localhost:8000/docs` when server is running.

---

## 📚 Documentation

- **[📚 Documentation Index](DOCUMENTATION_INDEX.md)** - Complete navigation guide
- **[📊 Documentation Analysis](DOCUMENTATION_ANALYSIS.md)** - Comprehensive review of all documentation
- **[🚀 Usability Improvements](USABILITY_IMPROVEMENTS.md)** - Enhancement recommendations
