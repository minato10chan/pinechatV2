import streamlit as st
from src.services.pinecone_service import PineconeService

def render_agent(pinecone_service: PineconeService):
    st.title("Agent Mode")
    
    # ユーザー入力
    user_input = st.text_input("タスクを入力してください", key="agent_input")
    
    if user_input:
        # 思考プロセスの表示
        st.subheader("🤔 思考プロセス")
        
        # タスクの分析
        st.write("1. タスクの分析")
        st.write(f"- 入力されたタスク: {user_input}")
        st.write("- タスクの目的: 関連情報の検索と表示")
        
        # 実行計画
        st.write("2. 実行計画")
        st.write("- Pineconeデータベースから関連情報を検索")
        st.write("- 検索結果をスコア順に表示")
        st.write("- 将来的にはツール実行機能を追加予定")
        
        # 実行
        st.write("3. 実行")
        st.write("- Pinecone検索を実行中...")
        
        # Pineconeから関連情報を検索
        search_results = pinecone_service.query(user_input, top_k=3)
        
        # 検索結果の表示
        st.subheader("🔍 関連情報")
        st.write(f"- 検索結果: {len(search_results['matches'])}件の関連情報が見つかりました")
        
        for i, match in enumerate(search_results["matches"], 1):
            st.write(f"#### 結果 {i}")
            st.write(f"- 関連度スコア: {match.score:.2f}")
            st.write(f"- 内容: {match.metadata['text']}")
            st.write("---")
        
        # 実行結果の要約
        st.subheader("📝 実行結果の要約")
        st.write("- タスクの実行が完了しました")
        st.write(f"- {len(search_results['matches'])}件の関連情報を表示しました")
        st.write("- 現在はPinecone検索のみ対応しています")
        st.write("- 今後、ツール実行機能を追加予定です") 