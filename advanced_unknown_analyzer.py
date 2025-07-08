#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from collections import Counter
import struct

# PIL のインポートをオプションにする
try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("✓ PIL available - Full analysis enabled")
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - Limited analysis")

# 設定
ROOT = Path("C:/Users/ygenk/Desktop/tsv_matome")
UNKNOWN_DIR = ROOT / "images" / "unknown"
CONVERTED_DIR = ROOT / "images" / "converted"
SAMPLE_DIR = ROOT / "images" / "samples"  # サンプル保存用
CONVERTED_DIR.mkdir(exist_ok=True)
SAMPLE_DIR.mkdir(exist_ok=True)

def detailed_header_analysis(file_path: Path) -> dict:
    """詳細なヘッダー分析"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        file_size = len(data)
        if file_size < 16:
            return {"type": "too_small"}
        
        # 複数の解釈を試行
        analysis = {
            "file_size": file_size,
            "hex_header": data[:32].hex(),
            "interpretations": []
        }
        
        # 解釈1: 最初の8バイトが幅・高さ（リトルエンディアン）
        try:
            width_le = struct.unpack('<I', data[0:4])[0]
            height_le = struct.unpack('<I', data[4:8])[0]
            if 1 <= width_le <= 8192 and 1 <= height_le <= 8192:
                analysis["interpretations"].append({
                    "type": "bitmap_le",
                    "width": width_le,
                    "height": height_le,
                    "expected_size_rgb": width_le * height_le * 3,
                    "expected_size_rgba": width_le * height_le * 4,
                    "expected_size_gray": width_le * height_le
                })
        except:
            pass
        
        # 解釈2: 最初の8バイトが幅・高さ（ビッグエンディアン）
        try:
            width_be = struct.unpack('>I', data[0:4])[0]
            height_be = struct.unpack('>I', data[4:8])[0]
            if 1 <= width_be <= 8192 and 1 <= height_be <= 8192:
                analysis["interpretations"].append({
                    "type": "bitmap_be",
                    "width": width_be,
                    "height": height_be,
                    "expected_size_rgb": width_be * height_be * 3,
                    "expected_size_rgba": width_be * height_be * 4,
                    "expected_size_gray": width_be * height_be
                })
        except:
            pass
        
        # 解釈3: オフセット付きの幅・高さ
        for offset in [8, 12, 16, 20, 24, 32, 40, 48]:
            if offset + 8 <= len(data):
                try:
                    width = struct.unpack('<I', data[offset:offset+4])[0]
                    height = struct.unpack('<I', data[offset+4:offset+8])[0]
                    if 1 <= width <= 8192 and 1 <= height <= 8192:
                        analysis["interpretations"].append({
                            "type": f"bitmap_offset_{offset}",
                            "width": width,
                            "height": height,
                            "offset": offset,
                            "expected_size_rgb": width * height * 3,
                            "expected_size_rgba": width * height * 4,
                            "expected_size_gray": width * height
                        })
                except:
                    pass
        
        # 解釈4: 16ビット値として解釈
        try:
            width_16 = struct.unpack('<H', data[0:2])[0]
            height_16 = struct.unpack('<H', data[2:4])[0]
            if 1 <= width_16 <= 2048 and 1 <= height_16 <= 2048:
                analysis["interpretations"].append({
                    "type": "bitmap_16bit",
                    "width": width_16,
                    "height": height_16,
                    "expected_size_rgb": width_16 * height_16 * 3,
                    "expected_size_rgba": width_16 * height_16 * 4,
                    "expected_size_gray": width_16 * height_16
                })
        except:
            pass
        
        return analysis
        
    except Exception as e:
        return {"type": "error", "error": str(e)}

def try_convert_with_interpretation(file_path: Path, interpretation: dict) -> bool:
    """特定の解釈で変換を試行"""
    if not PIL_AVAILABLE:
        return False
    
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        width = interpretation["width"]
        height = interpretation["height"]
        offset = interpretation.get("offset", 0)
        
        # データのオフセットを適用
        if offset > 0:
            # ヘッダー情報をスキップ
            pixel_data = data[offset + 8:]  # 幅・高さの8バイト後から
        else:
            pixel_data = data[8:]  # 最初の8バイト（幅・高さ）をスキップ
        
        conversions_attempted = []
        
        # RGB24として試行
        expected_rgb = width * height * 3
        if len(pixel_data) >= expected_rgb:
            try:
                img = Image.frombytes('RGB', (width, height), pixel_data[:expected_rgb])
                # 画像が真っ黒や真っ白でないかチェック
                extrema = img.getextrema()
                if isinstance(extrema[0], tuple):  # RGB
                    total_range = sum(max_val - min_val for min_val, max_val in extrema)
                else:  # グレースケール
                    total_range = extrema[1] - extrema[0]
                
                if total_range > 10:  # ある程度のバリエーションがある
                    output_path = CONVERTED_DIR / f"{file_path.stem}_{interpretation['type']}_rgb_{width}x{height}.png"
                    img.save(output_path)
                    print(f"✓ RGB conversion: {output_path.name}")
                    return True
            except Exception as e:
                conversions_attempted.append(f"RGB failed: {str(e)[:30]}")
        
        # RGBA32として試行
        expected_rgba = width * height * 4
        if len(pixel_data) >= expected_rgba:
            try:
                img = Image.frombytes('RGBA', (width, height), pixel_data[:expected_rgba])
                extrema = img.getextrema()
                if isinstance(extrema[0], tuple):
                    total_range = sum(max_val - min_val for min_val, max_val in extrema[:3])  # RGBのみ
                else:
                    total_range = extrema[1] - extrema[0]
                
                if total_range > 10:
                    output_path = CONVERTED_DIR / f"{file_path.stem}_{interpretation['type']}_rgba_{width}x{height}.png"
                    img.save(output_path)
                    print(f"✓ RGBA conversion: {output_path.name}")
                    return True
            except Exception as e:
                conversions_attempted.append(f"RGBA failed: {str(e)[:30]}")
        
        # グレースケールとして試行
        expected_gray = width * height
        if len(pixel_data) >= expected_gray:
            try:
                img = Image.frombytes('L', (width, height), pixel_data[:expected_gray])
                extrema = img.getextrema()
                total_range = extrema[1] - extrema[0] if isinstance(extrema, tuple) else 0
                
                if total_range > 10:
                    output_path = CONVERTED_DIR / f"{file_path.stem}_{interpretation['type']}_gray_{width}x{height}.png"
                    img.save(output_path)
                    print(f"✓ Grayscale conversion: {output_path.name}")
                    return True
            except Exception as e:
                conversions_attempted.append(f"Gray failed: {str(e)[:30]}")
        
        # デバッグ情報
        if len(conversions_attempted) > 0:
            print(f"⚠️  All conversions failed for {file_path.name}: {'; '.join(conversions_attempted)}")
        
    except Exception as e:
        print(f"✗ Error in conversion: {e}")
    
    return False

def extract_most_common_patterns():
    """最も一般的なパターンのサンプルを抽出"""
    print("\n🎯 Extracting samples of most common patterns...")
    
    if not UNKNOWN_DIR.exists():
        return
    
    bin_files = list(UNKNOWN_DIR.glob("*.bin"))
    header_patterns = Counter()
    
    # ヘッダーパターンをカウント
    for file_path in bin_files:
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)
            if len(header) >= 8:
                pattern = header.hex()
                header_patterns[pattern] += 1
        except:
            continue
    
    # 上位パターンのサンプルを保存
    for pattern, count in header_patterns.most_common(5):
        if count >= 2:  # 2個以上ある場合のみ
            print(f"\n📋 Pattern {pattern}: {count} files")
            samples_saved = 0
            for file_path in bin_files:
                if samples_saved >= 3:  # 各パターン最大3サンプル
                    break
                try:
                    with open(file_path, "rb") as f:
                        header = f.read(8)
                    if header.hex() == pattern:
                        # サンプルとして最初の1KBを保存
                        sample_path = SAMPLE_DIR / f"pattern_{pattern}_{samples_saved+1}_{file_path.name}"
                        with open(file_path, "rb") as src, open(sample_path, "wb") as dst:
                            dst.write(src.read(1024))  # 最初の1KB
                        print(f"  💾 Saved sample: {sample_path.name}")
                        samples_saved += 1
                except:
                    continue

def comprehensive_analysis():
    """包括的な分析"""
    print(f"🔍 Advanced analysis of unknown format files")
    print(f"📁 Source: {UNKNOWN_DIR}")
    print(f"💾 Converted: {CONVERTED_DIR}")
    print(f"📋 Samples: {SAMPLE_DIR}")
    print("-" * 70)
    
    if not UNKNOWN_DIR.exists():
        print(f"❌ Unknown directory not found: {UNKNOWN_DIR}")
        return
    
    bin_files = list(UNKNOWN_DIR.glob("*.bin"))
    print(f"📊 Found {len(bin_files)} unknown format files")
    
    if len(bin_files) == 0:
        return
    
    # 統計情報
    total_interpretations = 0
    successful_conversions = 0
    header_patterns = Counter()
    size_analysis = {"<1KB": 0, "1-5KB": 0, "5-20KB": 0, ">20KB": 0}
    
    print("\n🔬 Performing detailed analysis...")
    
    # 詳細分析（最初の500ファイルのみ - 処理時間短縮）
    analysis_files = bin_files[:500] if len(bin_files) > 500 else bin_files
    print(f"📊 Analyzing {len(analysis_files)} files for detailed interpretation...")
    
    for i, file_path in enumerate(analysis_files):
        if i % 50 == 0:
            print(f"📈 Progress: {i} / {len(analysis_files)} (Converted: {successful_conversions})")
        
        # ファイルサイズ分析
        file_size = file_path.stat().st_size
        if file_size < 1024:
            size_analysis["<1KB"] += 1
        elif file_size < 5120:
            size_analysis["1-5KB"] += 1
        elif file_size < 20480:
            size_analysis["5-20KB"] += 1
        else:
            size_analysis[">20KB"] += 1
        
        # ヘッダーパターン分析
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)
            pattern = header.hex()
            header_patterns[pattern] += 1
        except:
            continue
        
        # 詳細な解釈分析
        analysis = detailed_header_analysis(file_path)
        
        if "interpretations" in analysis:
            total_interpretations += len(analysis["interpretations"])
            
            # 各解釈で変換を試行
            for interpretation in analysis["interpretations"]:
                if try_convert_with_interpretation(file_path, interpretation):
                    successful_conversions += 1
                    break  # 一つでも成功したら次のファイルへ
    
    # パターンサンプルの抽出
    extract_most_common_patterns()
    
    # 結果表示
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE ANALYSIS RESULTS")
    print("=" * 70)
    
    print(f"📁 Files analyzed: {len(analysis_files):,}")
    print(f"🔍 Total interpretations found: {total_interpretations:,}")
    print(f"✅ Successful conversions: {successful_conversions:,}")
    
    conversion_rate = (successful_conversions / len(analysis_files)) * 100 if analysis_files else 0
    print(f"✨ Conversion success rate: {conversion_rate:.1f}%")
    
    print(f"\n📊 Top header patterns:")
    for pattern, count in header_patterns.most_common(10):
        percentage = (count / len(analysis_files)) * 100
        print(f"  {pattern}: {count:,} files ({percentage:.1f}%)")
    
    print(f"\n📏 File size analysis:")
    for size_range, count in size_analysis.items():
        percentage = (count / len(analysis_files)) * 100
        print(f"  {size_range}: {count:,} files ({percentage:.1f}%)")
    
    if successful_conversions > 0:
        print(f"\n✅ Successfully converted files saved to: {CONVERTED_DIR}")
        print("💡 Verify the converted images in an image viewer")
    
    print(f"\n📋 Pattern samples saved to: {SAMPLE_DIR}")
    print("💡 You can examine these samples with a hex editor")
    
    # 推奨事項
    remaining_files = len(bin_files) - successful_conversions
    if remaining_files > 0:
        print(f"\n💡 Recommendations for {remaining_files:,} remaining files:")
        print("   1. Check if they are a proprietary image format")
        print("   2. Try opening with specialized image viewers")
        print("   3. Contact the data provider for format specifications")
        print("   4. Consider that some may not be images at all")

if __name__ == "__main__":
    comprehensive_analysis()