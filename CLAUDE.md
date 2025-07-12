# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TSV_MATOME is a Japanese trademark search system that processes TSV (Tab-Separated Values) files from the Japan Patent Office, manages trademark data in SQLite, and provides both web-based and command-line search interfaces. The system handles trademark text, applicant information, rights holder data, images, and goods classification with comprehensive search capabilities.

## Core Architecture

### Database Layer
- **Main Database**: `output.db` (SQLite) - contains 18 tables with 437,223 total records (optimized)
- **Schema**: Defined in `create_schema.sql` with 25 optimized indexes
- **Database Size**: 270.93MB with comprehensive trademark data
- **Key Tables**:
  - `jiken_c_t` - Core trademark case information (16,688 records, 100% coverage)
  - `standard_char_t_art`, `indct_use_t_art`, `search_use_t_art_table` - Trademark text (90%+ coverage)
  - `right_person_art_t` - Rights holder information (22.9% coverage, registered trademarks only)
  - `jiken_c_t_shutugannindairinin` - Applicant/agent information (88.6% codes, 15.2% names)
  - `jiken_c_t_shohin_joho` - Designated goods/services information (100% coverage)
  - `goods_class_art` - Goods/services classification (68.9% coverage)
  - `reg_mapping` - Critical mapping table linking application numbers to registration numbers (33,764 mappings)
  - `applicant_mapping` - Partial applicant code to name mapping (573 entries with confidence levels)
  - **Phase 1 Tables**: `applicant_master_full` (1,612 records), `applicant_integration_mapping` (40 records)
  - `t_sample` - Trademark image data (31.0% coverage, Base64 encoded images)
  - **Enhanced Tables**: `t_basic_item_enhanced`, `mgt_info_enhanced`, `add_info_enhanced` (extended date/trial info)

### Application Layer
- **Production Flask App**: `app_dynamic_join_claude_optimized.py` - Main web interface (port 5002)
- **CLI Search Tool**: `cli_trademark_search.py` - Command-line interface with full search capabilities
- **Enhanced CLI Search**: `cli_trademark_search_enhanced.py` - TM-SONAR compliant search with advanced normalization
- **Text Normalization**: `text_normalizer.py` - TM-SONAR level text processing and pronunciation matching
- **Autonomous System**: `autonomous_system_launcher.py` - Self-testing and improvement system
- **HTML Generators**: `search_results_html_generator_improved.py` - Responsive HTML output with folding
- **Alternative Servers**: Various specialized servers for different use cases
- **Core Architecture**: Single-query optimization pattern to avoid N+1 problems (95% query reduction achieved)

### Data Processing Pipeline
- **TSV Import**: `import_tsv_data_fixed.py` - Handles 77 different TSV file types (272MB total)
- **Database Optimization**: `database_optimization.py` - Performance optimization and duplicate removal
- **Image Processing**: `extract_images_no_pandas.py` - Extracts Base64 images (6,488 images available)
- **Weekly Updates**: `weekly_data_updater.py` - Incremental data updates with automatic backups

## Common Commands

### Database Operations
```bash
# Initialize fresh database with optimized schema
python3 init_database.py

# Build critical reg_mapping table (enables rights holder display)
python3 build_reg_mapping.py

# Create partial applicant mapping (enables some applicant name display) 
python3 create_partial_applicant_mapping.py

# Phase 1: Import applicant master data (improves applicant name coverage to 15.2%)
python3 import_applicant_master_data.py

# Run comprehensive database optimization (indexes, duplicate removal)
python3 database_optimization.py

# Test database operations and relationships
python3 test_app.py
```

### Search and Analysis
```bash
# CLI trademark search (multiple search types)
python3 cli_trademark_search.py --mark-text "ソニー" --limit 10
python3 cli_trademark_search.py --app-num "2020138119"
python3 cli_trademark_search.py --goods-classes "09" --limit 5

# Enhanced CLI search with TM-SONAR normalization
python3 cli_trademark_search_enhanced.py --mark-text "ソニー" --enhanced --limit 10
python3 cli_trademark_search_enhanced.py --mark-text "チヂミ" --pronunciation --limit 5
python3 cli_trademark_search_enhanced.py --mark-text "ソニー,パナソニック" --tm-sonar --limit 20
python3 cli_trademark_search_enhanced.py --mark-text "ソニ？" --fuzzy --limit 15

# Phase 1: Enhanced applicant search (improved coverage)
python3 cli_trademark_search_enhanced.py --applicant-name "ＮＴＴ株式会社" --limit 5
python3 cli_trademark_search_enhanced.py --applicant-name "フリュー" --enhanced --limit 3

# Generate responsive HTML search results
python3 search_results_html_generator_improved.py --mark-text "ブル" --limit 3 --output "results.html"

# Autonomous system operations
python3 autonomous_system_launcher.py status
python3 autonomous_system_launcher.py search --mark-text "ソニー" --limit 10
python3 autonomous_system_launcher.py test
python3 autonomous_system_launcher.py improve
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

### Data Management
```bash
# Full TSV data import (initial setup)
python3 import_tsv_data_fixed.py

# Enhanced database schema (add extended fields)
python3 complete_database_enhancement.py

# Weekly data updates with validation
python3 weekly_data_updater.py weekly_data/YYYYMMDD/tsv --validate

# Extract images from trademark data (no pandas dependency)
python3 extract_images_no_pandas.py
```

### Analysis and Testing
```bash
# Comprehensive test suite
python3 test_search_functionality.py
python3 test_final_relationships.py
python3 comprehensive_test_suite.py

# Database analysis and coverage reports
python3 analyze_database_detailed.py
python3 analyze_trademark_display.py
python3 applicant_code_analysis.py

# Performance benchmarking
python3 performance_benchmark.py
```

## Key Implementation Details

### Critical Database Dependencies
Before development work, ensure these components exist:
1. **`reg_mapping`**: Run `python3 build_reg_mapping.py` - enables rights holder display (33,764 mappings)
2. **`applicant_mapping`**: Run `python3 create_partial_applicant_mapping.py` - enables partial applicant names
3. **Phase 1 Applicant Data**: Run `python3 import_applicant_master_data.py` - improves applicant coverage to 15.2%
4. **Enhanced tables**: Run `python3 complete_database_enhancement.py` - adds extended date/trial information
5. **Optimized indexes**: Created by `database_optimization.py` (25 indexes total)

### Data Coverage and Limitations
- **High Coverage (90%+)**: Basic info, trademark text, designated goods, similar group codes
- **Medium Coverage (60-90%)**: Goods classifications, trademark descriptions
- **Limited Coverage (<30%)**: Rights holder info (registered only), applicant names (Phase 1 improved to 15.2%)
- **Phase 1 Implemented**: Applicant master data system (`applicant_master_full` table with 1,612 records)

### Single-Query Optimization Pattern
```python
# ALWAYS use this pattern for search queries to avoid N+1 problems
def get_optimized_results(app_nums: List[str]) -> List[Dict]:
    # Single query with all necessary JOINs including enhanced tables
    query = f"""
        SELECT DISTINCT
            j.normalized_app_num AS app_num,
            COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) as mark_text,
            COALESCE(je.raz_toroku_no, tbi.reg_num, rm.reg_num, h.reg_num) AS registration_number,
            tbi.prior_app_right_occr_dt AS prior_right_date,
            tbi.conti_prd_expire_dt AS expiry_date,
            mgi.trial_dcsn_year_month_day AS trial_request_date,
            GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes
        FROM jiken_c_t j
        LEFT JOIN jiken_c_t_enhanced je ON j.normalized_app_num = je.normalized_app_num
        LEFT JOIN t_basic_item_enhanced tbi ON j.normalized_app_num = tbi.normalized_app_num
        LEFT JOIN mgt_info_enhanced mgi ON j.normalized_app_num = mgi.normalized_app_num
        LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN right_person_art_t h ON rm.reg_num = h.reg_num
        WHERE j.normalized_app_num IN ({placeholders})
        GROUP BY j.normalized_app_num
    """
```

### Column Name Normalization
- **Always use `normalized_app_num`** (not `shutugan_no`) for application numbers across all tables
- **Remove hyphens** from application numbers: `2024-12345` → `202412345`
- **Use COALESCE** for trademark text priority: `standard_char_t` → `indct_use_t` → `search_use_t`
- **Enhanced tables** use `normalized_app_num` consistently (optimized in database_optimization.py)

### Performance Considerations
- **Fast Queries**: Basic searches ~0.002s, complex searches ~0.009s
- **Slow Query**: Goods classification search (44s) - requires optimization
- **Index Usage**: 25 optimized indexes for common search patterns
- **Memory Management**: Results paginated (default: 200 per page)

### Rights Holder Information Pattern
```sql
-- CORRECT: Must use reg_mapping to connect applications to registrations
SELECT j.normalized_app_num, rp.right_person_name
FROM jiken_c_t j
JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num  
JOIN right_person_art_t rp ON rm.reg_num = rp.reg_num

-- INCORRECT: Direct join will fail (different number spaces)
SELECT j.normalized_app_num, rp.right_person_name
FROM jiken_c_t j
JOIN right_person_art_t rp ON j.normalized_app_num = rp.normalized_app_num
```

### Phase 1 Applicant Information Pattern
```sql
-- CORRECT: Phase 1 implementation with priority fallback system
SELECT j.normalized_app_num,
    CASE 
        WHEN amf.appl_name IS NOT NULL AND amf.appl_name != '' AND amf.appl_name NOT LIKE '%省略%'
        THEN amf.appl_name
        WHEN am.appl_name IS NOT NULL AND am.appl_name != '' AND am.appl_name NOT LIKE '%省略%'
        THEN am.appl_name
        WHEN apm.applicant_name IS NOT NULL
        THEN apm.applicant_name || ' (推定)'
        ELSE 'コード:' || ap.shutugannindairinin_code
    END as applicant_name
FROM jiken_c_t j
LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no AND ap.shutugannindairinin_sikbt = '1'
LEFT JOIN applicant_master_full amf ON ap.shutugannindairinin_code = amf.appl_cd  -- Phase 1: Highest priority
LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd        -- Legacy: Medium priority  
LEFT JOIN applicant_mapping apm ON ap.shutugannindairinin_code = apm.applicant_code  -- Estimated: Lowest priority
```

### TM-SONAR Text Normalization System
The system implements comprehensive text normalization following TM-SONAR (Trademark Sonar) specifications:

```python
# Use TextNormalizer for advanced trademark text processing
from text_normalizer import TextNormalizer

normalizer = TextNormalizer()

# Basic normalization (P1 level)
basic_result = normalizer.normalize_basic("あっぷる・Ⅲ世代")  # → "アップル・3世代"

# Pronunciation matching (称呼同一判定)
pronunciation_result = normalizer.normalize_pronunciation("チヂミ")  # → "チジミ" 

# TM-SONAR trademark normalization
trademark_result = normalizer.normalize_trademark("α-ブロッカー▲")  # → "A-ブロッカ-"

# Multiple search terms and wildcards
search_terms = normalizer.normalize_search_terms("ソニー,パナソニック", "trademark")
```

**Key Normalization Features:**
- **P1-P13 Basic Rules**: Hiragana→Katakana, case conversion, hyphen unification, symbol removal
- **Greek/Latin→ASCII**: α→A, β→B, Σ→S, etc.
- **Old Kanji→New**: 國→国, 學→学, 會→会, etc.
- **Roman Numerals→Arabic**: Ⅰ→1, Ⅱ→2, Ⅲ→3, etc.
- **Pronunciation Matching**: ヂ→ジ, ヅ→ズ, ヴェ→ベ, ティ→チ, etc.
- **Multi-term Search**: Space/comma separation with OR logic
- **Two-stage Notation**: 二段併記 with ＼ separator support
- **Wildcard Search**: ？ for partial matching

**Search Mode Options:**
- `--enhanced`: Basic P1 normalization
- `--pronunciation`: Pronunciation matching (発音同一判定)
- `--tm-sonar`: Full TM-SONAR compliance with multi-term support
- `--fuzzy`: Character-level partial matching

## Current System Status (2025-07-12)

### Database Optimization Status
- **Optimized Database**: 437,223 records across 18 tables (61,574 duplicates removed)
- **Enhanced Coverage**: 100% basic info, 90%+ trademark text, 100% designated goods
- **Performance Improvements**: 25 indexes, VACUUM optimization complete
- **Extended Data**: All enhanced tables with date/trial information populated

### Phase Implementation Status
- **Phase 1 COMPLETED**: Applicant Registration Information Files (055, 056)
  - `applicant_master_full` table: 1,612 records imported
  - `applicant_integration_mapping` table: 40 corporate merger records
  - Applicant name coverage improved from 14.8% to 15.2%
  - Enhanced CLI search with `--applicant-name` parameter fully functional
- **Phase 2 PENDING**: International trademark data (Madrid Protocol), design applications, intermediate records
  - New TSV files available: `intl_t_org_*`, `dsgn_gvrnmnt_*`, trial/opposition data
  - Estimated to add international trademark registration management, design state information, and trial proceedings

### Available Information Types
**Reliably Available (90%+ coverage)**:
- Basic application info (app number, dates, registration status)
- Trademark text (standard, display, search variants) 
- Designated goods/services details
- Trademark descriptions and similar group codes

**Partially Available (20-70% coverage)**:
- Rights holder information (registered trademarks only)
- Applicant names (partial mapping available)
- Goods classifications and images
- Extended date information (renewal, expiry, etc.)

**Limited/Missing**:
- Complete applicant master data (0% - requires additional TSV import)
- Comprehensive trial information (minimal data available)
- International classification version details

## Development Workflow

### Before Starting Development
1. **Verify Database State**: Run `python3 test_app.py` to ensure proper initialization
2. **Check Critical Tables**: Ensure `reg_mapping`, `applicant_mapping`, and enhanced tables exist
3. **Review Documentation**: Check `DATABASE_DETAILED_ANALYSIS.md` for current data coverage

### When Adding Search Features
1. Use the single-query optimization pattern to avoid N+1 problems
2. Test with `cli_trademark_search.py` or `cli_trademark_search_enhanced.py` before web implementation
3. Consider data coverage limitations when designing UI
4. Use appropriate JOINs via `reg_mapping` for rights holder data
5. For text search features, leverage `TextNormalizer` for TM-SONAR compliant processing
6. Test normalization with both basic and pronunciation modes for different use cases

### When Debugging Performance Issues
1. **Goods Classification Search**: Known 44s performance issue (requires normalization)
2. **Index Usage**: Verify queries use the 25 optimized indexes via `EXPLAIN QUERY PLAN`
3. **Memory Usage**: Monitor with large result sets, implement pagination
4. **Query Patterns**: Avoid N+1 by using the optimized single-query approach

### File Organization

### Core Files
- `output.db` - Main SQLite database (270.93MB, optimized)
- `create_schema.sql` - Database schema with 25 indexes
- `cli_trademark_search.py` - Primary command-line interface
- `cli_trademark_search_enhanced.py` - Enhanced CLI with TM-SONAR normalization features and Phase 1 applicant search
- `text_normalizer.py` - TM-SONAR compliant text normalization utility
- `app_dynamic_join_claude_optimized.py` - Production web application
- `import_applicant_master_data.py` - Phase 1 applicant master data import system
- `create_applicant_master_schema.sql` - Phase 1 applicant database schema

### Data Processing
- `tsv_data/tsv/` - Source TSV files from Patent Office (77+ files, 272MB+)
- `import_tsv_data_fixed.py` - TSV data import with encoding handling
- `import_applicant_master_data.py` - Phase 1 applicant master data import (1,612 records)
- `database_optimization.py` - Performance optimization and cleanup
- `complete_database_enhancement.py` - Extended data import
- **Phase 2 Files**: `intl_t_org_*` (international), `dsgn_gvrnmnt_*` (design), `intrmd_*` (intermediate records)

### Analysis and Utilities
- `DATABASE_DETAILED_ANALYSIS.md` - Comprehensive database analysis report
- `search_results_html_generator_improved.py` - Responsive HTML output generator
- `autonomous_system_launcher.py` - Self-testing and improvement system
- `images/final_complete/` - Extracted trademark images (6,488 files)

### Dependencies
- Python 3.x with sqlite3 (built-in)
- Flask (for web interface): `pip install flask`
- Standard library modules: csv, pathlib, re, logging, argparse, json

## Common Patterns and Architectural Constraints

### Error Handling Patterns
```python
# Standard database connection with optimization check
def get_db_connection():
    if not Path("output.db").exists():
        raise FileNotFoundError("Run python3 init_database.py first")
    conn = sqlite3.connect("output.db")
    conn.row_factory = sqlite3.Row
    return conn
```

### HTML Generation with Responsive Design
```python
# Use improved HTML generator for responsive output with folding
from search_results_html_generator_improved import ImprovedSearchResultsHTMLGenerator

generator = ImprovedSearchResultsHTMLGenerator("search_results/html")
html_content = generator.search_and_generate_html(search_params)
file_path = generator.save_html_file(html_content, "results.html")
```

### Autonomous System Integration
```python
# Use autonomous system for testing and improvement
from autonomous_system_launcher import AutonomousSystemLauncher

launcher = AutonomousSystemLauncher()
launcher.run_search(mark_text="ソニー", limit=10)
launcher.run_automated_tests()
launcher.run_improvement_cycle()
```

## Known Issues and Limitations

### Performance Issues
- **Goods Classification Search**: 44.7 seconds (requires table normalization)
- **Large Result Sets**: Memory usage with thousands of results

### Data Gaps
- **Applicant Names**: Improved to 15.2% coverage with Phase 1 implementation (was 14.8%)
- **Trial Information**: Minimal data in `mgt_info_enhanced` table
- **International Classifications**: Version information not consistently available
- **Phase 2 Pending**: International trademark data, design applications, intermediate records

### TSV Import Constraints
- **Encoding Issues**: Multiple encoding detection required (UTF-8, CP932, EUC-JP)
- **Column Mapping**: Complex field normalization between different TSV file formats
- **Memory Usage**: Large file processing requires batch processing for stability