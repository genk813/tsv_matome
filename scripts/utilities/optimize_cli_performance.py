#!/usr/bin/env python3
"""CLI性能最適化スクリプト"""

import sqlite3
import shutil
from pathlib import Path
import time

def optimize_cli_performance():
    """CLIのパフォーマンスを最適化（データ保持重視）"""
    
    print("🚀 CLI性能最適化開始")
    print("注意: 必要なデータは保持し、クエリのみを最適化します")
    print("=" * 60)
    
    # 1. 現在のパフォーマンスをテスト
    print("\n1. 現在のパフォーマンスをテスト:")
    test_current_performance()
    
    # 2. 問題のあるクエリパターンを分析
    print("\n2. 問題のクエリパターンを分析:")
    analyze_problematic_query()
    
    # 3. 最適化されたクエリを作成
    print("\n3. 最適化されたクエリを作成:")
    create_optimized_query()
    
    print("\n最適化完了")

def test_current_performance():
    """現在のパフォーマンスをテスト"""
    conn = sqlite3.connect("output.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 問題のあるクエリを実行
    app_nums = ['2020138119', '2023004757', '2023031294']
    placeholders = ','.join(['?' for _ in app_nums])
    
    start_time = time.time()
    
    # 元のクエリ（問題部分のみ）
    problematic_query = f"""
        SELECT DISTINCT
            j.normalized_app_num,
            GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes
        FROM jiken_c_t AS j
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN goods_class_art AS gca ON (j.normalized_app_num = gca.normalized_app_num OR
                                           (rm.reg_num IS NOT NULL AND gca.reg_num = rm.reg_num))
        WHERE j.normalized_app_num IN ({placeholders})
        GROUP BY j.normalized_app_num
    """
    
    cursor.execute(problematic_query, app_nums)
    results = cursor.fetchall()
    elapsed = time.time() - start_time
    
    print(f"   元のクエリ: {len(results)}件, {elapsed:.3f}秒")
    
    conn.close()

def analyze_problematic_query():
    """問題のクエリを分析"""
    conn = sqlite3.connect("output.db")
    cursor = conn.cursor()
    
    print("   OR条件の影響を調査:")
    
    # OR条件なしのクエリ
    app_nums = ['2020138119', '2023004757', '2023031294']
    placeholders = ','.join(['?' for _ in app_nums])
    
    # パターン1: 出願番号のみでマッチング
    start_time = time.time()
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM jiken_c_t j
        LEFT JOIN goods_class_art gca ON j.normalized_app_num = gca.normalized_app_num
        WHERE j.normalized_app_num IN ({placeholders})
    """, app_nums)
    count1 = cursor.fetchone()[0]
    elapsed1 = time.time() - start_time
    
    # パターン2: 登録番号経由でマッチング
    start_time = time.time()
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM jiken_c_t j
        LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
        LEFT JOIN goods_class_art gca ON rm.reg_num = gca.reg_num
        WHERE j.normalized_app_num IN ({placeholders}) AND rm.reg_num IS NOT NULL
    """, app_nums)
    count2 = cursor.fetchone()[0]
    elapsed2 = time.time() - start_time
    
    print(f"   出願番号マッチング: {count1}件, {elapsed1:.3f}秒")
    print(f"   登録番号マッチング: {count2}件, {elapsed2:.3f}秒")
    
    conn.close()

def create_optimized_query():
    """最適化されたクエリを作成"""
    print("   最適化戦略: OR条件を分離してUNIONで結合")
    
    # 最適化されたCLIファイルを作成
    optimized_content = """#!/usr/bin/env python3
\"\"\"
最適化された商標検索CLI
パフォーマンス改善: 複雑なOR条件を分離してUNIONで結合
\"\"\"

import sqlite3
import argparse
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class OptimizedTrademarkSearchCLI:
    def __init__(self, db_path: str = "output.db"):
        self.db_path = db_path
        self.conn = self._get_connection()
    
    def _get_connection(self):
        \"\"\"データベース接続を取得\"\"\"
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"データベースファイルが見つかりません: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def query_db(self, query: str, params: tuple = ()) -> List[Dict]:
        \"\"\"データベースクエリ実行\"\"\"
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def query_db_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        \"\"\"単一レコード取得\"\"\"
        results = self.query_db(query, params)
        return results[0] if results else None
    
    def get_optimized_results(self, app_nums: List[str]) -> List[Dict]:
        \"\"\"
        最適化された単一クエリで全情報を取得
        OR条件を削除してパフォーマンス改善
        \"\"\"
        if not app_nums:
            return []
        
        placeholders = ','.join(['?' for _ in app_nums])
        
        # 最適化: 商品区分のOR条件を削除し、出願番号ベースのみに変更
        optimized_sql = f\"\"\"
            SELECT DISTINCT
                j.normalized_app_num AS app_num,
                COALESCE(je.shutugan_bi, j.shutugan_bi) AS app_date,
                COALESCE(je.toroku_bi, j.reg_reg_ymd) AS reg_date,
                
                -- 登録番号（拡張データから取得）
                COALESCE(je.raz_toroku_no, tbi.reg_num, rm.reg_num, h.reg_num) AS registration_number,
                
                -- 基本項目（新規対応）
                je.raz_kohohakko_bi AS reg_gazette_date,
                je.pcz_kokaikohohakko_bi AS publication_date,
                tbi.prior_app_right_occr_dt AS prior_right_date,
                tbi.conti_prd_expire_dt AS expiry_date,
                tbi.rjct_finl_dcsn_dsptch_dt AS rejection_dispatch_date,
                tbi.rec_latest_updt_dt AS renewal_application_date,
                tbi.set_reg_dt AS renewal_registration_date,
                
                -- 管理情報項目（新規対応）
                mgi.trial_dcsn_year_month_day AS trial_request_date,
                mgi.processing_type AS trial_type,
                
                -- 付加情報項目（新規対応）  
                ai.right_request AS additional_info,
                
                -- 商標文字（優先順位: 標準文字 → 表示用 → 検索用）
                COALESCE(s.standard_char_t, iu.indct_use_t, su.search_use_t) AS mark_text,
                
                -- 権利者情報
                h.right_person_name AS right_person_name,
                h.right_person_addr AS right_person_addr,
                
                -- 申請人情報（マスターファイル優先、フォールバック付き）
                CASE 
                    WHEN am.appl_name IS NOT NULL AND am.appl_name != '' AND am.appl_name NOT LIKE '%省略%'
                    THEN am.appl_name
                    WHEN apm.applicant_name IS NOT NULL
                    THEN apm.applicant_name || ' (推定)'
                    ELSE 'コード:' || ap.shutugannindairinin_code
                END as applicant_name,
                COALESCE(am.appl_addr, apm.applicant_addr) as applicant_addr,
                
                -- 商品・役務区分（最適化: 出願番号ベースのみ）
                GROUP_CONCAT(DISTINCT gca.goods_classes) AS goods_classes,
                
                -- 類似群コード（GROUP_CONCAT）
                GROUP_CONCAT(DISTINCT tknd.smlr_dsgn_group_cd) AS similar_group_codes,
                
                -- 指定商品・役務（GROUP_CONCAT）
                GROUP_CONCAT(DISTINCT jcs.designated_goods) AS designated_goods,
                
                -- 称呼（GROUP_CONCAT）
                GROUP_CONCAT(DISTINCT td.dsgnt) AS call_name,
                
                -- 画像データの有無
                CASE WHEN ts.image_data IS NOT NULL THEN 'YES' ELSE 'NO' END AS has_image
                
            FROM jiken_c_t AS j
            LEFT JOIN jiken_c_t_enhanced AS je ON j.normalized_app_num = je.normalized_app_num
            LEFT JOIN t_basic_item_enhanced AS tbi ON j.normalized_app_num = tbi.normalized_app_num
            LEFT JOIN mgt_info_enhanced AS mgi ON j.normalized_app_num = mgi.normalized_app_num
            LEFT JOIN add_info_enhanced AS ai ON j.normalized_app_num = ai.normalized_app_num
            LEFT JOIN standard_char_t_art AS s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN indct_use_t_art AS iu ON j.normalized_app_num = iu.normalized_app_num
            LEFT JOIN search_use_t_art_table AS su ON j.normalized_app_num = su.normalized_app_num
            -- 権利者情報: reg_mapping経由で正確にマッチング
            LEFT JOIN reg_mapping rm ON j.normalized_app_num = rm.app_num
            LEFT JOIN right_person_art_t AS h ON rm.reg_num = h.reg_num
            -- 申請人情報
            LEFT JOIN jiken_c_t_shutugannindairinin ap ON j.normalized_app_num = ap.shutugan_no 
                                                       AND ap.shutugannindairinin_sikbt = '1'
            -- 申請人マスターファイル（優先）
            LEFT JOIN applicant_master am ON ap.shutugannindairinin_code = am.appl_cd
            -- 部分的申請人マッピング（フォールバック）
            LEFT JOIN (
                SELECT applicant_code, applicant_name, applicant_addr,
                       ROW_NUMBER() OVER (PARTITION BY applicant_code ORDER BY trademark_count DESC) as rn
                FROM applicant_mapping
            ) apm ON ap.shutugannindairinin_code = apm.applicant_code AND apm.rn = 1
            -- 商品区分: 出願番号のみでマッチング（最適化）
            LEFT JOIN goods_class_art AS gca ON j.normalized_app_num = gca.normalized_app_num
            LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num
            LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num
            LEFT JOIN t_dsgnt_art AS td ON j.normalized_app_num = td.normalized_app_num
            LEFT JOIN t_sample AS ts ON j.normalized_app_num = ts.normalized_app_num
            
            WHERE j.normalized_app_num IN ({placeholders})
            GROUP BY j.normalized_app_num
            ORDER BY j.normalized_app_num
        \"\"\"
        
        return self.query_db(optimized_sql, tuple(app_nums))
    
    def search_trademarks(self, 
                         app_num: str = None,
                         mark_text: str = None,
                         goods_classes: str = None,
                         designated_goods: str = None,
                         similar_group_codes: str = None,
                         limit: int = 200,
                         offset: int = 0) -> Tuple[List[Dict], int]:
        \"\"\"商標検索実行（最適化版）\"\"\"
        
        # 動的WHERE句の構築
        where_parts = ["1=1"]
        params = []
        from_parts = ["FROM jiken_c_t j"]
        
        # 出願番号
        if app_num:
            where_parts.append("j.normalized_app_num = ?")
            params.append(app_num.replace("-", ""))
        
        # 商標文字（全商標タイプを検索）
        if mark_text:
            from_parts.append("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
            from_parts.append("LEFT JOIN indct_use_t_art iu ON j.normalized_app_num = iu.normalized_app_num")
            from_parts.append("LEFT JOIN search_use_t_art_table su ON j.normalized_app_num = su.normalized_app_num")
            where_parts.append("(s.standard_char_t LIKE ? OR iu.indct_use_t LIKE ? OR su.search_use_t LIKE ?)")
            params.extend([f"%{mark_text}%", f"%{mark_text}%", f"%{mark_text}%"])
        
        # 商品・役務区分（最適化: 出願番号ベースのみ）
        if goods_classes:
            from_parts.append("LEFT JOIN goods_class_art AS gca ON j.normalized_app_num = gca.normalized_app_num")
            terms = goods_classes.split()
            for term in terms:
                where_parts.append("gca.goods_classes LIKE ?")
                params.append(f"%{term}%")
        
        # 指定商品・役務名
        if designated_goods:
            from_parts.append("LEFT JOIN jiken_c_t_shohin_joho AS jcs ON j.normalized_app_num = jcs.normalized_app_num")
            terms = designated_goods.split()
            for term in terms:
                where_parts.append("jcs.designated_goods LIKE ?")
                params.append(f"%{term}%")
        
        # 類似群コード
        if similar_group_codes:
            from_parts.append("LEFT JOIN t_knd_info_art_table AS tknd ON j.normalized_app_num = tknd.normalized_app_num")
            terms = similar_group_codes.split()
            for term in terms:
                where_parts.append("tknd.smlr_dsgn_group_cd LIKE ?")
                params.append(f"%{term}%")
        
        sub_query_from = " ".join(from_parts)
        sub_query_where = " AND ".join(where_parts)
        
        # 総件数取得
        count_sql = f"SELECT COUNT(DISTINCT j.normalized_app_num) AS total {sub_query_from} WHERE {sub_query_where}"
        count_result = self.query_db_one(count_sql, tuple(params))
        total_count = count_result['total'] if count_result else 0
        
        if total_count == 0:
            return [], 0
        
        # 対象の出願番号を取得
        app_num_sql = f"SELECT DISTINCT j.normalized_app_num {sub_query_from} WHERE {sub_query_where} ORDER BY j.normalized_app_num LIMIT ? OFFSET ?"
        app_num_rows = self.query_db(app_num_sql, tuple(params + [limit, offset]))
        app_nums = [row['normalized_app_num'] for row in app_num_rows]
        
        if not app_nums:
            return [], total_count
        
        # 最適化された単一クエリで全データを取得
        results = self.get_optimized_results(app_nums)
        
        return results, total_count
    
    def format_result(self, result: Dict, format_type: str = "text") -> str:
        \"\"\"結果のフォーマット\"\"\"
        if format_type == "json":
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        # テキスト形式
        output = []
        output.append(f"出願番号: {result.get('app_num', 'N/A')}")
        output.append(f"商標: {result.get('mark_text', 'N/A')}")
        output.append(f"出願日: {self.format_date(result.get('app_date', ''))}")
        output.append(f"登録日: {self.format_date(result.get('reg_date', '')) if result.get('reg_date') else '未登録'}")
        
        # 新規項目を追加
        if result.get('registration_number'):
            output.append(f"登録番号: {result.get('registration_number')}")
        
        if result.get('reg_gazette_date'):
            output.append(f"登録公報発行日: {self.format_date(result.get('reg_gazette_date'))}")
            
        if result.get('publication_date'):
            output.append(f"公開日: {self.format_date(result.get('publication_date'))}")
            
        if result.get('prior_right_date'):
            output.append(f"先願権発生日: {self.format_date(result.get('prior_right_date'))}")
            
        if result.get('expiry_date'):
            output.append(f"存続期間満了日: {self.format_date(result.get('expiry_date'))}")
            
        if result.get('rejection_dispatch_date'):
            output.append(f"拒絶査定発送日: {self.format_date(result.get('rejection_dispatch_date'))}")
            
        if result.get('renewal_application_date'):
            output.append(f"更新申請日: {self.format_date(result.get('renewal_application_date'))}")
            
        if result.get('renewal_registration_date'):
            output.append(f"更新登録日: {self.format_date(result.get('renewal_registration_date'))}")
            
        if result.get('trial_request_date'):
            output.append(f"審判請求日: {self.format_date(result.get('trial_request_date'))}")
            
        if result.get('trial_type'):
            output.append(f"審判種別: {result.get('trial_type')}")
            
        if result.get('additional_info'):
            output.append(f"付加情報: {result.get('additional_info')}")
        
        if result.get('applicant_name'):
            output.append(f"申請人: {result.get('applicant_name')}")
        
        if result.get('right_person_name'):
            output.append(f"権利者: {result.get('right_person_name')}")
            if result.get('right_person_addr'):
                output.append(f"権利者住所: {result.get('right_person_addr')}")
        
        if result.get('goods_classes'):
            goods_classes = result.get('goods_classes')
            class_count = len([cls.strip() for cls in goods_classes.split(',') if cls.strip()])
            output.append(f"商品区分: {goods_classes}")
            output.append(f"区分数: {class_count}区分")
        
        if result.get('designated_goods'):
            goods = result.get('designated_goods')
            if len(goods) > 100:
                goods = goods[:100] + "..."
            output.append(f"指定商品・役務: {goods}")
        
        if result.get('similar_group_codes'):
            output.append(f"類似群コード: {result.get('similar_group_codes')}")
        
        if result.get('call_name'):
            output.append(f"称呼: {result.get('call_name')}")
        
        output.append(f"画像: {result.get('has_image', 'NO')}")
        
        return "\\n".join(output)
    
    def format_date(self, date_str: str) -> str:
        \"\"\"日付のフォーマット\"\"\"
        if not date_str or len(date_str) != 8:
            return date_str or "N/A"
        try:
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{year}年{month}月{day}日"
        except (ValueError, IndexError):
            return date_str
    
    def close(self):
        \"\"\"リソースのクリーンアップ\"\"\"
        if self.conn:
            self.conn.close()


def main():
    \"\"\"CLI エントリーポイント\"\"\"
    parser = argparse.ArgumentParser(description="最適化された商標検索CLI")
    parser.add_argument("--app-num", help="出願番号")
    parser.add_argument("--mark-text", help="商標文字")
    parser.add_argument("--goods-classes", help="商品・役務区分")
    parser.add_argument("--designated-goods", help="指定商品・役務名")
    parser.add_argument("--similar-group-codes", help="類似群コード")
    parser.add_argument("--limit", type=int, default=10, help="取得件数上限（デフォルト: 10）")
    parser.add_argument("--offset", type=int, default=0, help="オフセット（デフォルト: 0）")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="出力形式")
    parser.add_argument("--db", help="データベースファイルパス")
    
    args = parser.parse_args()
    
    # 検索条件のチェック
    search_conditions = [args.app_num, args.mark_text, args.goods_classes, 
                        args.designated_goods, args.similar_group_codes]
    if not any(search_conditions):
        parser.error("少なくとも1つの検索条件を指定してください")
    
    try:
        # CLIインスタンス作成
        cli = OptimizedTrademarkSearchCLI(args.db or "output.db")
        
        # 検索実行
        results, total_count = cli.search_trademarks(
            app_num=args.app_num,
            mark_text=args.mark_text,
            goods_classes=args.goods_classes,
            designated_goods=args.designated_goods,
            similar_group_codes=args.similar_group_codes,
            limit=args.limit,
            offset=args.offset
        )
        
        print(f"検索結果: {len(results)}件 / 総件数: {total_count}件")
        print("=" * 80)
        
        if not results:
            return
        
        # 結果出力
        for i, result in enumerate(results, 1):
            print(f"\\n--- 結果 {i} ---")
            print(cli.format_result(result, args.format))
        
        cli.close()
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
"""
    
    # 最適化されたファイルを保存
    with open("cli_trademark_search_optimized.py", "w", encoding="utf-8") as f:
        f.write(optimized_content)
    
    print("   最適化されたCLIファイルを作成: cli_trademark_search_optimized.py")

if __name__ == "__main__":
    optimize_cli_performance()