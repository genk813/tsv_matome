#!/usr/bin/env python3
"""Debug trademark type search in complex search"""

from tmcloud_search_integrated import TMCloudIntegratedSearch
from pathlib import Path

def test_debug():
    db_path = Path(__file__).parent / "tmcloud_v2_20250818_081655.db"
    searcher = TMCloudIntegratedSearch(str(db_path))
    
    # Test search_by_trademark_type with unified_format=False
    print("Testing search_by_trademark_type with unified_format=False...")
    results = searcher.search_by_trademark_type('標準文字', limit=3, unified_format=False)
    print(f"Got {len(results)} results")
    
    if results:
        print("First result:")
        for key, value in results[0].items():
            print(f"  {key}: {value}")
    
    # Test search_complex
    print("\n" + "="*50)
    print("Testing search_complex...")
    conditions = [{'type': 'trademark_type', 'keyword': '標準文字'}]
    
    try:
        results = searcher.search_complex(conditions, operator='AND', limit=3, unified_format=True)
        print(f"Got {len(results)} results")
        
        if results:
            print("First result:")
            for key, value in results[0].items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug()