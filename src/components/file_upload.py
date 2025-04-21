import streamlit as st
from src.utils.text_processing import process_text_file
from src.services.pinecone_service import PineconeService
from src.config.settings import METADATA_CATEGORIES
from datetime import datetime
import pandas as pd
import json
import traceback

def read_file_content(file) -> str:
    """ファイルの内容を適切なエンコーディングで読み込む"""
    encodings = ['utf-8', 'shift-jis', 'cp932', 'euc-jp']
    content = file.getvalue()
    
    for encoding in encodings:
        try:
            # バイト列を文字列にデコード
            decoded_content = content.decode(encoding)
            # デコードした文字列を再度エンコードして元のバイト列と比較
            if decoded_content.encode(encoding) == content:
                return decoded_content
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    
    # すべてのエンコーディングで失敗した場合
    try:
        # UTF-8で強制的にデコードを試みる（一部の文字が化ける可能性あり）
        return content.decode('utf-8', errors='replace')
    except Exception as e:
        raise ValueError(f"ファイルのエンコーディングを特定できませんでした。エラー: {str(e)}")

def render_file_upload(pinecone_service: PineconeService):
    """ファイルアップロード機能のUIを表示"""
    st.title("📄 ファイルアップロード")
    
    with st.form("file_upload_form"):
        st.markdown("### ファイル情報の入力")
        
        # ファイルのアップロード
        uploaded_file = st.file_uploader(
            "ファイルを選択",
            type=["txt", "pdf", "doc", "docx"],
            help="アップロードするファイルを選択してください"
        )
        
        # ファイル名の入力
        filename = st.text_input(
            "ファイル名",
            help="ファイルの名前を入力してください（拡張子なし）"
        )
        
        # 大カテゴリの選択
        main_category = st.selectbox(
            "大カテゴリ",
            ["法令", "条例", "要綱", "その他"],
            help="ファイルの大カテゴリを選択してください"
        )
        
        # 中カテゴリの選択（複数選択可能）
        sub_categories = st.multiselect(
            "中カテゴリ",
            ["建築", "都市計画", "景観", "環境", "防災", "その他"],
            help="ファイルの中カテゴリを選択してください（複数選択可）"
        )
        
        # 市区町村の選択
        city = st.selectbox(
            "市区町村",
            ["川越市", "さいたま市", "その他"],
            help="ファイルに関連する市区町村を選択してください"
        )
        
        # アップロードボタン
        submit_button = st.form_submit_button("アップロード")
        
        if submit_button:
            try:
                # 必須項目のチェック
                if not all([uploaded_file, filename, main_category, sub_categories, city]):
                    st.error("❌ 必須項目（ファイル、ファイル名、大カテゴリ、中カテゴリ、市区町村）を入力してください")
                    return
                
                # ファイルの処理
                chunks = process_text_file(uploaded_file)
                
                # メタデータの追加
                for chunk in chunks:
                    chunk["metadata"] = {
                        "filename": filename,
                        "main_category": main_category,
                        "sub_categories": sub_categories,  # 複数のカテゴリをリストとして保存
                        "city": city,
                        "created_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "upload_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "source": "file_upload"
                    }
                
                # Pineconeへのアップロード
                pinecone_service.upload_chunks(chunks)
                
                st.success("✅ ファイルをアップロードしました")
                
            except Exception as e:
                st.error(f"❌ アップロードに失敗しました: {str(e)}")
                st.error(f"🔍 エラーの詳細: {type(e).__name__}")
                st.error(f"📜 スタックトレース:\n{traceback.format_exc()}") 