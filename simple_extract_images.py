#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import base64
import imghdr
import re
from pathlib import Path

# 設定
ROOT = Path("C:/Users/ygenk/Desktop/tsv_matome")
TSV_FILE = ROOT / "tsv" / "upd_t_sample.tsv"
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)

# 統計用カウンター
stats = {
    'total_rows': 0,
    'skipped_empty': 0,
    'skipped_standard_char': 0,
    'skipped_invalid_base64': 0,
    'skipped_small_size': 0,
    'skipped_unknown_format': 0,
    'saved_successfully': 0,
    'fixed_images': 0,
    'unknown_saved': 0,
    'errors': 0
}

def clean_base64_data(b64_data: str) -> str:
    """Base64データのクリーニング"""
    if not b64_data:
        return ""
    
    b64_data = b64_data.strip()
    
    # データURLプレフィックスがある場合は除去
    if ',' in b64_data and b64_data.startswith('data:'):
        b64_data = b64_data.split(',', 1)[1]
    
    # 改行と空白のみ除去
    b64_data = re.sub(r'[\r\n\s]+', '', b64_data)
    
    # Base64パディングの修正
    missing_padding = len(b64_data) % 4
    if missing_padding:
        b64_data += '=' * (4 - missing_padding)
    
    return b64_data

def detect_image_format(img_bytes: bytes) -> str:
    """画像形式を検出（不明な場合も含む）"""
    if len(img_bytes) < 8:
        return None
    
    # imghdirを使用
    try:
        format_type = imghdr.what(None, img_bytes)
        if format_type:
            return format_type
    except:
        pass
    
    # マジックナンバーによる判定
    if img_bytes.startswith(b'\xFF\xD8\xFF'):
        return 'jpeg'
    elif img_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    elif img_bytes.startswith(b'GIF87a') or img_bytes.startswith(b'GIF89a'):
        return 'gif'
    elif img_bytes.startswith(b'RIFF') and len(img_bytes) >= 12 and b'WEBP' in img_bytes[8:12]:
        return 'webp'
    elif img_bytes.startswith(b'BM'):
        return 'bmp'
    
    # 不明フォーマットでも保存を試行
    return 'unknown'

def try_fix_image(img_bytes: bytes, img_format: str) -> bytes:
    """画像の簡単な修復を試行"""
    try:
        if img_format == 'jpeg':
            # JPEGのEOIマーカーをチェック・追加
            if not img_bytes.endswith(b'\xFF\xD9'):
                stats['fixed_images'] += 1
                return img_bytes + b'\xFF\xD9'
        elif img_format == 'png':
            # PNGのIENDチャンクをチェック・追加
            if not img_bytes.endswith(b'IEND\xae\x42\x60\x82'):
                stats['fixed_images'] += 1
                return img_bytes + b'\x00\x00\x00\x00IEND\xae\x42\x60\x82'
        elif img_format == 'gif':
            # GIFのターミネーターをチェック・追加
            if not img_bytes.endswith(b'\x3B'):
                stats['fixed_images'] += 1
                return img_bytes + b'\x3B'
    except:
        pass
    
    return img_bytes

def try_find_embedded_image(img_bytes: bytes) -> tuple:
    """バイナリ内に埋め込まれた画像を検索"""
    if len(img_bytes) < 100:
        return None, None
    
    # 最初の200バイト内で画像ヘッダーを検索
    search_range = min(200, len(img_bytes) - 10)
    
    for i in range(search_range):
        remaining = img_bytes[i:]
        if len(remaining) < 10:
            continue
            
        # JPEG
        if remaining.startswith(b'\xFF\xD8\xFF'):
            return 'jpeg', remaining
        # PNG
        elif remaining.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png', remaining
        # GIF
        elif remaining.startswith(b'GIF87a') or remaining.startswith(b'GIF89a'):
            return 'gif', remaining
    
    return None, None

def normalize_app_num(app_num: str) -> str:
    """出願番号の正規化"""
    if not app_num:
        return ""
    return app_num.replace("-", "").strip()

def is_standard_character_mark(b64_data: str) -> bool:
    """標準文字かどうかの判定"""
    if not b64_data:
        return True
    
    b64_data = b64_data.strip()
    
    # 基本的な標準文字判定
    if (b64_data.startswith("//") or 
        set(b64_data) == {"/"} or 
        b64_data == "" or 
        b64_data.lower() in ["nan", "null", "none"] or 
        len(b64_data) < 20):
        return True
    
    # スラッシュが80%以上の場合も標準文字
    if len(b64_data) > 0 and b64_data.count("/") / len(b64_data) > 0.8:
        return True
    
    return False

def save_image(app_num: str, img_bytes: bytes, img_format: str, is_unknown: bool = False) -> bool:
    """画像ファイルを保存"""
    try:
        normalized_app_num = normalize_app_num(app_num)
        
        extension_map = {
            'jpeg': 'jpg',
            'png': 'png', 
            'gif': 'gif',
            'webp': 'webp',
            'bmp': 'bmp',
            'unknown': 'bin'  # 不明フォーマットは.binで保存
        }
        
        extension = extension_map.get(img_format, 'bin')
        
        # 不明フォーマットの場合は別のフォルダに保存
        if is_unknown:
            unknown_dir = IMG_DIR / "unknown"
            unknown_dir.mkdir(exist_ok=True)
            out_path = unknown_dir / f"{normalized_app_num}.{extension}"
        else:
            out_path = IMG_DIR / f"{normalized_app_num}.{extension}"
        
        with open(out_path, "wb") as f:
            f.write(img_bytes)
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to save {app_num}: {e}")
        return False

def process_images():
    """メイン処理"""
    print(f"📁 Reading TSV file: {TSV_FILE}")
    print(f"💾 Output directory: {IMG_DIR}")
    print("-" * 60)
    
    try:
        # TSVファイル読み込み
        df = pd.read_csv(TSV_FILE, sep="\t", encoding="cp932", dtype=str)
        print(f"✓ Successfully read file")
        
        stats['total_rows'] = len(df)
        print(f"📊 Total rows: {stats['total_rows']}")
        
        # 画像抽出処理
        success_count = 0
        
        for idx, row in df.iterrows():
            if idx % 1000 == 0:
                print(f"📈 Processing row {idx:,} / {len(df):,} (Success: {success_count})")
            
            app_num = str(row.get("app_num", "")).strip()
            b64_data = str(row.get("image_data", "")).strip()
            
            # 空データのスキップ
            if not app_num or not b64_data or b64_data == 'nan':
                stats['skipped_empty'] += 1
                continue
            
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
                
                # 既知のフォーマットの場合
                if img_format in ['jpeg', 'png', 'gif', 'webp', 'bmp']:
                    # 修復を試行
                    final_bytes = try_fix_image(img_bytes, img_format)
                    
                    if save_image(app_num, final_bytes, img_format):
                        stats['saved_successfully'] += 1
                        success_count += 1
                        if idx % 500 == 0:
                            print(f"✓ {app_num}.{img_format} ({len(final_bytes):,} bytes)")
                    else:
                        stats['errors'] += 1
                
                # 不明フォーマットの場合
                elif img_format == 'unknown':
                    # 埋め込まれた画像を検索
                    found_format, found_bytes = try_find_embedded_image(img_bytes)
                    
                    if found_format and found_bytes:
                        # 埋め込まれた画像が見つかった
                        fixed_bytes = try_fix_image(found_bytes, found_format)
                        if save_image(app_num, fixed_bytes, found_format):
                            stats['saved_successfully'] += 1
                            success_count += 1
                            if idx % 500 == 0:
                                print(f"🔍 {app_num}.{found_format} (embedded, {len(fixed_bytes):,} bytes)")
                    else:
                        # 不明フォーマットとして保存
                        if save_image(app_num, img_bytes, 'unknown', is_unknown=True):
                            stats['unknown_saved'] += 1
                            success_count += 1
                            if idx % 1000 == 0:
                                print(f"❓ {app_num}.bin (unknown format, {len(img_bytes):,} bytes)")
                
                else:
                    stats['skipped_unknown_format'] += 1
                    
            except Exception as e:
                stats['skipped_invalid_base64'] += 1
                if idx % 1000 == 0:
                    print(f"⚠️  Error for {app_num}: {str(e)[:50]}")
                continue
    
    except Exception as e:
        print(f"❌ Error reading TSV file: {e}")
        return
    
    # 統計情報の表示
    print("\n" + "=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total rows processed:      {stats['total_rows']:,}")
    print(f"Successfully saved:        {stats['saved_successfully']:,}")
    print(f"Unknown format saved:      {stats['unknown_saved']:,}")
    print(f"Fixed images:              {stats['fixed_images']:,}")
    print(f"Skipped (empty data):      {stats['skipped_empty']:,}")
    print(f"Skipped (standard char):   {stats['skipped_standard_char']:,}")
    print(f"Skipped (invalid base64):  {stats['skipped_invalid_base64']:,}")
    print(f"Skipped (too small):       {stats['skipped_small_size']:,}")
    print(f"Skipped (unknown format):  {stats['skipped_unknown_format']:,}")
    print(f"Errors:                    {stats['errors']:,}")
    
    total_saved = stats['saved_successfully'] + stats['unknown_saved']
    success_rate = (total_saved / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
    print(f"\n✨ Total success rate: {success_rate:.1f}%")
    print(f"📊 Known formats: {stats['saved_successfully']:,}")
    print(f"❓ Unknown formats: {stats['unknown_saved']:,}")
    
    if total_saved > 0:
        print(f"✅ Images saved to: {IMG_DIR}")
        print(f"❓ Unknown formats saved to: {IMG_DIR}/unknown")
        print(f"🔧 Images repaired: {stats['fixed_images']}")

if __name__ == "__main__":
    process_images()