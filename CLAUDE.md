# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Purpose** — TMCloud-specific guide that extends CLAUDE_BASE.md principles for autonomous yet safe development.

---

## TL;DR (TMCloud Specifics)

* ✅ **Database first**: Always verify database state with `python3 autonomous_system_launcher.py status`
* 📐 **Single-query optimization**: Use JOINs to avoid N+1 problems in search functions
* 🧪 **Test with CLI first**: Validate search logic with `cli_trademark_search.py` before web implementation
* ⛔ **Never** modify core TSV import logic without backup and comprehensive testing
* 🛑 **Escalate** when: database corruption risk • search performance regression > 1s • data quality score < 90

---

## Project Overview

TMCloud (formerly tsv_matome) is a comprehensive Japanese trademark search system that processes TSV files from the Japan Patent Office. It provides both web-based and command-line search interfaces with advanced search capabilities, automated testing, and self-improvement features.

## Core Architecture

### Database Layer
- **Main Database**: `output.db` (SQLite, ~288MB)
- **Schema**: Defined in `create_schema.sql` and `scripts/phase2_schema.sql`
- **31+ tables** with 450,000+ total records
- **43+ optimized indexes** for performance
- **Unified search view** combining domestic and international trademarks (2,018,919+ records)

### Key Database Tables
- `jiken_c_t` - Core trademark case information (22,227+ records)
- `standard_char_t_art`, `indct_use_t_art`, `search_use_t_art_table` - Trademark text data
- `right_person_art_t` - Rights holder information 
- `goods_class_art` - Goods/services classification (30,582 records)
- `reg_mapping` - Application to registration number mapping (33,764 mappings)
- `t_sample` - Trademark image data (Base64 encoded)
- International trademark tables for Madrid Protocol data

## Key Commands

### System Operations
```bash
# System status check and diagnostics
python3 autonomous_system_launcher.py status

# Database initialization (creates schema and indexes)
python3 init_database.py

# Import all TSV data files (77+ files)
python3 import_tsv_data_fixed.py

# Build critical application-to-registration mapping
python3 build_reg_mapping.py

# Extract trademark images from database
python3 extract_images_no_pandas.py
```

### Search and Testing
```bash
# High-performance CLI search (unified domestic/international)
python3 cli_trademark_search.py

# Enhanced CLI search with TM-SONAR compliance
python3 cli_trademark_search_enhanced.py

# Comprehensive system testing
python3 comprehensive_search_test.py

# Performance benchmarking
python3 performance_benchmark.py
```

### Web Application
```bash
# Production web server (port 5002)
python3 app_dynamic_join_claude_optimized.py

# Enhanced web interface with modern styling
python3 enhanced_web_server.py
```

### Data Maintenance
```bash
# Weekly data updates with automatic backups
python3 weekly_data_updater.py

# Database optimization and duplicate removal
python3 database_optimization.py

# Applicant master data import
python3 import_applicant_master_data.py
```

## Critical Development Patterns

### Single-Query Optimization
Always use single-query patterns to avoid N+1 problems. Example:
```python
# Good - single query with JOIN
query = """
SELECT jiken.*, standard.*, goods.*
FROM jiken_c_t jiken
LEFT JOIN standard_char_t_art standard ON jiken.app_num = standard.app_num
LEFT JOIN goods_class_art goods ON jiken.app_num = goods.app_num
WHERE jiken.app_num = ?
"""

# Bad - multiple queries causing N+1 problem
for row in basic_results:
    standard_info = get_standard_info(row['app_num'])  # Additional query
    goods_info = get_goods_info(row['app_num'])        # Additional query
```

### Normalized Application Numbers
Always use normalized application number format (`normalized_app_num`):
```python
# Convert user input to normalized format
normalized_app_num = app_num.replace('-', '').replace('商願', '').replace('商標登録', '')
```

### Text Processing
Use `TextNormalizer` for TM-SONAR compliant text processing:
```python
from text_normalizer import TextNormalizer

normalizer = TextNormalizer()
# P1 basic normalization
normalized_text = normalizer.normalize_text(text, level='basic')
# P2 pronunciation matching
pronunciation = normalizer.normalize_text(text, level='pronunciation')
# Trademark-specific normalization
trademark_text = normalizer.normalize_text(text, level='trademark')
```

## Application Structure

### Main Application Files
- **`app_dynamic_join_claude_optimized.py`** - Production Flask web application
  - Modern web interface with responsive design
  - Optimized single-query pattern implementation
  - Image serving and trademark display features
  - Pagination and advanced search filters

### CLI Search Tools
- **`cli_trademark_search.py`** - High-performance command-line interface
  - Unified search for domestic and international trademarks
  - Multiple search types (application number, mark text, goods classes, etc.)
  - Duplicate elimination and optimized queries

### Data Processing Pipeline
- **`import_tsv_data_fixed.py`** - Handles 77+ different TSV file types
- **`scripts/import_phase2_international_trademarks.py`** - International trademark data
- **`build_reg_mapping.py`** - Creates critical mapping between application and registration numbers

### Testing Infrastructure
- **`comprehensive_search_test.py`** - Tests various search patterns and scenarios
- **`test_results/`** - Directory containing test execution results in JSON format
- **`autonomous_system_launcher.py`** - Unified testing and operation launcher

## Web Application Components

### Templates (Jinja2)
Located in `templates/` directory:
- **`base_enhanced.html`** - Enhanced template with modern styling
- **`index_enhanced.html`** - Enhanced search interface
- **`detail.html`** - Individual trademark details

### Static Files
- **`static/style.css`** - Modern CSS with gradient backgrounds, card designs, and responsive layout
- Color scheme: Indigo/purple gradients with professional styling
- Mobile-responsive design with CSS Grid/Flexbox

## Database Schema Patterns

### Core Tables Structure
```sql
-- Core trademark case information
CREATE TABLE jiken_c_t (
    app_num TEXT PRIMARY KEY,
    app_date TEXT,
    app_name TEXT,
    -- ... additional fields
);

-- Trademark text data
CREATE TABLE standard_char_t_art (
    app_num TEXT,
    standard_char_name TEXT,
    -- ... additional fields
);

-- Goods classification
CREATE TABLE goods_class_art (
    app_num TEXT,
    goods_class_no TEXT,
    goods_name TEXT,
    -- ... additional fields
);
```

### Performance Indexes
The system uses 43+ optimized indexes. Key patterns:
```sql
-- Composite indexes for common search patterns
CREATE INDEX idx_jiken_app_name ON jiken_c_t(app_name);
CREATE INDEX idx_standard_char_name ON standard_char_t_art(standard_char_name);
CREATE INDEX idx_goods_class_composite ON goods_class_art(goods_class_no, goods_name);
```

## Data Quality and Integrity

### Current System Status (A-Grade)
- **Database size**: 275MB (optimized and deduplicated)
- **Search performance**: All patterns complete in <1 second
- **Data quality**: 94/100 overall score with 97.3% coverage
- **Duplicate resolution**: Fixed 2041x duplication issues

### Critical Data Relationships
- `jiken_c_t` (core cases) ↔ `standard_char_t_art` (text data)
- `jiken_c_t` ↔ `goods_class_art` (goods classification)
- `jiken_c_t` ↔ `reg_mapping` (application to registration mapping)
- `t_sample` contains Base64 encoded trademark images

## Development Workflow (TMCloud-Specific)

### Branch Strategy
- **Branch naming**: `feat/search-<feature>`, `fix/db-<issue>`, `chore/optimize-<component>`
- **TMCloud-specific prefixes**: `data/`, `search/`, `web/`, `cli/`, `test/`

### Before Development
1. **Verify database state**: `python3 autonomous_system_launcher.py status`
2. **Check recent test results**: Review `test_results/` directory
3. **Understand current data quality**: Check improvement history
4. **Create feature branch**: Follow conventional naming with TMCloud prefixes

### During Development
1. **Use single-query optimization patterns** (critical for performance)
2. **Follow normalized application number format** (`normalized_app_num`)
3. **Leverage TextNormalizer for text processing** (TM-SONAR compliance)
4. **Test with CLI tools before web implementation**
5. **Keep commits ≤ 200 LOC** for reviewability
6. **Write tests for search functions** with expected result counts

### After Development
1. **Run comprehensive tests**: `python3 comprehensive_search_test.py`
2. **Verify performance**: `python3 performance_benchmark.py`
3. **Check data quality score**: Must maintain ≥ 90/100
4. **Update documentation**: Maintain improvement history
5. **CI must be green** before requesting review

### Commit Message Format (TMCloud)
```
type(scope): brief summary

Examples:
feat(search): add fuzzy matching for trademark names
fix(db): resolve duplicate entries in Sony search results
perf(cli): optimize goods classification query performance
test(web): add integration tests for image serving

Longer description if required.
Fixes #123
```

## Autonomous System Features

### Self-Improvement System
- **`autonomous_system_launcher.py`** - Main system launcher
- **`analyze_current_state.py`** - System diagnostics and analysis
- **`analyze_coverage_gaps.py`** - Data quality assessment
- **`performance_benchmark.py`** - Performance measurement and optimization

### Autonomous Operations
- Status monitoring and reporting
- Automated search testing
- Performance optimization
- Data integrity checks
- Continuous improvement cycles

## Recent Critical Fixes (2025-07-13)

- ✅ Resolved duplicate display issue (2041x improvement)
- ✅ Fixed Sony search from 0→2 accurate results
- ✅ Optimized goods classification search (timeout→<1s)
- ✅ Added 5,539 missing jiken_c_t records
- ✅ Comprehensive index optimization

## Documentation

### Comprehensive Documentation Available
- **`CLAUDE_BASE.md`** - Base development principles and workflow
- **`DATABASE_DETAILED_ANALYSIS.md`** - Detailed database analysis
- **`SYSTEM_IMPROVEMENTS_SUMMARY.md`** - Recent improvements and fixes
- **`AUTONOMOUS_SYSTEM_README.md`** - Autonomous system guide
- **`WEEKLY_UPDATE_GUIDE.md`** - Data maintenance procedures

### Search Capabilities
- ✅ Application number search
- ✅ Trademark text search (Japanese/English/symbols)
- ✅ Goods classification search
- ✅ Similar group code search
- ✅ International trademark search
- ✅ Applicant name search
- ✅ Rights holder information (registered trademarks)
- ✅ Trademark images (domestic trademarks)
- ✅ Pronunciation search

## TMCloud-Specific Guidelines

### Tech Stack
| Component | Technology | Configuration |
|-----------|------------|---------------|
| Language | Python 3.12+ | Type hints required |
| Database | SQLite | 43+ optimized indexes |
| Web Framework | Flask | Production server on port 5002 |
| Testing | pytest | Coverage ≥ 90% + performance tests |
| Text Processing | Custom TextNormalizer | TM-SONAR compliance |

### Security & Compliance
- **Never commit sensitive data**: TSV files contain patent office data
- **Validate search inputs**: Prevent SQL injection in dynamic queries
- **Image serving**: Secure Base64 decoding for trademark images
- **Performance monitoring**: Alert if search queries > 1 second
- **Data integrity**: Run `pip-audit` weekly for dependencies

### Testing Strategy (TMCloud-Specific)
```bash
# Unit tests for search functions
pytest tests/test_search_functions.py -v

# Integration tests with actual database
pytest tests/test_integration.py -v

# Performance regression tests
python3 performance_benchmark.py

# Comprehensive search validation
python3 comprehensive_search_test.py

# Coverage report (target ≥ 90%)
pytest --cov=. --cov-report=html
```

### Deployment & Operations
```bash
# Database health check
python3 autonomous_system_launcher.py status

# Staging deployment (local testing)
python3 app_dynamic_join_claude_optimized.py

# Performance baseline
python3 performance_benchmark.py > baseline_$(date +%Y%m%d).txt

# Weekly data updates
python3 weekly_data_updater.py
```

### TMCloud Autonomy Escalation Matrix
| Trigger | Required Action |
|---------|----------------|
| **Search timeout > 1s** | Analyze query, optimize indexes, request approval for schema changes |
| **Data quality < 90** | Run diagnostics, identify gaps, create improvement plan |
| **Database corruption** | Pause operations, request explicit `CONFIRM: RESTORE` token |
| **TSV import failure** | Backup current state, analyze failed files, escalate if > 5% loss |

### Temporary Scripts Policy
- **Store in**: `scripts/tmp/` directory
- **Naming**: `tmp_YYYYMMDD_purpose.py` format
- **Cleanup**: Auto-delete after 30 days via CI check
- **Examples**: `tmp_20250714_sony_duplicate_fix.py`

## File Structure Notes

### Data Organization
- **`tsv_data/tsv/`** - 77+ TSV files from Japan Patent Office (NEVER commit to repo)
- **`csvs/`** - 193+ CSV specification files documenting data formats
- **`images/final_complete/`** - 6,488+ trademark images (JPG format)
- **`decoded_tsvs/`** - Processed TSV files in readable format
- **`scripts/tmp/`** - Temporary experimental scripts (auto-cleaned)

### Configuration
- **`create_schema.sql`** - Core database schema with 31+ tables
- **`scripts/phase2_schema.sql`** - International trademark schema extension
- **`scripts/create_unified_trademark_view.sql`** - Unified search view creation
- **`test_results/`** - Automated test execution results (JSON format)

### Documentation Hierarchy
1. **`CLAUDE.md`** (this file) - Primary development guide
2. **`CLAUDE_BASE.md`** - Universal development principles
3. **`DATABASE_DETAILED_ANALYSIS.md`** - Database architecture details
4. **`SYSTEM_IMPROVEMENTS_SUMMARY.md`** - Recent fixes and optimizations
5. **`AUTONOMOUS_SYSTEM_README.md`** - Self-improvement system guide