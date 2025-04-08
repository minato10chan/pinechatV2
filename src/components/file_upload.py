import streamlit as st
from src.utils.text_processing import process_text_file
from src.services.pinecone_service import PineconeService
from src.config.settings import METADATA_CATEGORIES
from datetime import datetime

def read_file_content(file) -> str:
    """ファイルの内容を適切なエンコーディングで読み込む"""
    encodings = ['utf-8', 'shift-jis', 'cp932', 'euc-jp']
    content = file.getvalue()
    
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    
    raise ValueError("ファイルのエンコーディングを特定できませんでした。UTF-8、Shift-JIS、CP932、EUC-JPのいずれかで保存されているファイルをアップロードしてください。")

def render_file_upload(pinecone_service: PineconeService):
    """ファイルアップロード機能のUIを表示"""
    st.title("ファイルアップロード")
    st.write("テキストファイルをアップロードして、Pineconeデータベースに保存します。")
    
    uploaded_file = st.file_uploader("テキストファイルをアップロード", type=['txt'])
    
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
                    file_content = read_file_content(uploaded_file)
                    chunks = process_text_file(file_content, uploaded_file.name)
                    st.write(f"ファイルを{len(chunks)}個のチャンクに分割しました")
                    
                    # メタデータを追加
                    for chunk in chunks:
                        chunk["metadata"] = {
                            **chunk.get("metadata", {}),
                            "main_category": main_category,
                            "sub_category": sub_category,
                            "city": city,
                            "created_date": created_date.isoformat() if created_date else None,
                            "upload_date": upload_date.isoformat(),
                            "source": source if source else None
                        }
                    
                    with st.spinner("Pineconeにアップロード中..."):
                        pinecone_service.upload_chunks(chunks)
                        st.success("アップロードが完了しました！")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"エラーが発生しました: {str(e)}") 