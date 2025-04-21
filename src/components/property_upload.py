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
    city = st.text_input("所在地", placeholder="都道府県・市区町村を入力してください")
    layout = st.selectbox(
        "間取り",
        ["1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3K", "3DK", "3LDK", "4K以上", "その他"]
    )
    price = st.number_input("価格（万円）", min_value=0, step=100)
    
    # アップロードボタン
    if st.button("アップロード"):
        if not all([property_name, property_type, city, layout, price]):
            st.warning("すべての項目を入力してください。")
            return
        
        try:
            # 物件情報の構造化
            property_data = {
                "property_name": property_name,
                "property_type": property_type,
                "city": city,
                "layout": layout,
                "price": f"{price}万円"
            }
            
            # テキストチャンクの作成
            text = f"{property_name}は{property_type}です。{city}に位置し、間取りは{layout}、価格は{price}万円です。"
            chunks = [{
                "text": text,
                "metadata": property_data
            }]
            
            # Pineconeへのアップロード（property namespaceを使用）
            with st.spinner("アップロード中..."):
                pinecone_service.upload_chunks(chunks, namespace="property")
                st.success("物件情報のアップロードが完了しました。")
                
        except Exception as e:
            st.error(f"アップロード中にエラーが発生しました: {str(e)}") 