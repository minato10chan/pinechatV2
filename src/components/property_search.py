def render_property_search(pinecone_service: PineconeService):
    """物件情報検索機能のUIを表示"""
    st.title("物件情報検索")
    st.write("登録された物件情報を検索します。")
    
    # 検索クエリの入力
    search_query = st.text_input(
        "検索キーワード",
        placeholder="物件名、特徴、条件などを入力してください"
    )
    
    # 検索条件の指定
    st.subheader("検索条件")
    col1, col2 = st.columns(2)
    
    with col1:
        property_type = st.multiselect(
            "物件種別",
            ["マンション", "アパート", "一戸建て", "土地", "その他"]
        )
        
        city = st.text_input(
            "所在地",
            placeholder="都道府県・市区町村を入力してください"
        )
    
    with col2:
        layout = st.multiselect(
            "間取り",
            ["1K", "1DK", "1LDK", "2K", "2DK", "2LDK", "3K", "3DK", "3LDK", "4K以上", "その他"]
        )
        
        price_range = st.slider(
            "価格帯（万円）",
            min_value=0,
            max_value=10000,
            value=(0, 10000),
            step=100
        )
    
    # 検索ボタン
    if st.button("検索"):
        if not search_query:
            st.warning("検索キーワードを入力してください。")
            return
        
        try:
            # 検索条件の構築
            filter_conditions = {}
            if property_type:
                filter_conditions["property_type"] = {"$in": property_type}
            if city:
                filter_conditions["city"] = {"$regex": city}
            if layout:
                filter_conditions["layout"] = {"$in": layout}
            
            # Pineconeでの検索（property namespaceを使用）
            with st.spinner("検索中..."):
                results = pinecone_service.query(
                    query=search_query,
                    top_k=10,
                    filter_conditions=filter_conditions,
                    namespace="property"
                )
                
                if not results:
                    st.info("該当する物件情報が見つかりませんでした。")
                    return
                
                # 検索結果の表示
                st.subheader("検索結果")
                for result in results:
                    with st.expander(f"{result['metadata']['property_name']} - {result['metadata']['property_type']}"):
                        st.write(f"**所在地:** {result['metadata']['city']}")
                        st.write(f"**間取り:** {result['metadata']['layout']}")
                        st.write(f"**価格:** {result['metadata']['price']}")
                        st.write(f"**説明:** {result['text']}")
                        
        except Exception as e:
            st.error(f"検索中にエラーが発生しました: {str(e)}") 