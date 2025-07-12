#!/usr/bin/env python3
"""
TSV_MATOME ファイル整理実行スクリプト
ファイルを適切なディレクトリに移動し、プロジェクトを整理する
"""

import os
import shutil
from pathlib import Path

def organize_files():
    root = Path(".")
    
    # 移動定義
    moves = {
        # 一時的な分析スクリプト → scripts/tmp/
        "scripts/tmp": [
            "analyze_all_tsv_files.py",
            "analyze_applicant_data.py", 
            "analyze_database_detailed.py",
            "analyze_enhanced_trademark_display.py",
            "analyze_goods_search_performance.py",
            "analyze_missing_applicant_files.py",
            "analyze_phase2_tsv.py",
            "analyze_trademark_display.py",
            "advanced_unknown_analyzer.py",
            "applicant_code_analysis.py",
            "check_applicant_data.py",
            "check_data_samples.py", 
            "check_image_data.py",
            "check_reg_mapping.py",
            "check_section_symbol.py",
            "debug_applicant_search.py",
            "debug_pronunciation_search.py",
            "profile_actual_search.py",
            "test_app.py",
            "test_applicant_search.py",
            "test_company_debug.py",
            "test_enhanced_search.py",
            "test_final_relationships.py",
            "test_p2_14_debug.py", 
            "test_p2_14_real_data.py",
            "test_search_direct.py",
            "test_search_functionality.py",
            "optimize_goods_search.py",
            "file_organization_plan.py",
            "check_db_status.py"  # 今日作成したテスト用
        ],
        
        # 旧バージョン → scripts/deprecated/
        "scripts/deprecated": [
            "app_dynamic_join.py",
            "app_dynamic_join_claude.py", 
            "app_dynamic_join_claude_optimized_v2.py",
            "app_enhanced.py",
            "app_simple_fixed.py",
            "cli_trademark_search_backup.py",
            "import_tsv_data.py",                     # 旧版
            "import_applicant_master.py",             # 旧版
            "search_results_html_generator.py",       # 旧版
            "extract_images.py",                      # 旧版
            "build_applicant_master.py",              # 旧版
            "create_enhanced_applicant_mapping.py",   # 旧版
            "fix_applicant_encoding.py",
            "waiting_for_applicant_files.py",
            "update_t_sample.py",
            "update_t_sample_fast.py"
        ],
        
        # 実験的なスクリプト → scripts/experimental/
        "scripts/experimental": [
            "autonomous_test_system.py",
            "self_improving_system.py", 
            "enhanced_search_app.py",
            "enhanced_web_server.py",
            "final_applicant_enhanced_server.py",
            "applicant_master_ready_server.py",
            "simple_web_test.py",
            "simple_extract_images.py",
            "simple_performance_test.py",
            "build_enhanced_index.py",
            "build_enhanced_index_debug.py",
            "enhance_database_schema.py",
            "mcp_tsv_matome.py",
            "search_engine.py",
            "decode_tsvs.py",
            "read_t_sample_head.py",
            "update_search_with_applicant.py"
        ],
        
        # ユーティリティ → scripts/utilities/
        "scripts/utilities": [
            "comprehensive_test_suite.py",
            "optimize_cli_performance.py",
            "optimize_search_performance.py"
        ]
    }
    
    print("📁 TSV_MATOME ファイル整理実行")
    print("=" * 50)
    
    # 各カテゴリのファイルを移動
    for dest_dir, files in moves.items():
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📂 {dest_dir} に移動:")
        moved_count = 0
        
        for file in files:
            file_path = root / file
            if file_path.exists():
                dest_file = dest_path / file
                try:
                    shutil.move(str(file_path), str(dest_file))
                    print(f"  ✓ {file}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ✗ {file} - エラー: {e}")
            else:
                print(f"  ? {file} - ファイルが見つかりません")
        
        print(f"  小計: {moved_count}件移動")
    
    # 残っているPythonファイルを確認
    remaining_py = list(root.glob("*.py"))
    print(f"\n📄 ルートディレクトリに残るPythonファイル: {len(remaining_py)}件")
    
    # コアファイル（本番用）
    core_files = [
        "app_dynamic_join_claude_optimized.py",
        "cli_trademark_search.py", 
        "cli_trademark_search_enhanced.py",
        "cli_trademark_search_optimized.py",  # 今日の最適化版
        "text_normalizer.py",
        "init_database.py",
        "import_tsv_data_fixed.py",
        "database_optimization.py",
        "build_reg_mapping.py",
        "create_partial_applicant_mapping.py",
        "import_applicant_master_data.py",
        "complete_database_enhancement.py",
        "search_results_html_generator_improved.py",
        "autonomous_system_launcher.py",
        "weekly_data_updater.py",
        "extract_images_no_pandas.py",
        "performance_benchmark.py"
    ]
    
    print("\n✅ コアファイル（残す）:")
    for file in sorted(remaining_py):
        if file.name in core_files:
            print(f"  ✓ {file.name}")
        else:
            print(f"  ? {file.name} - 未分類")

if __name__ == "__main__":
    organize_files()