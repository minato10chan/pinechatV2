import streamlit as st
from src.services.pinecone_service import PineconeService

def render_agent(pinecone_service: PineconeService):
    st.title("Agent Mode")
    
    # ユーザー入力
    user_input = st.text_input("タスクを入力してください", key="agent_input")
    
    if user_input:
        # Pineconeから関連情報を検索
        search_results = pinecone_service.search(user_input, top_k=3)
        
        # 検索結果の表示
        st.subheader("関連情報")
        for result in search_results:
            st.write(f"スコア: {result['score']:.2f}")
            st.write(result['metadata']['text'])
            st.write("---")
        
        # タスクの実行結果を表示（将来的にツール実行機能を追加）
        st.subheader("実行結果")
        st.info("現在はPinecone検索のみ対応しています。今後、ツール実行機能を追加予定です。") 