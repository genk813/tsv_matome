#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import base64
import imghdr
import re
from pathlib import Path
from collections import defaultdict

# 設定
ROOT = Path("C:/Users/ygenk/Desktop/tsv_matome")
TSV_FILE = ROOT / "tsv" / "upd_t_sample.tsv"
FINAL_DIR = ROOT / "images" / "final_complete"
FINAL_DIR.mkdir(exist_ok=True)

# 統計用カウンター
stats = {
    'total_rows': 0,
    'unique_app_nums': 0,
    'multirow_cases': 0,
    'skipped_empty': 0,
    'skipped_standard_char': 0,
    'skipped_invalid_base64': 0,
    'skipped_small_size': 0,
    'skipped_unknown_format': 0,
    'saved_successfully': 0,
    'fixed_images': 0,
    'recovered_unknown': 0,
    'errors': 0
}

def clean_base64_data(b64_data: str) -> str:
    """Base64データのクリーニング（より積極的）"""
    if not b64_data:
        return ""
    
    b64_data = b64_data.strip()
    
    # データURLプレフィックスがある場合は除去
    if ',' in b64_data and b64_data.startswith('data:'):
        b64_data = b64_data.split(',', 1)[1]
    
    # 改行、空白、タブを除去
    b64_data = re.sub(r'[\r\n\s\t]+', '', b64_data)
    
    # 無効なBase64文字を除去（より積極的）
    b64_data = re.sub(r'[^A-Za-z0-9+/=]', '', b64_data)
    
    # Base64パディングの修正
    missing_padding = len(b64_data) % 4
    if missing_padding:
        b64_data += '=' * (4 - missing_padding)
    
    return b64_data

def detect_image_format(img_bytes: bytes) -> str:
    """画像形式を検出（より詳細）"""
    if len(img_bytes) < 8:
        return None
    
    # imghdirを使用
    try:
        format_type = imghdr.what(None, img_bytes)
        if format_type:
            return format_type
    except:
        pass
    
    # マジックナンバーによる詳細判定
    if img_bytes.startswith(b'\xFF\xD8\xFF'):
        return 'jpeg'
    elif img_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif img_bytes.startswith(b'GIF87a') or img_bytes.startswith(b'GIF89a'):
        return 'gif'
    elif img_bytes.startswith(b'RIFF') and len(img_bytes) >= 12:
        if b'WEBP' in img_bytes[8:12]:
            return 'webp'
    elif img_bytes.startswith(b'BM'):
        return 'bmp'
    elif len(img_bytes) >= 12:
        # TIFF形式
        if img_bytes.startswith(b'II\x2A\x00') or img_bytes.startswith(b'MM\x00\x2A'):
            return 'tiff'
    
    return None

def try_fix_image(img_bytes: bytes, img_format: str) -> bytes:
    """画像の修復を試行（より積極的）"""
    try:
        if img_format == 'jpeg':
            # JPEGの場合、SOI確認とEOI追加
            if img_bytes.startswith(b'\xFF\xD8'):
                if not img_bytes.endswith(b'\xFF\xD9'):
                    stats['fixed_images'] += 1
                    return img_bytes + b'\xFF\xD9'
        elif img_format == 'png':
            # PNGの場合、IENDチャンク追加
            if not img_bytes.endswith(b'IEND\xae\x42\x60\x82'):
                stats['fixed_images'] += 1
                return img_bytes + b'\x00\x00\x00\x00IEND\xae\x42\x60\x82'
        elif img_format == 'gif':
            # GIFの場合、ターミネーター追加
            if not img_bytes.endswith(b'\x3B'):
                stats['fixed_images'] += 1
                return img_bytes + b'\x3B'
        elif img_format == 'webp':
            # WebPは通常修復不要だが、サイズチェック
            if len(img_bytes) >= 12:
                return img_bytes
        elif img_format == 'bmp':
            # BMPの場合、ヘッダーサイズ確認
            if len(img_bytes) >= 54:  # 最小BMPヘッダーサイズ
                return img_bytes
    except:
        pass
    
    return img_bytes

def try_recover_unknown_format(img_bytes: bytes) -> tuple:
    """不明フォーマットから画像復旧を試行"""
    if len(img_bytes) < 20:
        return None, None
    
    # パターン1: 先頭にゴミデータがある場合
    for offset in range(0, min(200, len(img_bytes) - 10)):
        remaining = img_bytes[offset:]
        
        # JPEG検索
        if remaining.startswith(b'\xFF\xD8\xFF'):
            stats['recovered_unknown'] += 1
            return 'jpeg', remaining
        # PNG検索
        elif remaining.startswith(b'\x89PNG\r\n\x1a\n'):
            stats['recovered_unknown'] += 1
            return 'png', remaining
        # GIF検索
        elif remaining.startswith(b'GIF87a') or remaining.startswith(b'GIF89a'):
            stats['recovered_unknown'] += 1
            return 'gif', remaining
        # BMP検索
        elif remaining.startswith(b'BM'):
            stats['recovered_unknown'] += 1
            return 'bmp', remaining
    
    return None, None

def normalize_app_num(app_num: str) -> str:
    """出願番号の正規化"""
    if not app_num:
        return ""
    return app_num.replace("-", "").strip()

def is_standard_character_mark(b64_data: str) -> bool:
    """標準文字かどうかの判定（より厳密）"""
    if not b64_data:
        return True
    
    b64_data = b64_data.strip()
    
    # 明確な標準文字パターン
    if (b64_data.startswith("//") or 
        set(b64_data.strip()) == {"/"} or 
        b64_data == "" or 
        b64_data.lower() in ["nan", "null", "none"] or 
        len(b64_data) < 20):
        return True
    
    # スラッシュが多すぎる場合
    if len(b64_data) > 0 and b64_data.count("/") / len(b64_data) > 0.8:
        return True
    
    # 標準文字を示す文字列を含む場合
    if "標準文字" in b64_data or "standard" in b64_data.lower():
        return True
    
    return False

def consolidate_multirow_data(df: pd.DataFrame) -> dict:
    """複数行にわたるimage_dataを統合（詳細版）"""
    print("🔄 Consolidating multi-row image data...")
    
    # app_numでグループ化（順序保持）
    grouped_data = defaultdict(list)
    
    for idx, row in df.iterrows():
        app_num = str(row.get("app_num", "")).strip()
        image_data = str(row.get("image_data", "")).strip()
        
        if app_num and image_data and image_data != 'nan':
            grouped_data[app_num].append(image_data)
    
    # 統合結果
    consolidated = {}
    multirow_count = 0
    max_rows = 0
    
    for app_num, image_data_list in grouped_data.items():
        if len(image_data_list) > 1:
            # 複数行の場合、連結
            consolidated_data = ''.join(image_data_list)
            consolidated[app_num] = consolidated_data
            multirow_count += 1
            max_rows = max(max_rows, len(image_data_list))
            
            if multirow_count <= 20:  # 最初の20件をログ出力
                print(f"📋 Multi-row: {app_num} ({len(image_data_list)} rows, {len(consolidated_data):,} chars)")
        else:
            # 単行の場合、そのまま
            consolidated[app_num] = image_data_list[0]
    
    stats['multirow_cases'] = multirow_count
    stats['unique_app_nums'] = len(consolidated)
    
    print(f"✓ Consolidated {multirow_count} multi-row cases")
    print(f"✓ Maximum rows per case: {max_rows}")
    print(f"✓ Total unique app_nums: {len(consolidated)}")
    
    return consolidated

def save_image(app_num: str, img_bytes: bytes, img_format: str) -> bool:
    """画像ファイルを保存"""
    try:
        normalized_app_num = normalize_app_num(app_num)
        
        extension_map = {
            'jpeg': 'jpg',
            'png': 'png', 
            'gif': 'gif',
            'webp': 'webp',
            'bmp': 'bmp',
            'tiff': 'tiff'
        }
        
        extension = extension_map.get(img_format, 'bin')
        out_path = FINAL_DIR / f"{normalized_app_num}.{extension}"
        
        with open(out_path, "wb") as f:
            f.write(img_bytes)
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to save {app_num}: {e}")
        return False

def process_final_extraction():
    """最終的な画像抽出処理"""
    print(f"📁 Reading TSV file: {TSV_FILE}")
    print(f"💾 Final output directory: {FINAL_DIR}")
    print("-" * 60)
    
    try:
        # TSVファイル読み込み
        df = pd.read_csv(TSV_FILE, sep="\t", encoding="cp932", dtype=str)
        print(f"✓ Successfully read file")
        
        stats['total_rows'] = len(df)
        print(f"📊 Total rows: {stats['total_rows']}")
        
        # 複数行データの統合
        consolidated = consolidate_multirow_data(df)
        
        print(f"\n🔬 Processing consolidated image data...")
        success_count = 0
        large_images = 0
        
        for i, (app_num, b64_data) in enumerate(consolidated.items()):
            if i % 500 == 0:
                print(f"📈 Processing {i:,} / {len(consolidated):,} (Success: {success_count}, Large: {large_images})")
            
            # 標準文字のスキップ
            if is_standard_character_mark(b64_data):
                stats['skipped_standard_char'] += 1
                continue
            
            # Base64データのクリーニング
            cleaned_b64 = clean_base64_data(b64_data)
            if not cleaned_b64:
                stats['skipped_empty'] += 1
                continue
            
            try:
                # Base64デコード
                img_bytes = base64.b64decode(cleaned_b64, validate=True)
                
                # サイズチェック
                if len(img_bytes) < 100:
                    stats['skipped_small_size'] += 1
                    continue
                
                # 画像形式検出
                img_format = detect_image_format(img_bytes)
                final_bytes = img_bytes
                
                # 不明フォーマットの場合、復旧を試行
                if not img_format:
                    recovered_format, recovered_bytes = try_recover_unknown_format(img_bytes)
                    if recovered_format and recovered_bytes:
                        img_format = recovered_format
                        final_bytes = recovered_bytes
                
                if img_format:
                    # 修復を試行
                    final_bytes = try_fix_image(final_bytes, img_format)
                    
                    if save_image(app_num, final_bytes, img_format):
                        stats['saved_successfully'] += 1
                        success_count += 1
                        
                        # 大きな画像をカウント
                        if len(final_bytes) > 50000:
                            large_images += 1
                        
                        if i % 500 == 0 or len(final_bytes) > 100000:
                            print(f"✓ {app_num}.{img_format} ({len(final_bytes):,} bytes)")
                    else:
                        stats['errors'] += 1
                else:
                    stats['skipped_unknown_format'] += 1
                    
            except Exception as e:
                stats['skipped_invalid_base64'] += 1
                continue
    
    except Exception as e:
        print(f"❌ Error reading TSV file: {e}")
        return
    
    # 統計情報の表示
    print("\n" + "=" * 60)
    print("📊 FINAL EXTRACTION RESULTS")
    print("=" * 60)
    print(f"Total rows in TSV:         {stats['total_rows']:,}")
    print(f"Unique app_nums:           {stats['unique_app_nums']:,}")
    print(f"Multi-row cases detected:  {stats['multirow_cases']:,}")
    print(f"Successfully saved:        {stats['saved_successfully']:,}")
    print(f"Large images (>50KB):      {large_images:,}")
    print(f"Fixed images:              {stats['fixed_images']:,}")
    print(f"Recovered from unknown:    {stats['recovered_unknown']:,}")
    print(f"Skipped (empty data):      {stats['skipped_empty']:,}")
    print(f"Skipped (standard char):   {stats['skipped_standard_char']:,}")
    print(f"Skipped (invalid base64):  {stats['skipped_invalid_base64']:,}")
    print(f"Skipped (too small):       {stats['skipped_small_size']:,}")
    print(f"Skipped (unknown format):  {stats['skipped_unknown_format']:,}")
    print(f"Errors:                    {stats['errors']:,}")
    
    success_rate = (stats['saved_successfully'] / stats['unique_app_nums'] * 100) if stats['unique_app_nums'] > 0 else 0
    print(f"\n✨ Final success rate: {success_rate:.1f}%")
    
    # データ品質分析
    avg_per_multirow = stats['multirow_cases'] / max(1, stats['unique_app_nums'] - (stats['unique_app_nums'] - stats['multirow_cases']))
    print(f"📊 Average rows per multi-row case: {avg_per_multirow:.1f}")
    
    if stats['saved_successfully'] > 0:
        print(f"\n✅ Final images saved to: {FINAL_DIR}")
        print(f"🔧 Images repaired: {stats['fixed_images']}")
        print(f"🔄 Images recovered from unknown: {stats['recovered_unknown']}")
        print(f"📏 Large images (>50KB): {large_images:,}")
        
        print(f"\n🎉 MISSION ACCOMPLISHED!")
        print(f"   From fragmented TSV data → {stats['saved_successfully']:,} complete images")
        print(f"   Solved the multi-row puzzle! 🧩")

if __name__ == "__main__":
    process_final_extraction()