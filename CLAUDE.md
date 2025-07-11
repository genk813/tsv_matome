# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TSV_MATOME is a Japanese trademark search system that processes TSV (Tab-Separated Values) files from the Japan Patent Office, manages trademark data in SQLite, and provides a web-based search interface. The system handles trademark text, applicant information, rights holder data, images, and goods classification.

## Core Architecture

### Database Layer
- **Main Database**: `output.db` (SQLite) - contains 11 tables with ~270k trademark records
- **Schema**: Defined in `create_schema.sql` with 14 optimized indexes
- **Key Tables**:
  - `jiken_c_t` - Core trademark case information (primary table)
  - `standard_char_t_art`, `indct_use_t_art`, `search_use_t_art_table` - Trademark text (priority: standard → display → search)
  - `right_person_art_t` - Rights holder information (for registered trademarks)
  - `jiken_c_t_shutugannindairinin` - Applicant/agent information (by codes)
  - `goods_class_art` - Goods/services classification
  - `reg_mapping` - Critical mapping table linking application numbers to registration numbers
  - `applicant_mapping` - Partial applicant code to name mapping (573 entries with confidence levels)

### Application Layer
- **Optimized App**: `app_dynamic_join_claude_optimized.py` - Production Flask app (port 5002)
- **Alternative Servers**: 
  - `enhanced_web_server.py` - Applicant-aware version (port 8001)
  - `simple_web_test.py` - Basic HTTP server (port 8000)
- **Core Architecture**: Single-query optimization to avoid N+1 problems (95% query reduction achieved)

### Data Processing Pipeline
- **TSV Import**: `import_tsv_data_fixed.py` - Handles 34 different TSV file types from Patent Office
- **Image Processing**: `extract_images.py` - Extracts Base64 images from `t_sample` table
- **Weekly Updates**: `weekly_data_updater.py` - Incremental data updates with automatic backups

## Common Commands

### Database Operations
```bash
# Initialize fresh database
python3 init_database.py

# Build critical reg_mapping table (enables rights holder display)
python3 build_reg_mapping.py

# Create partial applicant mapping (enables some applicant name display)
python3 create_partial_applicant_mapping.py

# Test database operations
python3 test_app.py
```

### Application Servers
```bash
# Production Flask app (requires: pip install flask)
python3 app_dynamic_join_claude_optimized.py
# → http://localhost:5002

# Enhanced server with applicant support
python3 enhanced_web_server.py
# → http://localhost:8001

# Basic test server (no Flask required)
python3 simple_web_test.py
# → http://localhost:8000
```

### Data Import and Updates
```bash
# Full TSV data import (initial setup)
python3 import_tsv_data_fixed.py

# Weekly data updates
python3 weekly_data_updater.py weekly_data/YYYYMMDD/tsv --validate

# Extract images from trademark data
python3 extract_images.py
```

### Analysis and Testing
```bash
# Search functionality test
python3 test_search_functionality.py

# Trademark display coverage analysis
python3 analyze_trademark_display.py

# Applicant code analysis
python3 applicant_code_analysis.py
```

## Key Implementation Details

### Data Relationships and Mapping
- **Application vs Registration**: Complex many-to-many relationship via `reg_mapping` table
- **Applicant Information**: 
  - Codes only in `jiken_c_t_shutugannindairinin` (privacy protection)
  - Partial name mapping via `applicant_mapping` (reverse-engineered from registered trademarks)
  - Full applicant master files: `upd_appl_reg_info.tsv`, `upd_under_integ_appl_info_mgt.tsv` (external)
- **Trademark Text Priority**: Standard character → Display use → Search use (COALESCE pattern)

### Performance Optimizations
- **Single Query Strategy**: `get_optimized_results()` function consolidates multiple JOINs
- **Applicant Display Logic**: Shows actual names when available, falls back to codes with confidence levels
- **Image Handling**: Base64 detection and file serving with multiple format support

### TSV File Handling
- **Encoding Issues**: Multiple encoding detection (UTF-8, CP932, EUC-JP)
- **Column Mapping**: `shutugan_no` → `normalized_app_num`, field normalization
- **Batch Processing**: Handles large files with memory-efficient processing

### Search Architecture
- **Multi-table Search**: Searches across standard_char_t_art, indct_use_t_art, search_use_t_art_table
- **Result Enhancement**: Automatic addition of rights holder, applicant, and image information
- **Confidence Levels**: Applicant mapping includes reliability indicators (高/中/低)

## Development Workflow

### When Adding New Features
1. Check `SOLUTION_SUMMARY.md` for context and previous solutions
2. Use existing analysis scripts to understand data patterns
3. Test with `test_search_functionality.py` before deploying
4. Update `reg_mapping` or `applicant_mapping` tables if data relationships change

### When Debugging Search Issues
1. Verify `reg_mapping` table exists and is populated (build_reg_mapping.py)
2. Check applicant mapping coverage (applicant_code_analysis.py)
3. Ensure proper column name mappings in queries
4. Test individual table queries before complex JOINs

### Weekly Data Maintenance
- Use `weekly_data_updater.py` for incremental updates
- Automatic backup creation before updates
- Validate data integrity after updates
- Monitor trademark display coverage rates

## File Organization

### Core Files
- `app_dynamic_join_claude_optimized.py` - Main production application
- `create_schema.sql` - Database schema definition
- `output.db` - Main SQLite database

### Data Files
- `tsv_data/tsv/` - Source TSV files from Patent Office (34 files)
- `images/final_complete/` - Extracted trademark images
- `backups/` - Automatic database backups

### Analysis and Utilities
- `history/` - Development session logs and analysis
- `templates/` - Flask HTML templates
- Analysis scripts: `analyze_*.py`, `check_*.py`

## Environment Configuration

### Required Environment Variables
- `DB_PATH` - Database location (default: ./output.db)
- `IMAGES_DIR` - Image directory (default: ./images/final_complete)
- `SECRET_KEY` - Flask secret key

### Dependencies
- Python 3.x with sqlite3 (built-in)
- Flask (for web interface): `pip install flask`
- Standard library modules: csv, pathlib, re, logging