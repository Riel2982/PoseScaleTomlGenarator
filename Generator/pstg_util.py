import os
import shutil
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

def get_app_dir():
    """実行ファイルのディレクトリパスを取得"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable) # 実行ファイルのディレクトリ
    else:
        return os.path.dirname(os.path.abspath(__file__)) # 実行ファイルのディレクトリ

def get_temp_dir():
    """Tempディレクトリのパスを取得"""
    return os.path.join(get_app_dir(), 'Temp') # Tempディレクトリ

def setup_logging(output_log=False):
    """ロガーの初期化"""
    logger = logging.getLogger() # ロガー
    logger.setLevel(logging.DEBUG) # ログレベル

    if logger.hasHandlers(): # ハンドラーが設定されている場合
        logger.handlers.clear()

    console_formatter = logging.Formatter('%(levelname)s: %(message)s') # コンソールフォーマッター
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s') # ファイルフォーマッター

    console_handler = logging.StreamHandler() # コンソールハンドラー
    console_handler.setLevel(logging.INFO) # コンソールログレベル
    console_handler.setFormatter(console_formatter) # コンソールフォーマッター
    logger.addHandler(console_handler) # コンソールハンドラーを追加

    # ファイル出力
    if output_log:
        app_dir = get_app_dir() # 実行ファイルのディレクトリ
        log_dir = os.path.join(app_dir, 'logs') # ログディレクトリ
        os.makedirs(log_dir, exist_ok=True) # ログディレクトリを作成

        log_file = os.path.join(log_dir, 'PoseScaleTomlGenerator.log') # ログファイル
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024, # ログファイルサイズ
            backupCount=5, # バックアップファイル数
            encoding='utf-8' # エンコーディング
        ) # ログハンドラー
        file_handler.setLevel(logging.INFO) # ファイルログレベル
        file_handler.setFormatter(file_formatter) # ファイルフォーマッター
        logger.addHandler(file_handler) # ファイルハンドラーを追加

        debug_log_file = os.path.join(log_dir, 'debug_data.log') # デバッグログファイル
        debug_handler = RotatingFileHandler(
            debug_log_file,
            maxBytes=10 * 1024 * 1024, # デバッグログファイルサイズ
            backupCount=5, # バックアップファイル数
            encoding='utf-8' # エンコーディング
        ) # デバッグハンドラー
        debug_handler.setLevel(logging.DEBUG) # デバッグログレベル
        debug_handler.setFormatter(file_formatter) # デバッグフォーマッター
        debug_handler.addFilter(lambda record: record.levelno == logging.DEBUG) # デバッグフィルター
        logger.addHandler(debug_handler) # デバッグハンドラーを追加

def clean_temp_dir():
    """Tempディレクトリを削除"""
    temp_dir = get_temp_dir() # Tempディレクトリ
    if os.path.exists(temp_dir): # Tempディレクトリが存在する場合
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.info(f"Tempディレクトリを削除しました: {temp_dir}")
        except Exception as e:
            logging.warning(f"Tempディレクトリの削除に失敗しました (無視します): {e}")

def save_file_with_timestamp(file_path, data, overwrite=False):
    """タイムスタンプ付きでファイルを保存 (overwrite=Trueの場合は上書き)"""
    if os.path.exists(file_path) and not overwrite: # 既存のファイルが存在する場合
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S") # タイムスタンプ
        base, ext = os.path.splitext(file_path) # ファイル名と拡張子
        rename_path = f"{base}_{timestamp}{ext}" # リネーム後のファイル名
        try:
            os.rename(file_path, rename_path)
            logging.info(f"既存のファイルをリネームしました: {rename_path}")
            print(f"既存のファイルをリネームしました: {rename_path}")
        except OSError as e:
            logging.error(f"ファイルのリネームに失敗しました: {e}")
    elif os.path.exists(file_path) and overwrite: # 既存のファイルが存在する場合
        logging.info(f"既存のファイルを上書きします: {file_path}")
        print(f"既存のファイルを上書きします: {file_path}")

    try: # ファイルを保存
        with open(file_path, 'w', encoding='utf-8') as save_file:
            save_file.write(data)
        print(f'ファイルを保存しました {file_path}')
        logging.info(f'ファイルを保存しました {file_path}')
    except OSError as e: # ファイルの保存に失敗しました
        logging.error(f"ファイルの保存に失敗しました: {e}")

def load_chara_mapping():
    """キャラクター名のマッピング関数を返す"""
    setting_chara_mapping = {
        "MIKU": "MIK", "RIN": "RIN", "LEN": "LEN", "LUKA": "LUK",
        "NERU": "NER", "HAKU": "HAK", "KAITO": "KAI", "MEIKO": "MEI",
        "SAKINE": "SAK", "TETO": "TET"
    }

    toml_chara_mapping = {
        "MIKU": "0", "RIN": "1", "LEN": "2", "LUKA": "3",
        "NERU": "4", "HAKU": "5", "KAITO": "6", "MEIKO": "7",
        "SAKINE": "8", "TETO": "9"
    }

    # キャラクター名のマッピング関数
    def map_chara(chara, mapping_type="module_to_setting"):
        if mapping_type == "module_to_setting": # module_to_setting（モジュール名を設定名に変換）
            return setting_chara_mapping.get(chara, chara)
        elif mapping_type == "module_to_cos_scale": # module_to_cos_scale（モジュール名をCOS値に変換）
            return toml_chara_mapping.get(chara, chara)
        else:
            return chara

    return map_chara

def is_match(name, contains_str, exclude_str=None):
    """モジュール名がキーワードにマッチするか判定 (ORマッチ)"""
    if not contains_str: # contains_strが空の場合
        return False
        
    contains = contains_str.split(',') # contains_strをカンマ区切りで分割
    includes = [word.strip() for word in contains if word.strip() and not word.strip().startswith('|')] # includes（含むキーワード）
    
    # Legacy support: excludes starting with | in contains_str（contains_str内の|で始まる除外キーワードのサポート）
    legacy_excludes = [word.strip()[1:] for word in contains if word.strip().startswith('|')] # legacy_excludes（除外キーワード）
    
    explicit_excludes = [] # explicit_excludes（明示的除外キーワード）
    if exclude_str: # exclude_strが空の場合
        explicit_excludes = [word.strip() for word in exclude_str.split(',') if word.strip()] # explicit_excludes（明示的除外キーワード）
        
    excludes = legacy_excludes + explicit_excludes # excludes（除外キーワード）

    # 文字化け対策
    if '\ufffd' in includes:
        logging.warning(f"設定 {contains_str} に無効な文字が含まれているため、そのキーワードは無視します。")
        includes = [i for i in includes if i != '\ufffd']

    logging.debug(f"Checking Module: {name} against Includes: {includes}, Excludes: {excludes}")

    # Exclude check (if ANY exclude word is found, return False)（ANDマッチ）
    if any(exc in name for exc in excludes):
        return False

    # ORマッチで処理
    return any(inc in name for inc in includes)
