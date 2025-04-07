import streamlit as st
from src.services.pinecone_service import PineconeService
from src.config.settings import (
    CHUNK_SIZE,
    BATCH_SIZE,
    EMBEDDING_MODEL,
    DEFAULT_TOP_K,
    SIMILARITY_THRESHOLD,
    DEFAULT_PROMPT_TEMPLATES
)

def render_settings(pinecone_service: PineconeService):
    """設定画面のUIを表示"""
    st.title("設定")
    
    # テキスト処理設定
    st.header("テキスト処理設定")
    chunk_size = st.number_input(
        "チャンクサイズ（文字数）",
        min_value=100,
        max_value=2000,
        value=st.session_state.get("chunk_size", CHUNK_SIZE),
        help="テキストを分割する際の1チャンクあたりの文字数"
    )
    
    batch_size = st.number_input(
        "バッチサイズ",
        min_value=10,
        max_value=500,
        value=st.session_state.get("batch_size", BATCH_SIZE),
        help="Pineconeへのアップロード時のバッチサイズ"
    )

    # 検索設定
    st.header("検索設定")
    top_k = st.number_input(
        "検索結果数",
        min_value=1,
        max_value=20,
        value=st.session_state.get("top_k", DEFAULT_TOP_K),
        help="検索時に返す結果の数"
    )
    
    similarity_threshold = st.slider(
        "類似度しきい値",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get("similarity_threshold", SIMILARITY_THRESHOLD),
        step=0.05,
        help="この値以上の類似度を持つ結果のみを表示します"
    )

    # プロンプト設定
    st.header("プロンプト設定")
    
    # プロンプトテンプレートの選択
    if "prompt_templates" not in st.session_state:
        st.session_state.prompt_templates = DEFAULT_PROMPT_TEMPLATES.copy()
    
    # プロンプトテンプレートの一覧を表示
    st.subheader("プロンプトテンプレート一覧")
    for i, template in enumerate(st.session_state.prompt_templates):
        with st.expander(f"テンプレート: {template['name']}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text_area("システムプロンプト", value=template["system_prompt"], key=f"system_prompt_{i}", height=150)
                st.text_area("応答テンプレート", value=template["response_template"], key=f"response_template_{i}", height=150)
            with col2:
                if st.button("削除", key=f"delete_template_{i}"):
                    st.session_state.prompt_templates.pop(i)
                    st.rerun()
    
    # 新規プロンプトテンプレートの追加
    st.subheader("新規プロンプトテンプレートの追加")
    new_template_name = st.text_input("テンプレート名")
    new_system_prompt = st.text_area("システムプロンプト", height=150)
    new_response_template = st.text_area("応答テンプレート", height=150)
    
    if st.button("テンプレートを追加"):
        if new_template_name and new_system_prompt and new_response_template:
            st.session_state.prompt_templates.append({
                "name": new_template_name,
                "system_prompt": new_system_prompt,
                "response_template": new_response_template
            })
            st.success("テンプレートを追加しました")
            st.rerun()
        else:
            st.error("全てのフィールドを入力してください")

    # データベース設定
    st.header("データベース設定")
    if st.button("データベースの状態を確認"):
        try:
            stats = pinecone_service.get_index_stats()
            st.json(stats)
        except Exception as e:
            st.error(f"データベースの状態取得に失敗しました: {str(e)}")

    if st.button("データベースをクリア"):
        if st.warning("本当にデータベースをクリアしますか？この操作は取り消せません。"):
            try:
                pinecone_service.clear_index()
                st.success("データベースをクリアしました。")
            except Exception as e:
                st.error(f"データベースのクリアに失敗しました: {str(e)}")

    # 設定の保存
    if st.button("設定を保存"):
        st.session_state.update({
            "chunk_size": chunk_size,
            "batch_size": batch_size,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        })
        st.success("設定を保存しました。") 