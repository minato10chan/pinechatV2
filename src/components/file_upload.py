import streamlit as st
from src.utils.text_processing import process_text_file
from src.services.pinecone_service import PineconeService
from src.config.settings import METADATA_CATEGORIES
from datetime import datetime
import pandas as pd
import json
import traceback
import io

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

def process_csv_file(file):
    """CSVファイルを処理してチャンクに分割"""
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(file)
        
        # 各列を結合してテキストを作成
        chunks = []
        for _, row in df.iterrows():
            # 各行をテキストに変換
            text = " ".join([str(val) for val in row.values if pd.notna(val)])
            if text.strip():
                chunks.append({
                    "text": text,
                    "metadata": {
                        "row_data": row.to_dict()
                    }
                })
        
        return chunks
    except Exception as e:
        raise ValueError(f"CSVファイルの処理に失敗しました: {str(e)}")

def render_file_upload(pinecone_service: PineconeService):
    """ファイルアップロード機能のUIを表示"""
    st.title("ファイルアップロード")
    st.write("テキストファイルをアップロードして、Pineconeデータベースに保存します。")
    
    uploaded_file = st.file_uploader("テキストファイルをアップロード", type=['txt', 'csv'])
    
    if uploaded_file is not None:
        # メタデータ入力フォーム
        st.subheader("メタデータ入力")
        
        # 大カテゴリの選択
        main_category = st.selectbox(
            "大カテゴリ *",
            METADATA_CATEGORIES["大カテゴリ"],
            index=None,
            placeholder="大カテゴリを選択してください"
        )
        
        # 中カテゴリの選択（大カテゴリに依存）
        if main_category:
            sub_category = st.selectbox(
                "中カテゴリ *",
                METADATA_CATEGORIES["中カテゴリ"][main_category],
                index=None,
                placeholder="中カテゴリを選択してください"
            )
        else:
            sub_category = None
        
        # 市区町村の選択
        city = st.selectbox(
            "市区町村 *",
            METADATA_CATEGORIES["市区町村"],
            index=None,
            placeholder="市区町村を選択してください"
        )
        
        # データ作成日の選択
        created_date = st.date_input(
            "データ作成日",
            value=None,
            format="YYYY/MM/DD"
        )
        
        # ソース元の入力
        source = st.text_input(
            "ソース元",
            placeholder="ソース元を入力してください（任意）"
        )
        
        # アップロード日（自動設定）
        upload_date = datetime.now()
        
        if st.button("データベースに保存"):
            # 必須項目のチェック
            if not all([main_category, sub_category, city]):
                st.error("大カテゴリ、中カテゴリ、市区町村は必須項目です。")
                return
                
            try:
                with st.spinner("ファイルを処理中..."):
                    # ファイルの種類に応じて処理を分岐
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    if file_extension == 'csv':
                        chunks = process_csv_file(uploaded_file)
                    else:
                        file_content = read_file_content(uploaded_file)
                        chunks = process_text_file(file_content, uploaded_file.name)
                    
                    st.write(f"ファイルを{len(chunks)}個のチャンクに分割しました")
                    
                    # メタデータを追加
                    for chunk in chunks:
                        chunk["metadata"] = {
                            "main_category": main_category,
                            "sub_category": sub_category,
                            "city": city,
                            "created_date": created_date.isoformat() if created_date else None,
                            "upload_date": upload_date.isoformat(),
                            "source": source if source else None
                        }
                        chunk["filename"] = uploaded_file.name
                        chunk["chunk_id"] = chunk["id"]
                    
                    with st.spinner("Pineconeにアップロード中..."):
                        pinecone_service.upload_chunks(chunks)
                        st.success("アップロードが完了しました！")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}") 