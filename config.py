"""
TMCloud Configuration
環境変数でテスト/本番を切り替え可能
"""

import os
from pathlib import Path

# データベースパス
DB_PATH = os.environ.get('TMCLOUD_DB_PATH', 'output.db')

# 画像ディレクトリパス
IMAGE_PATH = os.environ.get('TMCLOUD_IMAGE_PATH', 'images/final_complete')

# テストモードかどうか
IS_TEST_MODE = 'TMCLOUD_DB_PATH' in os.environ

# CIモードかどうか
IS_CI_MODE = os.environ.get('CI', 'false').lower() == 'true'

# その他の設定
CONFIG = {
    'database': {
        'path': DB_PATH,
        'timeout': 30,
        'check_same_thread': False
    },
    'images': {
        'path': IMAGE_PATH,
        'allowed_extensions': ['.jpg', '.jpeg', '.png']
    },
    'search': {
        'max_results': 1000 if IS_TEST_MODE else 10000,
        'timeout': 5 if IS_TEST_MODE else 30
    },
    'performance': {
        'slow_query_threshold': 0.1 if IS_CI_MODE else 1.0  # 秒
    }
}

def get_db_path():
    """データベースパスを取得"""
    return Path(CONFIG['database']['path'])

def get_image_dir():
    """画像ディレクトリパスを取得"""
    return Path(CONFIG['images']['path'])

def is_test_mode():
    """テストモードかどうか"""
    return IS_TEST_MODE

def is_ci_mode():
    """CIモードかどうか"""
    return IS_CI_MODE