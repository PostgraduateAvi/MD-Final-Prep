# MD Final Prep - Complete Automation Guide
=======================================

This repository now includes comprehensive automation tools for the complete MD Final Prep workflow. The automation system provides multiple levels of functionality from simple setup to advanced parallel processing.

## 🚀 Quick Start

### Option 1: Single Command Full Automation
```bash
python3 md_final_prep_agent.py --mode full
```

### Option 2: Interactive Setup + Automation
```bash
python3 quick_setup.py
python3 md_final_prep_agent.py --mode full
```

### Option 3: Advanced Automation with Monitoring
```bash
python3 automate.py --full --parallel
```

## 📁 Automation Scripts Overview

### 1. `md_final_prep_agent.py` - Master Automation Agent
**The primary automation script that orchestrates the entire workflow.**

Features:
- Complete dependency checking and installation
- Full content processing pipeline
- Progress tracking and comprehensive logging
- Error handling and recovery
- Multiple execution modes
- Configuration management
- Automated validation

**Usage:**
```bash
# Complete automation
python3 md_final_prep_agent.py --mode full

# Individual components
python3 md_final_prep_agent.py --mode setup
python3 md_final_prep_agent.py --mode tokenize
python3 md_final_prep_agent.py --mode embeddings
python3 md_final_prep_agent.py --mode server
python3 md_final_prep_agent.py --mode status
```

### 2. `quick_setup.py` - Automated Setup and Environment Verification
**Quick setup script for dependency management and environment preparation.**

Features:
- Automated dependency installation
- Environment verification
- Missing directory creation
- Configuration setup
- Setup repair functionality

**Usage:**
```bash
# Interactive setup
python3 quick_setup.py

# Automated setup
python3 quick_setup.py --auto

# Check current status
python3 quick_setup.py --check

# Repair broken setup
python3 quick_setup.py --repair
```

### 3. `automate.py` - Advanced Automation Engine
**Advanced automation with parallel processing, monitoring, and backup functionality.**

Features:
- Parallel processing capabilities
- Real-time progress monitoring with visual feedback
- Performance monitoring (CPU, memory, disk usage)
- Backup and restore functionality
- Advanced error recovery
- System performance tracking

**Usage:**
```bash
# Interactive mode
python3 automate.py

# Full automation
python3 automate.py --full

# Parallel processing
python3 automate.py --full --parallel

# Backup management
python3 automate.py --backup
python3 automate.py --list-backups
python3 automate.py --restore backup_name
```

## ⚙️ Configuration

### Configuration File: `md_prep_config.json`
The automation system uses a JSON configuration file for customization:

```json
{
  "base_path": "PDFs",
  "output_files": {
    "tokenized": "tokenized_content.json",
    "embeddings": "embeddings.jsonl",
    "token_summary": "token_summary.csv",
    "agent_token_summary": "token_summary.txt"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "auto_restart": true
  },
  "processing": {
    "max_retries": 3,
    "chunk_size": 512,
    "embedding_model": "text-embedding-ada-002"
  },
  "validation": {
    "min_tokens_per_file": 10,
    "max_file_size_mb": 500,
    "required_categories": [
      "harrison_textbooks",
      "guidelines",
      "neurology_textbooks",
      "question_papers"
    ]
  }
}
```

## 🔄 Complete Automation Workflow

The automation system follows this comprehensive workflow:

### Phase 1: Environment Setup
1. **Dependency Checking**: Verify Python version and required packages
2. **Installation**: Automatically install missing dependencies
3. **Directory Creation**: Create missing PDF categorization directories
4. **Configuration**: Setup default configuration files
5. **Verification**: Test all components work correctly

### Phase 2: Content Processing
1. **PDF Discovery**: Scan all PDF directories for content
2. **Text Extraction**: Extract text from PDFs using multiple methods
3. **Tokenization**: Convert text to tokens using simple or advanced methods
4. **Chunking**: Split content into manageable chunks for processing
5. **Token Analysis**: Generate comprehensive token statistics

### Phase 3: Advanced Processing (Optional)
1. **Embedding Generation**: Create OpenAI embeddings for semantic search
2. **Vector Storage**: Store embeddings in JSONL format for retrieval
3. **Index Building**: Create searchable indexes

### Phase 4: Validation and Deployment
1. **Output Validation**: Verify all outputs are generated correctly
2. **Quality Checks**: Ensure token counts and file completeness
3. **API Server**: Start FastAPI server for content access
4. **Documentation**: Generate processing reports

### Phase 5: Backup and Monitoring
1. **State Backup**: Create backups of processing states
2. **Performance Monitoring**: Track system resource usage
3. **Error Recovery**: Automatic retry and recovery mechanisms
4. **Progress Tracking**: Real-time progress visualization

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Dependencies Installation Failed
```bash
# Manual dependency installation
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Check installation
python3 quick_setup.py --check
```

#### 2. PDF Processing Errors
```bash
# Try different tokenization method
python3 md_final_prep_agent.py --mode tokenize

# Check PDF accessibility
python3 pdf_token_agent.py
```

#### 3. Embedding Generation Issues
```bash
# Set OpenAI API key
export OPENAI_API_KEY=your_api_key_here

# Run embeddings separately
python3 md_final_prep_agent.py --mode embeddings
```

#### 4. Server Won't Start
```bash
# Check port availability
python3 md_final_prep_agent.py --mode status

# Try different port in config
# Edit md_prep_config.json and change server.port
```

### Recovery Options

#### Restore from Backup
```bash
# List available backups
python3 automate.py --list-backups

# Restore specific backup
python3 automate.py --restore backup_20241127_143022
```

#### Repair Installation
```bash
# Repair setup
python3 quick_setup.py --repair

# Reset configuration
rm md_prep_config.json
python3 quick_setup.py --auto
```

## 📊 Monitoring and Logs

### Log Files
- `md_prep_automation_TIMESTAMP.log` - Main automation logs
- `logs/automation_TIMESTAMP.log` - Advanced automation logs

### Progress Monitoring
The advanced automation engine provides real-time monitoring:
- Visual progress bars for each processing phase
- CPU, memory, and disk usage tracking
- Estimated time remaining for each task
- Error reporting and recovery status

### Performance Metrics
- Processing speed (tokens per second)
- Resource utilization over time
- Task completion times
- Error rates and recovery attempts

## 🔧 Advanced Features

### Parallel Processing
```bash
# Enable parallel tokenization
python3 automate.py --full --parallel
```

### Custom Configuration
```bash
# Edit configuration
nano md_prep_config.json

# Apply changes
python3 md_final_prep_agent.py --mode status
```

### API Integration
```bash
# Start API server
python3 md_final_prep_agent.py --mode server

# Access at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## 📈 Output Files and Statistics

After successful automation, you'll have:

### Primary Outputs
- `tokenized_content.json` - Complete tokenization results with text chunks
- `token_summary.csv` - Summary statistics for all processed files
- `token_summary.txt` - Agent-generated token summary
- `embeddings.jsonl` - OpenAI embeddings for semantic search (if API key provided)

### Metadata Files
- `md_prep_config.json` - Configuration settings
- `logs/` - Comprehensive logging directory
- `backups/` - Automated backup directory

### Processing Statistics
- Total files processed: ~56 files
- Total tokens generated: ~19.2M tokens
- Unique tokens: ~6.1M tokens
- Categories: Harrison Textbooks, Guidelines, Neurology, Question Papers

## 🎯 Best Practices

### For Best Results
1. **Run setup first**: Always run `quick_setup.py` before full automation
2. **Set API keys**: Configure `OPENAI_API_KEY` for embedding generation
3. **Monitor resources**: Use advanced automation for resource monitoring
4. **Create backups**: Regular backups before major processing
5. **Check logs**: Review logs for any processing issues

### Performance Optimization
- Use parallel processing for large datasets
- Ensure adequate disk space (>2GB recommended)
- Close unnecessary applications during processing
- Use SSD storage for better I/O performance

## 🔄 Maintenance

### Regular Maintenance Tasks
```bash
# Update dependencies
python3 -m pip install --upgrade -r requirements.txt

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete

# Verify setup periodically
python3 quick_setup.py --check
```

### Backup Strategy
```bash
# Create regular backups
python3 automate.py --backup

# Schedule automated backups (example cron)
# 0 2 * * * cd /path/to/repo && python3 automate.py --backup
```

## 🆘 Support and Documentation

### Getting Help
1. Check the logs in the `logs/` directory
2. Run `python3 md_final_prep_agent.py --mode status` for current state
3. Use `python3 quick_setup.py --check` for environment verification
4. Review configuration in `md_prep_config.json`

### Additional Resources
- `README.md` - Repository overview
- `PDF_TOKEN_AGENT_SETUP.md` - Original agent documentation
- `openapi.yaml` - API specification
- Individual script help: `python3 script_name.py --help`

---

## Summary

The MD Final Prep automation system provides three levels of automation:

1. **Basic**: `md_final_prep_agent.py` - Reliable, comprehensive automation
2. **Setup**: `quick_setup.py` - Environment preparation and verification  
3. **Advanced**: `automate.py` - Full-featured with monitoring and parallel processing

Choose the level that best fits your needs and system capabilities. All scripts are designed to work together and provide a complete automation solution for medical study preparation materials.