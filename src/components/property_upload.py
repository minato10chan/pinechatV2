import streamlit as st
from src.services.pinecone_service import PineconeService
from src.utils.text_processing import process_text_file
from datetime import datetime
import json

def render_property_upload(pinecone_service: PineconeService):
    """物件情報アップロード機能のUIを表示"""
    st.title("物件情報アップロード")
    st.write("物件情報をアップロードします。")
    
    # 物件情報の入力フォーム
    property_name = st.text_input("物件名", placeholder="物件名を入力してください")
    property_type = st.selectbox(
        "物件種別",
        ["マンション", "アパート", "一戸建て", "土地", "その他"]
    )
    
    # 都道府県と市区町村を分けて入力
    col1, col2 = st.columns(2)
    with col1:
        prefecture = st.text_input("都道府県", placeholder="例：埼玉県")
    with col2:
        city = st.text_input("市区町村", placeholder="例：川越市")
    
    layout = st.selectbox(
        "間取り",
        ["1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3K", "3DK", "3LDK", "4K以上", "その他"]
    )
    
    # アップロードボタン
    if st.button("アップロード"):
        if not all([property_name, property_type, prefecture, city, layout]):
            st.warning("すべての項目を入力してください。")
            return
        
        try:
            # 物件情報の構造化
            property_data = {
                "property_name": property_name,
                "property_type": property_type,
                "prefecture": prefecture,
                "city": city,
                "layout": layout
            }
            
            # テキストチャンクの作成
            text = f"{property_name}は{property_type}です。{prefecture}{city}に位置し、間取りは{layout}です。"
            chunks = [{
                "id": f"property_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "text": text,
                "metadata": property_data
            }]
            
            # Pineconeへのアップロード（property namespaceを使用）
            with st.spinner("アップロード中..."):
                pinecone_service.upload_chunks(chunks, namespace="property")
                st.success("物件情報のアップロードが完了しました。")
                
        except Exception as e:
            st.error(f"アップロード中にエラーが発生しました: {str(e)}") 