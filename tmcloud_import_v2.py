#!/usr/bin/env python3
# tmcloud_import_v2_complete.py - 設計書のマッピングに基づく完全版

import sqlite3
import csv
from pathlib import Path
import chardet
from datetime import datetime

# 設定
DB_PATH = "tmcloud_v2.db"
TSV_DIR = Path("/home/ygenk/TMCloud/tsv_data/tsv/20250611/")

# データクレンジング関数
def normalize_app_num(value):
    """出願番号の正規化（ハイフン除去など）"""
    if not value:
        return None
    # ハイフンを除去
    value = value.replace('-', '')
    # 0埋めの番号をNULLに
    if value == '0000000000':
        return None
    return value

def cleanse_data(value):
    """データクレンジング（空文字列をNoneに変換）"""
    if value == '' or value is None:
        return None
    return value

def detect_encoding(file_path):
    """ファイルのエンコーディングを検出"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))
    return result['encoding'] or 'utf-8'

# 各テーブルのインポート関数
def import_trademark_standard_char(conn, tsv_path):
    """1-1: 商標（標準文字）テーブル"""
    print("Importing trademark_standard_char...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_standard_char 
                (app_num, split_num, sub_data_num, standard_char_t, add_del_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                normalize_app_num(row['app_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sub_data_num']),
                cleanse_data(row['standard_char_t']),
                cleanse_data(row['add_del_id'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_display(conn, tsv_path):
    """1-2: 商標（表示用）テーブル"""
    print("Importing trademark_display...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_display 
                (app_num, split_num, sub_data_num, indct_use_t, add_del_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                normalize_app_num(row['app_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sub_data_num']),
                cleanse_data(row['indct_use_t']),
                cleanse_data(row['add_del_id'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_search(conn, tsv_path):
    """1-3: 商標（検索用）テーブル"""
    print("Importing trademark_search...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_search 
                (app_num, split_num, sub_data_num, search_seq_num, search_use_t, add_del_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                normalize_app_num(row['app_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sub_data_num']),
                int(row['search_use_t_seq']) if row.get('search_use_t_seq') else 1,
                cleanse_data(row['search_use_t']),
                cleanse_data(row['add_del_id'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_pronunciation(conn, tsv_path):
    """1-4: 称呼テーブル"""
    print("Importing trademark_pronunciation...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_pronunciations 
                (app_num, split_num, sub_data_num, pronunciation_seq_num, pronunciation, add_del_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                normalize_app_num(row['app_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sub_data_num']),
                int(row['dsgnt_seq']) if row.get('dsgnt_seq') else 1,
                cleanse_data(row['dsgnt']),
                cleanse_data(row['add_del_id'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_detailed_descriptions(conn, tsv_path):
    """1-5: 商標の詳細な説明テーブル"""
    print("Importing trademark_detailed_descriptions...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_detailed_descriptions 
                (law_code, app_num, history_num, creation_date, 
                 length_exceed_flag, detailed_description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['yonpo_code']),
                normalize_app_num(row['shutugan_no']),
                int(row['dtz_rireki_no']) if row.get('dtz_rireki_no') else 1,
                cleanse_data(row['dtz_sakusei_bi']),
                cleanse_data(row['lengthchoka_flag']),
                cleanse_data(row['shohyonoshousaina_setumei'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_goods_services_info(conn, tsv_path):
    """2-1: 商品・役務情報テーブル"""
    print("Importing trademark_goods_services...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_goods_services 
                (law_code, app_num, class_num, goods_seq_num, 
                 length_exceed_flag, goods_services_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                '4',  # law_code
                normalize_app_num(row['shutugan_no']),
                cleanse_data(row['rui']),
                cleanse_data(row['abz_junjo_no']),
                cleanse_data(row.get('lengthchoka_flag', '0')),
                cleanse_data(row['shohinekimumeisho'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_goods_classes(conn, tsv_path):
    """2-2: 商品区分記事テーブル"""
    print("Importing trademark_goods_classes...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_goods_classes 
                (law_code, reg_num, split_num, app_num, mu_num,
                 goods_class_art_upd_date, class_num_registered, processing_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['mu_num']),
                cleanse_data(row['goods_cls_art_upd_ymd']),
                cleanse_data(row['desig_goods_or_desig_wrk_class']),
                cleanse_data(row['processing_type'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_similar_group_codes(conn, tsv_path):
    """2-3: 類似群コードテーブル"""
    print("Importing trademark_similar_group_codes...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # 類似群コードの変換処理（5文字ずつ分割してカンマ区切り）
            similar_codes = row['smlr_dsgn_group_cd']
            if similar_codes:
                # 5文字ずつに分割
                codes = [similar_codes[i:i+5] for i in range(0, len(similar_codes), 5)]
                similar_codes_csv = ','.join(codes)
            else:
                similar_codes_csv = None
                
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_similar_group_codes 
                (app_num, split_num, sub_data_num, class_num,
                 similar_group_codes, add_del_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                normalize_app_num(row['app_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sub_data_num']),
                cleanse_data(row['knd']),  # knd → class_num のマッピング
                similar_codes_csv,
                cleanse_data(row['add_del_id'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_vienna_codes(conn, tsv_path):
    """2-4: ウィーン分類テーブル"""
    print("Importing trademark_vienna_codes...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_vienna_codes 
                (add_del_id, app_num, split_num, sub_data_num,
                 large_class, mid_class, small_class, complement_sub_class)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sub_data_num']),
                cleanse_data(row['grphc_term_large_class']),
                cleanse_data(row['grphc_term_mid_class']),
                cleanse_data(row['grphc_term_small_class']),
                cleanse_data(row['grphc_term_complement_sub_cls'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_right_goods(conn, tsv_path):
    """2-5: 本権商品名テーブル"""
    print("Importing trademark_right_goods...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_right_goods 
                (processing_type, law_code, reg_num, split_num, app_num,
                 class_num_registered, rec_num, master_update_date,
                 goods_name_length, goods_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['desig_goods_or_desig_wrk_class']),
                cleanse_data(row['rec_num']),
                cleanse_data(row['mstr_updt_year_month_day']),
                cleanse_data(row['desg_gds_desg_wrk_name_len']),
                cleanse_data(row['desg_gds_name_desg_wrk_name'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_right_holders(conn, tsv_path):
    """3-1: 権利者記事テーブル"""
    print("Importing trademark_right_holders...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_right_holders 
                (processing_type, law_code, reg_num, split_num, app_num,
                 rec_num, pe_num, right_person_update_date, right_person_id,
                 right_person_addr_len, right_person_addr,
                 right_person_name_len, right_person_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['rec_num']),
                cleanse_data(row['pe_num']),
                cleanse_data(row['right_psn_art_upd_ymd']),
                cleanse_data(row['right_person_appl_id']),
                cleanse_data(row['right_person_addr_len']),
                cleanse_data(row['right_person_addr']),
                cleanse_data(row['right_person_name_len']),
                cleanse_data(row['right_person_name'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_applicants_agents(conn, tsv_path):
    """3-2: 出願人・代理人情報テーブル"""
    print("Importing trademark_applicants_agents...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_applicants_agents 
                (law_code, app_num, applicant_agent_type, applicant_agent_code,
                 change_num, individual_corp_type, country_prefecture_code,
                 representative_flag, num_above_applicants, num_other_agents,
                 applicant_agent_profession_type, applicant_agent_qualification_type,
                 applicant_agent_address, applicant_agent_name, applicant_agent_seq_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['yonpo_code']),
                normalize_app_num(row['shutugan_no']),
                cleanse_data(row['shutugannindairinin_sikbt']),
                cleanse_data(row['shutugannindairinin_code']),
                cleanse_data(row.get('gez_henko_no')),
                cleanse_data(row.get('gez_kohokan_kubun')),
                cleanse_data(row.get('gez_kokken_code')),
                cleanse_data(row.get('daihyoshutugannin_sikibetu')),
                cleanse_data(row.get('jokishutugannin_nanmei')),
                cleanse_data(row.get('dairininhoka_nanmei')),
                cleanse_data(row.get('dairinin_shubetu')),
                cleanse_data(row.get('dairininsikaku_shubetu')),
                cleanse_data(row.get('shutugannindairinin_jusho')),
                cleanse_data(row.get('shutugannindairinin_simei')),
                cleanse_data(row['gez_junjo_no'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_attorney_articles(conn, tsv_path):
    """3-3: 代理人記事テーブル"""
    print("Importing trademark_attorney_articles...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_attorney_articles 
                (processing_type, law_code, reg_num, split_num, app_num,
                 rec_num, attorney_seq_num, attorney_update_date,
                 attorney_appl_id, attorney_type, attorney_name_length,
                 attorney_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['rec_num']),
                cleanse_data(row['pe_num']),
                cleanse_data(row['atty_art_upd_ymd']),
                cleanse_data(row['atty_appl_id']),
                cleanse_data(row['atty_typ']),
                cleanse_data(row['atty_name_len']),
                cleanse_data(row['atty_name'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_case_info(conn, tsv_path):
    """4-1: 事件情報テーブル - 特許庁仕様書042_事件フォルダ_商標ファイル.csv準拠"""
    print("Importing trademark_case_info...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # 特許庁仕様書の全49項目を完全に反映
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_case_info 
                (master_update_datetime, law_code, app_num, app_date, 
                 app_type1, app_type2, app_type3, app_type4, app_type5,
                 reference_num, final_disposition_type, final_disposition_date,
                 reg_article_reg_num, reg_article_split_num, defensive_num,
                 reg_date, reg_article_total_num, reg_article_annual_num,
                 reg_article_gazette_date, examiner_code, pub_article_gazette_date,
                 class_count, reg_decision_class_count, standard_char_exist,
                 special_mark_exist, color_exist, article3_2_flag, article5_4_flag,
                 orig_app_type, orig_app_law_code, orig_app_num, retroactive_date,
                 defensive_orig_app_num, defensive_orig_reg_num, defensive_orig_split_num,
                 renewal_reg_num, renewal_split_num, renewal_defensive_num,
                 rewrite_reg_num, rewrite_split_num, rewrite_defensive_num,
                 public_order_violation_flag, accelerated_exam_mark,
                 applicable_law_class, exam_type, litigation_code,
                 decision_type, opposition_count, opposition_valid_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row.get('masterkosin_nitiji')),  # 1. マスタ更新日時
                cleanse_data(row.get('yonpo_code', '4')),     # 2. 四法コード
                normalize_app_num(row['shutugan_no']),        # 3. 出願番号
                cleanse_data(row.get('shutugan_bi')),         # 4. 出願日
                cleanse_data(row.get('shutugan_shubetu1')),   # 5. 出願種別1
                cleanse_data(row.get('shutugan_shubetu2')),   # 6. 出願種別2
                cleanse_data(row.get('shutugan_shubetu3')),   # 7. 出願種別3
                cleanse_data(row.get('shutugan_shubetu4')),   # 8. 出願種別4
                cleanse_data(row.get('shutugan_shubetu5')),   # 9. 出願種別5
                cleanse_data(row.get('seiri_no')),            # 10. 整理番号
                cleanse_data(row.get('saishushobun_shubetu')), # 11. 最終処分種別
                cleanse_data(row.get('saishushobun_bi')),     # 12. 最終処分日
                cleanse_data(row.get('raz_toroku_no')),       # 13. 登録記事登録番号
                cleanse_data(row.get('raz_bunkatu_no')),      # 14. 登録記事分割番号
                cleanse_data(row.get('bogo_no')),             # 15. 防護番号
                cleanse_data(row.get('toroku_bi')),           # 16. 登録日
                cleanse_data(row.get('raz_sotugo_su')),       # 17. 登録記事総通号数
                cleanse_data(row.get('raz_nenkantugo_su')),   # 18. 登録記事年間通号数
                cleanse_data(row.get('raz_kohohakko_bi')),    # 19. 登録記事公報発行日
                cleanse_data(row.get('tantokan_code')),       # 20. 担当官コード
                cleanse_data(row.get('pcz_kokaikohohakko_bi')), # 21. 公開公報記事公開公報発行日
                cleanse_data(row.get('kubun_su')),            # 22. 区分数
                cleanse_data(row.get('torokusateijikubun_su')), # 23. 登録査定時区分数
                cleanse_data(row.get('hyojunmoji_umu')),      # 24. 標準文字有無
                cleanse_data(row.get('rittaishohyo_umu')),    # 25. 特殊商標識別
                cleanse_data(row.get('hyoshosikisai_umu')),   # 26. 標章色彩有無
                cleanse_data(row.get('shohyoho3jo2ko_flag')), # 27. 商標法3条2項フラグ
                cleanse_data(row.get('shohyoho5jo4ko_flag')), # 28. 色彩の但し書フラグ
                cleanse_data(row.get('genshutugan_shubetu')), # 29. 原出願種別
                cleanse_data(row.get('genshutuganyonpo_code')), # 30. 原出願四法コード
                cleanse_data(row.get('genshutugan_no')),      # 31. 原出願番号
                cleanse_data(row.get('sokyu_bi')),            # 32. 遡及日
                cleanse_data(row.get('obz_shutugan_no')),     # 33. 防護原登録記事出願番号
                cleanse_data(row.get('obz_toroku_no')),       # 34. 防護原登録記事登録番号
                cleanse_data(row.get('obz_bunkatu_no')),      # 35. 防護原登録記事分割番号
                cleanse_data(row.get('kosintoroku_no')),      # 36. 更新登録番号
                cleanse_data(row.get('pez_bunkatu_no')),      # 37. 更新登録記事分割番号
                cleanse_data(row.get('pez_bogo_no')),         # 38. 更新登録記事防護番号
                cleanse_data(row.get('kakikaetoroku_no')),    # 39. 書換登録番号
                cleanse_data(row.get('ktz_bunkatu_no')),      # 40. 書換登録記事分割番号
                cleanse_data(row.get('ktz_bogo_no')),         # 41. 書換登録記事防護番号
                cleanse_data(row.get('krz_kojoryozokuihan_flag')), # 42. 公序良俗違反フラグ
                cleanse_data(row.get('sokisinsa_mark')),      # 43. 早期審査マーク
                cleanse_data(row.get('tekiyohoki_kubun')),    # 44. 適用法規区分
                cleanse_data(row.get('sinsa_shubetu')),       # 45. 審査種別
                cleanse_data(row.get('sosho_code')),          # 46. 訴訟コード
                cleanse_data(row.get('satei_shubetu')),       # 47. 査定種別
                cleanse_data(row.get('igiken_su')),           # 48. 異議件数
                cleanse_data(row.get('igiyuko_su'))           # 49. 異議有効数
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_basic_items(conn, tsv_path):
    """4-2: 商標基本項目記事テーブル"""
    print("Importing trademark_basic_items...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_basic_items 
                (add_del_id, mgt_num, rec_status_id, app_num, reg_num,
                 split_num, defensive_num, app_typ_sec, app_typ_split,
                 app_typ_complement_rjct, app_typ_chan, app_typ_priorty,
                 app_typ_group, app_typ_area_group, app_date,
                 prior_app_right_occr_date, rjct_finl_dcsn_dsptch_date,
                 final_disposition_code, final_disposition_date,
                 rewrite_app_num, old_law, ver_num, intl_reg_num,
                 intl_reg_split_num, intl_reg_date, rec_latest_updt_date,
                 conti_prd_expire_date, instllmnt_expr_date_aft_des_date,
                 installments_id, set_reg_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                cleanse_data(row['mgt_num']),
                cleanse_data(row['rec_status_id']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row.get('sec_num', '000')),
                cleanse_data(row['app_typ_sec']),
                cleanse_data(row['app_typ_split']),
                cleanse_data(row['app_typ_complement_rjct']),
                cleanse_data(row['app_typ_chan']),
                cleanse_data(row['app_typ_priorty']),
                cleanse_data(row['app_typ_group']),
                cleanse_data(row['app_typ_area_group']),
                cleanse_data(row['app_dt']),
                cleanse_data(row.get('prior_app_right_occr_dt')),
                cleanse_data(row.get('rjct_finl_dcsn_dsptch_dt')),
                cleanse_data(row.get('final_dspst_cd')),
                cleanse_data(row.get('final_dspst_dt')),
                cleanse_data(row.get('rwrt_app_num')),
                cleanse_data(row.get('old_law')),
                cleanse_data(row.get('ver_num')),
                cleanse_data(row.get('intl_reg_num')),
                cleanse_data(row.get('intl_reg_split_num')),
                cleanse_data(row.get('intl_reg_dt')),
                cleanse_data(row.get('rec_latest_updt_dt')),
                cleanse_data(row.get('conti_prd_expire_dt')),
                cleanse_data(row.get('instllmnt_expr_dt_aft_des_dt')),
                cleanse_data(row.get('installments_id')),
                cleanse_data(row.get('set_reg_dt'))
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_first_display(conn, tsv_path):
    """4-3: 商標第一表示部テーブル"""
    print("Importing trademark_first_display...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_first_display 
                (processing_type, law_code, reg_num, split_num,
                 history_num, master_update_date, cancel_disposal_flag,
                 intl_reg_num, intl_reg_date, after_designation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['history_num']),
                cleanse_data(row['mstr_updt_year_month_day']),
                cleanse_data(row['cancel_and_disposal_id']),
                cleanse_data(row['intl_reg_num']),
                cleanse_data(row['intl_reg_year_month_day']),
                cleanse_data(row['aft_desig_year_month_day'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_management_info(conn, tsv_path):
    """5-1: 管理情報テーブル"""
    print("Importing trademark_management_info...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_management_info 
                (processing_type, law_code, reg_num, split_num, master_update_date,
                 tscript_inspct_prhbt_flg, conti_prd_expire_date, next_pen_payment_limit_date,
                 last_pymnt_yearly, share_rate, pblc_prvt_trnsfr_reg_date, right_ersr_id,
                 right_disppr_date, close_orgnl_reg_trnsfr_rec_flg, close_reg_date,
                 gvrnmnt_relation_id_flg, pen_suppl_flg, apply_law, group_t_flg,
                 special_mark_exist, standard_char_exist, area_group_t_flg, trust_reg_flg,
                 app_num, recvry_num, app_date, app_exam_pub_num, app_exam_pub_date,
                 final_decision_date, trial_decision_date, set_reg_date, t_rewrite_app_num,
                 t_rewrite_app_date, t_rewrite_final_decision_date, t_rewrite_trial_decision_date,
                 t_rewrite_reg_date, invent_title_etc_len, pri_cntry_name_cd, pri_claim_date, pri_clim_cnt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['mstr_updt_year_month_day']),
                cleanse_data(row['tscript_inspct_prhbt_flg']),
                cleanse_data(row['conti_prd_expire_ymd']),
                cleanse_data(row['next_pen_pymnt_tm_lmt_ymd']),
                cleanse_data(row['last_pymnt_yearly']),
                cleanse_data(row['share_rate']),
                cleanse_data(row['pblc_prvt_trnsfr_reg_ymd']),
                cleanse_data(row['right_ersr_id']),
                cleanse_data(row['right_disppr_year_month_day']),
                cleanse_data(row['close_orgnl_reg_trnsfr_rec_flg']),
                cleanse_data(row['close_reg_year_month_day']),
                cleanse_data(row['gvrnmnt_relation_id_flg']),
                cleanse_data(row['pen_suppl_flg']),
                cleanse_data(row['apply_law']),
                cleanse_data(row['group_t_flg']),
                cleanse_data(row['special_t_id']),
                cleanse_data(row['standard_char_t_flg']),
                cleanse_data(row['area_group_t_flg']),
                cleanse_data(row['trust_reg_flg']),
                normalize_app_num(row['app_num']),
                cleanse_data(row.get('recvry_num')),
                cleanse_data(row['app_year_month_day']),
                cleanse_data(row.get('app_exam_pub_num')),
                cleanse_data(row.get('app_exam_pub_year_month_day')),
                cleanse_data(row.get('finl_dcsn_year_month_day')),
                cleanse_data(row.get('trial_dcsn_year_month_day')),
                cleanse_data(row.get('set_reg_year_month_day')),
                cleanse_data(row.get('t_rwrt_app_num')),
                cleanse_data(row.get('t_rwrt_app_year_month_day')),
                cleanse_data(row.get('t_rwrt_finl_dcsn_ymd')),
                cleanse_data(row.get('t_rwrt_trial_dcsn_ymd')),
                cleanse_data(row.get('t_rwrt_reg_year_month_day')),
                cleanse_data(row.get('invent_title_etc_len')),
                cleanse_data(row.get('pri_cntry_name_cd')),
                cleanse_data(row.get('pri_clim_year_month_day')),
                cleanse_data(row.get('pri_clim_cnt'))
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_updates(conn, tsv_path):
    """5-2: 商標更新記事テーブル"""
    print("Importing trademark_updates...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_updates 
                (processing_type, law_code, reg_num, split_num, app_num,
                 pe_num, t_updt_art_update_date, t_updt_app_num,
                 t_updt_temp_reg_flg, t_updt_title_chan_flg,
                 t_updt_recovery_num, t_updt_app_date,
                 t_updt_final_decision_date, t_updt_trial_decision_date,
                 t_updt_reg_date, mu_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['pe_num']),
                cleanse_data(row['t_updt_art_upd_ymd']),
                cleanse_data(row['t_updt_app_num']),
                cleanse_data(row['t_updt_temp_reg_flg']),
                cleanse_data(row['t_updt_title_chan_flg']),
                cleanse_data(row['t_updt_recovery_num']),
                cleanse_data(row['t_updt_app_ymd_app_ymd']),
                cleanse_data(row.get('t_updt_finl_dcsn_ymd')),
                cleanse_data(row.get('t_updt_trial_dcsn_ymd')),
                cleanse_data(row['t_updt_reg_year_month_day']),
                cleanse_data(row['mu_num'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_progress_info(conn, tsv_path):
    """5-3: 経過情報部テーブル"""
    print("Importing trademark_progress_info...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            app_num = normalize_app_num(row['app_num'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_progress_info (
                    processing_type, law_code, reg_num, split_num,
                    app_num, rec_num, pe_num, progress_update_date,
                    reg_intermediate_code, correspondence_mark,
                    process_date, progress_app_num, receipt_num
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']), 
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']), 
                cleanse_data(row['split_num']),
                app_num, 
                cleanse_data(row['rec_num']),
                cleanse_data(row['pe_num']), 
                cleanse_data(row['prog_info_upd_ymd']),
                cleanse_data(row['reg_intrmd_cd']), 
                cleanse_data(row['crrspnd_mk']),
                cleanse_data(row['rcpt_pymnt_dsptch_ymd']),
                cleanse_data(row['prog_info_div_app_num']),
                cleanse_data(row['rcpt_num_common_use'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_rewrite_applications(conn, tsv_path):
    """5-4: 書換申請番号テーブル"""
    print("Importing trademark_rewrite_applications...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_rewrite_applications 
                (processing_type, law_code, reg_num, split_num,
                 app_num, mrgn_info_update_date, mu_num, rewrite_app_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['mrgn_info_upd_ymd']),
                cleanse_data(row['mu_num']),
                cleanse_data(row['mrgn_t_rwrt_app_num'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_transfer_receipts(conn, tsv_path):
    """5-5: 移転受付情報テーブル"""
    print("Importing trademark_transfer_receipts...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_transfer_receipts 
                (processing_type, law_code, reg_num, split_num,
                 app_num, mrgn_info_update_date, mu_num, transfer_receipt_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['mrgn_info_upd_ymd']),
                cleanse_data(row['mu_num']),
                cleanse_data(row['trnsfr_rcpt_info'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_appeal_cases(conn, tsv_path):
    """6-1: 審判事件テーブル"""
    print("Importing trademark_appeal_cases...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # 商標のみ（law_divisionが4）をフィルタリング
            if row.get('ynpu_kbn') != '4':
                continue
                
            app_num = normalize_app_num(row.get('sytgn_bngu'))
            
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_appeal_cases (
                    delete_flag, appeal_num, app_num, law_division,
                    reg_num, split_num, similar_num, defensive_num,
                    appeal_level_type, appeal_type, appeal_request_date,
                    app_num_division, appeal_final_disposition_code,
                    final_disposition_confirm_date, update_datetime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['skbt_flg']),
                cleanse_data(row['snpn_bngu']),
                app_num,
                cleanse_data(row['ynpu_kbn']),
                cleanse_data(row.get('turk_bngu')),
                cleanse_data(row.get('bnkt_bngu')),
                cleanse_data(row.get('riz_bngu')),
                cleanse_data(row.get('bug_bngu')),
                cleanse_data(row['snkyu_sybt']),
                cleanse_data(row['snpn_sybt']),
                cleanse_data(row['snpn_sikyu_dt']),
                cleanse_data(row['sytgn_bngu_kbn']),
                cleanse_data(row.get('snpn_zkn_sisyu_sybn_cd')),
                cleanse_data(row.get('sisyu_sybn_kkti_dt')),
                cleanse_data(row['kusn_ntz_bat'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_decision_classifications(conn, tsv_path):
    """6-2: 審決分類テーブル"""
    print("Importing trademark_decision_classifications...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_decision_classifications (
                    delete_flag, appeal_num, decision_num, repeat_num,
                    law_division, applied_law_identification, appeal_level_type,
                    appeal_type, judgment_item_code, decision_classification_conclusion_code,
                    auxiliary_classification_identification, update_datetime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['skbt_flg']),
                cleanse_data(row['snpn_bngu']),
                cleanse_data(row['snkt_bngu']),
                cleanse_data(row['krkes_bngu']),
                cleanse_data(row['ynpu_kbn']),
                cleanse_data(row.get('tkyu_huk_skbt')),
                cleanse_data(row['snkyu_sybt']),
                cleanse_data(row['snpn_sybt']),
                cleanse_data(row['hnz_zku_cd']),
                cleanse_data(row['snkt_bnri_ktrn_cd']),
                cleanse_data(row.get('hj_bnri_skbt')),
                cleanse_data(row['kusn_ntz_bat'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_oppositions(conn, tsv_path):
    """6-3: 異議申立テーブル"""
    print("Importing trademark_oppositions...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_oppositions (
                    delete_flag, appeal_num, opposition_num,
                    opposition_app_date, opposition_final_disposition_code,
                    final_disposition_confirm_date, update_datetime
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['skbt_flg']),
                cleanse_data(row['snpn_bngu']),
                cleanse_data(row['mustt_bngu']),
                cleanse_data(row['ig_mustt_dt']),
                cleanse_data(row['ig_mustt_sisyu_sybn_cd']),
                cleanse_data(row.get('sisyu_sybn_kkti_dt')),
                cleanse_data(row['kusn_ntz_bat'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_opposition_decisions(conn, tsv_path):
    """6-4: 異議決定テーブル"""
    print("Importing trademark_opposition_decisions...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_opposition_decisions (
                    delete_flag, appeal_num, opposition_num, decision_num,
                    dispatch_doc_num, decision_confirmation_status, update_datetime
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['skbt_flg']),
                cleanse_data(row['snpn_bngu']),
                cleanse_data(row['mustt_bngu']),
                cleanse_data(row['ig_ktti_bngu']),
                cleanse_data(row['hssu_syri_bngu']),
                cleanse_data(row['ig_ktti_kkti_stat']),
                cleanse_data(row['kusn_ntz_bat'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_draft_records(conn, tsv_path):
    """7-1: 起案中間記録テーブル"""
    print("Importing trademark_draft_records...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # 商標のみ（law_codeが4）をフィルタリング
            if row.get('yonpo_code') != '4':
                continue
                
            app_num = normalize_app_num(row['shutugan_no'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_draft_records (
                    law_code, app_num, folder_creation_seq_num,
                    creation_date, intermediate_doc_code, response_mark,
                    draft_date, dispatch_date, objection_num,
                    document_num, rejection_reason_code, corresponding_doc_num,
                    document_type, version_num
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['yonpo_code']),
                app_num,
                int(row['folderbetusakusejnj_no']) if row.get('folderbetusakusejnj_no') else 0,
                cleanse_data(row['sakusei_bi']),
                cleanse_data(row['chukanshorui_code']),
                cleanse_data(row['taio_mark']),
                cleanse_data(row['kian_bi']),
                cleanse_data(row['hasso_bi']),
                cleanse_data(row.get('aaz_igi_no')),
                cleanse_data(row['shorui_no']),
                cleanse_data(row.get('kyozeturiyujobun_code')),
                cleanse_data(row['taioshorui_no']),
                cleanse_data(row['shorui_shubetu']),
                cleanse_data(row['version_no'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_application_records(conn, tsv_path):
    """7-2: 申請中間記録テーブル"""
    print("Importing trademark_application_records...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # 商標のみ（law_codeが4）をフィルタリング
            if row.get('yonpo_code') != '4':
                continue
                
            app_num = normalize_app_num(row['shutugan_no'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_application_records (
                    law_code, app_num, folder_creation_seq_num,
                    creation_date, intermediate_doc_code, correspondence_mark,
                    dispatch_date, receipt_date, opposition_num,
                    doc_num, procedure_complete_mark, order_complete_flag,
                    corresponding_doc_num, doc_type, version_num,
                    viewing_restriction_flag
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['yonpo_code']),
                app_num,
                int(row['folderbetusakusejnj_no']) if row.get('folderbetusakusejnj_no') else 0,
                cleanse_data(row['sakusei_bi']),
                cleanse_data(row['chukanshorui_code']),
                cleanse_data(row['taio_mark']),
                cleanse_data(row['sasidasi_bi']),
                cleanse_data(row['uketuke_bi']),
                cleanse_data(row.get('aaz_igi_no')),
                cleanse_data(row['shorui_no']),
                cleanse_data(row['hosikikan_mark']),
                cleanse_data(row['sireikan_flag']),
                cleanse_data(row['taioshorui_no']),
                cleanse_data(row['shorui_shubetu']),
                cleanse_data(row['version_no']),
                cleanse_data(row['eturankinsi_flag'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_priority_claims(conn, tsv_path):
    """8-1: 優先権情報テーブル"""
    print("Importing trademark_priority_claims...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # 商標のみ（law_codeが4）をフィルタリング
            if row.get('yonpo_code') != '4':
                continue
                
            app_num = normalize_app_num(row['shutugan_no'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_priority_claims (
                    law_code, app_num, priority_seq_num, priority_country_code,
                    priority_app_num, priority_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['yonpo_code']),
                app_num,
                int(row['bmz_junjo_no']) if row.get('bmz_junjo_no') else 1,
                cleanse_data(row['yusenkenkuni_code']),
                cleanse_data(row['yusenkenshutugan_no']),
                cleanse_data(row['yusenkenshucho_bi'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_gazette_publications(conn, tsv_path):
    """8-2: 公報発行情報テーブル"""
    print("Importing trademark_gazette_publications...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # 商標のみ（law_codeが4）をフィルタリング
            if row.get('yonpo_code') != '4':
                continue
                
            app_num = normalize_app_num(row['shutugan_no'])
            
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_gazette_publications (
                    law_code, app_num, gazette_seq_num, total_serial_num,
                    annual_serial_num, dept_serial_num, dept_annual_serial_num,
                    gazette_publication_date, correction_type, gazette_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['yonpo_code']),
                app_num,
                int(row['jaz_junjo_no']) if row.get('jaz_junjo_no') else 1,
                cleanse_data(row['jaz_sotugo_su']),
                cleanse_data(row['jaz_nenkantugo_su']),
                cleanse_data(row.get('jaz_bumonbetutugo_su')),
                cleanse_data(row.get('jaz_bumonbetunenkantugo_su')),
                cleanse_data(row['jaz_kohohakko_bi']),
                cleanse_data(row['jaz_seigo_sikibetu']),
                cleanse_data(row['jaz_koho_sikibetu'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_applicant_registration_info(conn, tsv_path):
    """9-1: 申請人登録情報テーブル"""
    print("Importing applicant_registration_info...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO applicant_registration_info (
                    data_id_code, applicant_code, applicant_name,
                    applicant_kana_name, applicant_postal_code, applicant_address,
                    roman_name, roman_address, integrated_applicant_code,
                    double_reg_integration_num
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['data_id_cd']),
                cleanse_data(row['appl_cd']),
                cleanse_data(row['appl_name']),
                cleanse_data(row['appl_cana_name']),
                cleanse_data(row['appl_postcode']),
                cleanse_data(row['appl_addr']),
                cleanse_data(row['wes_join_name']),
                cleanse_data(row['wes_join_addr']),
                cleanse_data(row['integ_appl_cd']),
                int(row['dbl_reg_integ_mgt_srl_num']) if row.get('dbl_reg_integ_mgt_srl_num') else 0
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_intl_trademark_registration(conn, tsv_path):
    """10-1: 国際商標登録管理情報テーブル"""
    print("Importing intl_trademark_registration...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO intl_trademark_registration (
                    add_del_id, intl_reg_num, intl_reg_num_update_count_code,
                    intl_reg_num_split_code, after_designation_date, intl_reg_date,
                    jpo_reference_num, jpo_reference_num_split_code, set_registration_date,
                    right_erasure_id, right_disappearance_date, close_registration_date,
                    inspection_prohibition_flag, define_flag, update_date, batch_update_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                cleanse_data(row['intl_reg_num']),
                cleanse_data(row['intl_reg_num_updt_cnt_sign_cd']),
                cleanse_data(row['intl_reg_num_split_sign_cd']),
                cleanse_data(row['aft_desig_year_month_day']),
                cleanse_data(row['intl_reg_year_month_day']),
                cleanse_data(row['jpo_rfr_num']),
                cleanse_data(row['jpo_rfr_num_split_sign_cd']),
                cleanse_data(row['set_reg_year_month_day']),
                cleanse_data(row['right_ersr_id']),
                cleanse_data(row['right_disppr_year_month_day']),
                cleanse_data(row['close_reg_year_month_day']),
                cleanse_data(row['inspct_prhbt_flg']),
                cleanse_data(row['define_flg']),
                cleanse_data(row['updt_year_month_day']),
                cleanse_data(row['batch_updt_year_month_day'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_intl_trademark_progress(conn, tsv_path):
    """10-2: 国際商標経過情報テーブル"""
    print("Importing intl_trademark_progress...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO intl_trademark_progress (
                    add_del_id, intl_reg_num, intl_reg_num_update_count_code,
                    intl_reg_num_split_code, after_designation_date, intermediate_code,
                    storage_num, intermediate_def_date_1, intermediate_def_date_2,
                    intermediate_def_date_3, intermediate_def_date_4, intermediate_def_date_5,
                    correspondence_mark, define_flag, status, update_date, batch_update_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                cleanse_data(row['intl_reg_num']),
                cleanse_data(row['intl_reg_num_updt_cnt_sign_cd']),
                cleanse_data(row['intl_reg_num_split_sign_cd']),
                cleanse_data(row['aft_desig_year_month_day']),
                cleanse_data(row['intrmd_cd']),
                cleanse_data(row['string_num']),
                cleanse_data(row['intrmd_dfn_1_dt']),
                cleanse_data(row['intrmd_dfn_2_dt']),
                cleanse_data(row['intrmd_dfn_3_dt']),
                cleanse_data(row['intrmd_dfn_4_dt']),
                cleanse_data(row['intrmd_dfn_5_dt']),
                cleanse_data(row['crrspnd_mk']),
                cleanse_data(row['define_flg']),
                cleanse_data(row['stts']),
                cleanse_data(row['updt_year_month_day']),
                cleanse_data(row['batch_updt_year_month_day'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_intl_trademark_holders(conn, tsv_path):
    """10-3: 国際商標名義人テーブル"""
    print("Importing intl_trademark_holders...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO intl_trademark_holders (
                    add_del_id, intl_reg_num, intl_reg_num_update_count_code,
                    intl_reg_num_split_code, after_designation_date,
                    temp_principal_reg_id_flag, display_seq, holder_input_seq_num,
                    holder_name, holder_address, define_flag, update_date, batch_update_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                cleanse_data(row['intl_reg_num']),
                cleanse_data(row['intl_reg_num_updt_cnt_sign_cd']),
                cleanse_data(row['intl_reg_num_split_sign_cd']),
                cleanse_data(row['aft_desig_year_month_day']),
                cleanse_data(row['temp_principal_reg_id_flg']),
                int(row['indct_seq']) if row.get('indct_seq') else 0,
                int(row['crrcter_input_seq_num']) if row.get('crrcter_input_seq_num') else 0,
                cleanse_data(row['crrcter_name']),
                cleanse_data(row['crrcter_addr']),
                cleanse_data(row['define_flg']),
                cleanse_data(row['updt_year_month_day']),
                cleanse_data(row['batch_updt_year_month_day'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_intl_trademark_goods_services(conn, tsv_path):
    """10-4: 国際商標商品・役務テーブル"""
    print("Importing intl_trademark_goods_services...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO intl_trademark_goods_services (
                    add_del_id, intl_reg_num, intl_reg_num_update_count_code,
                    intl_reg_num_split_code, after_designation_date,
                    temp_principal_reg_id_flag, display_seq, seq_num,
                    madpro_class, goods_service_name, intl_reg_record_date,
                    define_flag, update_date, batch_update_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                cleanse_data(row['intl_reg_num']),
                cleanse_data(row['intl_reg_num_updt_cnt_sign_cd']),
                cleanse_data(row['intl_reg_num_split_sign_cd']),
                cleanse_data(row['aft_desig_year_month_day']),
                cleanse_data(row['temp_principal_reg_id_flg']),
                int(row['indct_seq']) if row.get('indct_seq') else 0,
                int(row['seq_num']) if row.get('seq_num') else 0,
                cleanse_data(row['madopro_class']),
                cleanse_data(row['goods_service_name']),
                cleanse_data(row['intl_reg_rec_dt']),
                cleanse_data(row['define_flg']),
                cleanse_data(row['updt_year_month_day']),
                cleanse_data(row['batch_updt_year_month_day'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_intl_trademark_first_indication(conn, tsv_path):
    """10-5: 国際商標第一表示部テーブル"""
    print("Importing intl_trademark_first_indication...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO intl_trademark_first_indication (
                    add_del_id, intl_reg_num, intl_reg_num_update_count_code,
                    intl_reg_num_split_code, after_designation_date,
                    temp_principal_reg_id_flag, display_seq, final_decision_date,
                    trial_decision_date, priority_app_country_code, priority_app_date,
                    priority_claim_count, special_trademark_type_flag,
                    group_cert_warranty_flag, define_flag, update_date,
                    batch_update_date, trademark_detailed_explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                cleanse_data(row['intl_reg_num']),
                cleanse_data(row['intl_reg_num_updt_cnt_sign_cd']),
                cleanse_data(row['intl_reg_num_split_sign_cd']),
                cleanse_data(row['aft_desig_year_month_day']),
                cleanse_data(row['temp_principal_reg_id_flg']),
                int(row['indct_seq']) if row.get('indct_seq') else 0,
                cleanse_data(row['finl_dcsn_year_month_day']),
                cleanse_data(row['trial_dcsn_year_month_day']),
                cleanse_data(row['pri_app_gvrn_cntrcntry_cd']),
                cleanse_data(row['pri_app_year_month_day']),
                cleanse_data(row['pri_clim_cnt']),
                cleanse_data(row['special_t_typ_flg']),
                cleanse_data(row['group_cert_warranty_flg']),
                cleanse_data(row['define_flg']),
                cleanse_data(row['updt_year_month_day']),
                cleanse_data(row['batch_updt_year_month_day']),
                cleanse_data(row['t_dtl_explntn'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_design_state_gvrnmnt_mstr_mk(conn, tsv_path):
    """指定国官庁マスタ_マークファイル"""
    print("Importing design_state_gvrnmnt_mstr_mk...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO design_state_gvrnmnt_mstr_mk (
                    add_del_id, jpo_rfr_num, jpo_rfr_num_split_sign_cd, history_num,
                    standard_char_declarat_flg, color_clim_detail, color_clim_detail_japanese,
                    emblem_transliterat_detail, three_dmns_emblem_flg, sound_t_flg,
                    group_cert_warranty_flg, emblem_doc_detail, emblem_doc_detail_japanese,
                    vienna_class, exam_art_03_prgrph_02_flg, exam_color_proviso_apply_flg,
                    exam_art_09_prgrph_01_flg, acclrtd_exam_class, define_flg,
                    updt_year_month_day, batch_updt_year_month_day, special_t_typ,
                    t_dtl_explntn, t_dtl_explntn_japanese, dtl_explntn_doc_submt_dt,
                    color_chk_box, disclaimer, opt_emblem_doc_detail, opt_emblem_doc_detail_jp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row.get('add_del_id')),
                cleanse_data(row.get('jpo_rfr_num')),
                cleanse_data(row.get('jpo_rfr_num_split_sign_cd')),
                cleanse_data(row.get('history_num')),
                cleanse_data(row.get('standard_char_declarat_flg')),
                cleanse_data(row.get('color_clim_detail')),
                cleanse_data(row.get('color_clim_detail_japanese')),
                cleanse_data(row.get('emblem_transliterat_detail')),
                cleanse_data(row.get('three_dmns_emblem_flg')),
                cleanse_data(row.get('sound_t_flg')),
                cleanse_data(row.get('group_cert_warranty_flg')),
                cleanse_data(row.get('emblem_doc_detail')),
                cleanse_data(row.get('emblem_doc_detail_japanese')),
                cleanse_data(row.get('vienna_class')),
                cleanse_data(row.get('exam_art_03_prgrph_02_flg')),
                cleanse_data(row.get('exam_color_proviso_apply_flg')),
                cleanse_data(row.get('exam_art_09_prgrph_01_flg')),
                cleanse_data(row.get('acclrtd_exam_class')),
                cleanse_data(row.get('define_flg')),
                cleanse_data(row.get('updt_year_month_day')),
                cleanse_data(row.get('batch_updt_year_month_day')),
                cleanse_data(row.get('special_t_typ')),
                cleanse_data(row.get('t_dtl_explntn')),
                cleanse_data(row.get('t_dtl_explntn_japanese')),
                cleanse_data(row.get('dtl_explntn_doc_submt_dt')),
                cleanse_data(row.get('color_chk_box')),
                cleanse_data(row.get('disclaimer')),
                cleanse_data(row.get('opt_emblem_doc_detail')),
                cleanse_data(row.get('opt_emblem_doc_detail_jp'))
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_design_state_gvrnmnt_mstr_pri(conn, tsv_path):
    """指定国官庁マスタ_優先権ファイル"""
    print("Importing design_state_gvrnmnt_mstr_pri...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO design_state_gvrnmnt_mstr_pri (
                    add_del_id, jpo_rfr_num, jpo_rfr_num_split_sign_cd, history_num,
                    pri_clim_id, pri_finding_flg, pri_app_gvrn_cntrcntry_cd,
                    pri_app_num, pri_app_year_month_day, define_flg,
                    updt_year_month_day, batch_updt_year_month_day
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row.get('add_del_id')),
                cleanse_data(row.get('jpo_rfr_num')),
                cleanse_data(row.get('jpo_rfr_num_split_sign_cd')),
                cleanse_data(row.get('history_num')),
                int(row['pri_clim_id']) if row.get('pri_clim_id') else 0,
                cleanse_data(row.get('pri_finding_flg')),
                cleanse_data(row.get('pri_app_gvrn_cntrcntry_cd')),
                cleanse_data(row.get('pri_app_num')),
                cleanse_data(row.get('pri_app_year_month_day')),
                cleanse_data(row.get('define_flg')),
                cleanse_data(row.get('updt_year_month_day')),
                cleanse_data(row.get('batch_updt_year_month_day'))
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_trademark_images(conn, tsv_path):
    """11-1: 商標画像テーブル"""
    print("Importing trademark_images...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        # 複数行データを結合するためのバッファ
        images = {}
        
        for row in reader:
            app_num = normalize_app_num(row.get('app_num'))
            
            key = (
                row['doc_num'], 
                row['page_num'], 
                row['rec_seq_num'], 
                row['year_issu_cd']
            )
            
            if key not in images:
                images[key] = {
                    'country_code': cleanse_data(row['cntry_cd']),
                    'doc_type': cleanse_data(row['doc_typ']),
                    'doc_num': cleanse_data(row['doc_num']),
                    'app_num': app_num,
                    'page_num': cleanse_data(row['page_num']),
                    'rec_seq_num': int(row['rec_seq_num']),
                    'year_issue_code': cleanse_data(row['year_issu_cd']),
                    'data_creation_date': cleanse_data(row['data_crt_dt']),
                    'all_page_count': cleanse_data(row['all_page_cnt']),
                    'final_rec_seq_num': int(row['final_rec_seq_num']) if row.get('final_rec_seq_num') else None,
                    'fullsize_length': cleanse_data(row['fullsize_length']),
                    'fullsize_width': cleanse_data(row['fullsize_width']),
                    'compression_format': cleanse_data(row['comp_frmlchk']),
                    'resolution': cleanse_data(row['resolution']),
                    'line_count_length': cleanse_data(row['linecnt_length']),
                    'line_count_width': cleanse_data(row['linecnt_width']),
                    'image_data_length': cleanse_data(row['image_data_len']),
                    'image_data': row['image_data']  # base64データ
                }
            else:
                # 複数行の場合はデータを結合
                images[key]['image_data'] += row['image_data']
        
        # 結合されたデータをインサート
        for img in images.values():
            cursor.execute("""
                INSERT OR REPLACE INTO trademark_images (
                    country_code, doc_type, doc_num, app_num, page_num,
                    rec_seq_num, year_issue_code, data_creation_date,
                    all_page_count, final_rec_seq_num, fullsize_length,
                    fullsize_width, compression_format, resolution,
                    line_count_length, line_count_width, image_data_length,
                    image_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                img['country_code'], img['doc_type'], img['doc_num'],
                img['app_num'], img['page_num'], img['rec_seq_num'],
                img['year_issue_code'], img['data_creation_date'],
                img['all_page_count'], img['final_rec_seq_num'],
                img['fullsize_length'], img['fullsize_width'],
                img['compression_format'], img['resolution'],
                img['line_count_length'], img['line_count_width'],
                img['image_data_length'], img['image_data']
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_bougo_hyosho_articles(conn, tsv_path):
    """12-1: 防護標章記事テーブル"""
    print("Importing bougo_hyosho_articles...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO bougo_hyosho_articles (
                    processing_type, law_code, reg_num, split_num, app_num, pe_num,
                    defensive_art_upd_date, defensive_app_num, defensive_num,
                    defensive_temp_reg_flg, defensive_conti_prd_expire_date,
                    defensive_ersr_flg, defensive_apply_law, defensive_recovery_num,
                    defensive_app_date, defensive_app_exam_pub_num,
                    defensive_app_exam_pub_date, defensive_finl_dcsn_date,
                    defensive_trial_dcsn_date, defensive_reg_date,
                    defensive_rwrt_app_num, defensive_rwrt_app_date,
                    defensive_rwrt_finl_dcsn_date, defensive_rwrt_trial_dcsn_date,
                    defensive_rwrt_reg_date, mu_num, defensive_desig_goods_desig_wrk_cls
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['pe_num']),
                cleanse_data(row['sec_art_upd_ymd']),
                cleanse_data(row['sec_app_num']),
                cleanse_data(row['sec_num']),
                cleanse_data(row['sec_temp_reg_flg']),
                cleanse_data(row['sec_conti_prd_expire_ymd']),
                cleanse_data(row['sec_ersr_flg']),
                cleanse_data(row['sec_apply_law']),
                cleanse_data(row['sec_recovery_num']),
                cleanse_data(row['sec_app_year_month_day']),
                cleanse_data(row['sec_app_exam_pub_num']),
                cleanse_data(row['sec_app_exam_pub_ymd']),
                cleanse_data(row['sec_finl_dcsn_year_month_day']),
                cleanse_data(row['sec_trial_dcsn_year_month_day']),
                cleanse_data(row['sec_reg_year_month_day']),
                cleanse_data(row['sec_rwrt_app_num']),
                cleanse_data(row['sec_rwrt_app_year_month_day']),
                cleanse_data(row['sec_rwrt_finl_dcsn_ymd']),
                cleanse_data(row['sec_rwrt_trial_dcsn_ymd']),
                cleanse_data(row['sec_rwrt_reg_year_month_day']),
                cleanse_data(row['mu_num']),
                cleanse_data(row['sec_desig_goods_desig_wrk_cls'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_bougo_shohin_mei(conn, tsv_path):
    """12-2: 防護商品名テーブル"""
    print("Importing bougo_shohin_mei...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO bougo_shohin_mei (
                    processing_type, law_code, reg_num, split_num,
                    defensive_num, defensive_app_num, defensive_desig_goods_desig_wrk_cls,
                    master_update_date, defensive_desig_gds_desig_wrk_nm_len,
                    defensive_desig_gds_nm_desig_wrk_nm
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sec_num']),
                cleanse_data(row['sec_app_num']),
                cleanse_data(row['sec_desig_goods_desig_wrk_cls']),
                cleanse_data(row['mstr_updt_year_month_day']),
                cleanse_data(row['sec_desig_gds_desig_wrk_nm_len']),
                cleanse_data(row['sec_desig_gds_nm_desig_wrk_nm'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_bougo_koshin_kiji(conn, tsv_path):
    """12-3: 防護更新記事テーブル"""
    print("Importing bougo_koshin_kiji...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO bougo_koshin_kiji (
                    processing_type, law_code, reg_num, split_num, app_num, pe_num,
                    defensive_updt_art_upd_date, defensive_updt_app_num,
                    defensive_updt_num, defensive_updt_temp_reg_flg,
                    defensive_updt_title_chan_flg, defensive_updt_recovery_num,
                    defensive_updt_app_date, defensive_updt_finl_dcsn_date,
                    defensive_updt_trial_dcsn_date, defensive_updt_reg_date, mu_num
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['processing_type']),
                cleanse_data(row['law_cd']),
                cleanse_data(row['reg_num']),
                cleanse_data(row['split_num']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['pe_num']),
                cleanse_data(row['sec_updt_art_upd_ymd']),
                cleanse_data(row['sec_updt_app_num']),
                cleanse_data(row['sec_updt_sec_num']),
                cleanse_data(row['sec_updt_temp_reg_flg']),
                cleanse_data(row['sec_updt_title_chan_flg']),
                cleanse_data(row['sec_updt_recovery_num']),
                cleanse_data(row['sec_updt_app_year_month_day']),
                cleanse_data(row['sec_updt_finl_dcsn_ymd']),
                cleanse_data(row['sec_updt_trial_dcsn_ymd']),
                cleanse_data(row['sec_updt_reg_year_month_day']),
                cleanse_data(row['mu_num'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_shohyo_fuka_joho(conn, tsv_path):
    """13-1: 商標付加情報テーブル"""
    print("Importing shohyo_fuka_joho...")
    encoding = detect_encoding(tsv_path)
    cursor = conn.cursor()
    count = 0
    
    with open(tsv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO shohyo_fuka_joho (
                    add_del_id, app_num, split_num, sub_data_num,
                    right_request, grphc_id, color_harftone, gdmral_flg,
                    duplicate_reg_flg, special_exception_clim_flg, consent_coe_reg_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleanse_data(row['add_del_id']),
                normalize_app_num(row['app_num']),
                cleanse_data(row['split_num']),
                cleanse_data(row['sub_data_num']),
                cleanse_data(row['right_request']),
                cleanse_data(row['grphc_id']),
                cleanse_data(row['color_harftone']),
                cleanse_data(row['gdmral_flg']),
                cleanse_data(row['duplicate_reg_flg']),
                cleanse_data(row['special_exception_clim_flg']),
                cleanse_data(row['consent_coe_reg_id'])
            ))
            count += 1
    
    conn.commit()
    print(f"  Imported {count} records")
    return count

def import_all_tables(conn):
    """全テーブルのインポート"""
    
    # TSVファイルとインポート関数のマッピング
    import_mappings = [
        ('upd_standard_char_t_art.tsv', import_trademark_standard_char),
        ('upd_indct_use_t_art.tsv', import_trademark_display),
        ('upd_search_use_t_art_table.tsv', import_trademark_search),
        ('upd_t_dsgnt_art.tsv', import_trademark_pronunciation),
        ('upd_jiken_c_t_shousaina_setumei.tsv', import_trademark_detailed_descriptions),
        ('upd_jiken_c_t_shohin_joho.tsv', import_goods_services_info),
        ('upd_goods_class_art.tsv', import_trademark_goods_classes),
        ('upd_t_knd_info_art_table.tsv', import_trademark_similar_group_codes),
        ('upd_t_vienna_class_grphc_term_art.tsv', import_trademark_vienna_codes),
        ('upd_right_goods_name.tsv', import_trademark_right_goods),
        ('upd_right_person_art_t.tsv', import_trademark_right_holders),
        ('upd_jiken_c_t_shutugannindairinin.tsv', import_trademark_applicants_agents),
        ('upd_atty_art_t.tsv', import_trademark_attorney_articles),
        ('upd_jiken_c_t.tsv', import_case_info),
        ('upd_t_basic_item_art.tsv', import_trademark_basic_items),
        ('upd_t_first_indct_div.tsv', import_trademark_first_display),
        ('upd_mgt_info_t.tsv', import_trademark_management_info),
        ('upd_t_updt_art.tsv', import_trademark_updates),
        ('upd_prog_info_div_t.tsv', import_trademark_progress_info),
        ('upd_mrgn_t_rwrt_app_num.tsv', import_trademark_rewrite_applications),
        ('upd_trnsfr_rcpt_info_t.tsv', import_trademark_transfer_receipts),
        ('upd_snpn_zkn.tsv', import_trademark_appeal_cases),
        ('upd_snkt_bnri.tsv', import_trademark_decision_classifications),
        ('upd_ig_mustt.tsv', import_trademark_oppositions),
        ('upd_ig_ktti.tsv', import_trademark_opposition_decisions),
        ('upd_jiken_c_t_kian_dv.tsv', import_trademark_draft_records),
        ('upd_jiken_c_t_sinsei_dv.tsv', import_trademark_application_records),
        ('upd_jiken_c_t_yusenken_joho.tsv', import_trademark_priority_claims),
        ('upd_jiken_c_t_kohohako_joho.tsv', import_trademark_gazette_publications),
        ('upd_appl_reg_info.tsv', import_applicant_registration_info),
        ('upd_intl_t_org_org_reg_mgt_info.tsv', import_intl_trademark_registration),
        ('upd_intl_t_org_prog_info.tsv', import_intl_trademark_progress),
        ('upd_intl_t_org_set_crr_nm_addr.tsv', import_intl_trademark_holders),
        ('upd_intl_t_org_set_dsgn_gds_srvc.tsv', import_intl_trademark_goods_services),
        ('upd_intl_t_org_set_frst_indct.tsv', import_intl_trademark_first_indication),
        ('upd_design_state_gvrnmnt_mstr_mk.tsv', import_design_state_gvrnmnt_mstr_mk),
        ('upd_design_state_gvrnmnt_mstr_pri.tsv', import_design_state_gvrnmnt_mstr_pri),
        ('upd_t_sample.tsv', import_trademark_images),
        ('upd_sec_art.tsv', import_bougo_hyosho_articles),
        ('upd_sec_goods_name.tsv', import_bougo_shohin_mei),
        ('upd_sec_updt_art.tsv', import_bougo_koshin_kiji),
        ('upd_t_add_info.tsv', import_shohyo_fuka_joho),
    ]
    
    total_files = len(import_mappings)
    for index, (tsv_filename, import_func) in enumerate(import_mappings, 1):
        tsv_path = TSV_DIR / tsv_filename
        print(f"\n[{index}/{total_files}] Processing {tsv_filename}...")
        if tsv_path.exists():
            try:
                start_time = datetime.now()
                import_func(conn, tsv_path)
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"  Completed in {elapsed:.2f} seconds")
            except Exception as e:
                print(f"  Error importing {tsv_filename}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  Warning: {tsv_filename} not found, skipping...")

def main():
    print(f"Starting TMCloud import at {datetime.now()}")
    
    # シンプルなアプローチで新しいデータベースを作成
    import os
    
    # タイムスタンプ付きの新しいデータベース名を使用
    db_name = f"tmcloud_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"Creating new database: {db_name}")
    
    # 1. データベース作成
    try:
        conn = sqlite3.connect(db_name)
        print("Database connection established.")
        # パフォーマンス向上のための設定
        conn.execute("PRAGMA synchronous = OFF")
        conn.execute("PRAGMA journal_mode = MEMORY")
        conn.execute("PRAGMA cache_size = 10000")
    except sqlite3.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return
    
    # 2. テーブル作成（完全なスキーマ読み込み）
    print("Creating database schema...")
    try:
        with open('tmcloud_schema_v2.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
    except Exception as e:
        print(f"Error creating schema: {e}")
        conn.close()
        return
    
    # 3. TSVファイルをインポート
    print("Importing TSV files...")
    try:
        import_all_tables(conn)
    except Exception as e:
        print(f"Error during import: {e}")
        conn.close()
        return
    
    # 4. 完了
    conn.close()
    print(f"Import completed at {datetime.now()}")
    print("完了！")

if __name__ == "__main__":
    main()