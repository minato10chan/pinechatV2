import streamlit as st
from src.services.pinecone_service import PineconeService
from src.config.settings import (
    CHUNK_SIZE,
    BATCH_SIZE,
    EMBEDDING_MODEL,
    DEFAULT_TOP_K,
    SIMILARITY_THRESHOLD,
    DEFAULT_PROMPT_TEMPLATES,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_RESPONSE_TEMPLATE,
    save_prompt_templates,
    load_prompt_templates,
    save_default_prompts
)
import json
import pandas as pd

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
    
    # プロンプトテンプレートの管理
    st.subheader("プロンプトテンプレートの管理")
    
    # デフォルトプロンプトの編集
    st.subheader("デフォルトプロンプトの編集")
    default_system_prompt = st.text_area(
        "デフォルトシステムプロンプト",
        value=DEFAULT_SYSTEM_PROMPT,
        height=200
    )
    default_response_template = st.text_area(
        "デフォルトレスポンステンプレート",
        value=DEFAULT_RESPONSE_TEMPLATE,
        height=200
    )
    
    if st.button("デフォルトプロンプトを保存"):
        # デフォルトプロンプトを保存
        save_default_prompts(default_system_prompt, default_response_template)
        st.success("デフォルトプロンプトを保存しました")
        st.rerun()
    
    # 追加プロンプトの管理
    st.subheader("追加プロンプトの管理")
    
    # プロンプトテンプレートの読み込み
    prompt_templates = load_prompt_templates()
    
    # 既存のプロンプトテンプレートの編集
    for template in prompt_templates:
        with st.expander(f"編集: {template['name']}"):
            new_name = st.text_input("名前", value=template['name'], key=f"name_{template['name']}")
            new_system_prompt = st.text_area(
                "システムプロンプト",
                value=template['system_prompt'],
                height=200,
                key=f"system_{template['name']}"
            )
            new_response_template = st.text_area(
                "レスポンステンプレート",
                value=template['response_template'],
                height=200,
                key=f"response_{template['name']}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("保存", key=f"save_{template['name']}"):
                    # プロンプトテンプレートを更新
                    template['name'] = new_name
                    template['system_prompt'] = new_system_prompt
                    template['response_template'] = new_response_template
                    save_prompt_templates(prompt_templates)
                    st.success("プロンプトテンプレートを保存しました")
                    st.rerun()
            
            with col2:
                if st.button("削除", key=f"delete_{template['name']}"):
                    # プロンプトテンプレートを削除
                    prompt_templates.remove(template)
                    save_prompt_templates(prompt_templates)
                    st.success("プロンプトテンプレートを削除しました")
                    st.rerun()
    
    # 新しいプロンプトテンプレートの追加
    st.subheader("新しいプロンプトテンプレートの追加")
    new_template_name = st.text_input("テンプレート名")
    new_template_system_prompt = st.text_area(
        "システムプロンプト",
        height=200
    )
    new_template_response_template = st.text_area(
        "レスポンステンプレート",
        height=200
    )
    
    if st.button("新しいテンプレートを追加"):
        if new_template_name and new_template_system_prompt and new_template_response_template:
            # 新しいプロンプトテンプレートを追加
            prompt_templates.append({
                "name": new_template_name,
                "system_prompt": new_template_system_prompt,
                "response_template": new_template_response_template
            })
            save_prompt_templates(prompt_templates)
            st.success("新しいプロンプトテンプレートを追加しました")
            st.rerun()
        else:
            st.error("すべてのフィールドを入力してください")

    # データベース設定
    st.header("データベース設定")
    if st.button("データベースの状態を確認"):
        try:
            # インデックスの統計情報を取得
            stats = pinecone_service.get_index_stats()
            st.subheader("データベースの概要")
            st.json(stats)
            
            # データを取得して表形式で表示
            st.subheader("データベースの内容")
            data = pinecone_service.get_index_data()
            if data:
                # データフレームの作成
                df = pd.DataFrame(data)
                
                # メタデータの列を追加
                df['大カテゴリ'] = df['metadata'].apply(lambda x: x.get('main_category', ''))
                df['中カテゴリ'] = df['metadata'].apply(lambda x: x.get('sub_category', ''))
                df['市区町村'] = df['metadata'].apply(lambda x: x.get('city', ''))
                df['データ作成日'] = df['metadata'].apply(lambda x: x.get('created_date', ''))
                df['アップロード日'] = df['metadata'].apply(lambda x: x.get('upload_date', ''))
                df['ソース元'] = df['metadata'].apply(lambda x: x.get('source', ''))
                
                # 表示する列を選択
                display_columns = [
                    'ID', 'filename', 'chunk_id', '大カテゴリ', '中カテゴリ', 
                    '市区町村', 'データ作成日', 'アップロード日', 'ソース元', 
                    'text', 'score'
                ]
                
                # データフレームの表示
                st.dataframe(
                    df[display_columns],
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.TextColumn("ID", width="small"),
                        "filename": st.column_config.TextColumn("ファイル名", width="medium"),
                        "chunk_id": st.column_config.TextColumn("チャンクID", width="small"),
                        "大カテゴリ": st.column_config.TextColumn("大カテゴリ", width="medium"),
                        "中カテゴリ": st.column_config.TextColumn("中カテゴリ", width="medium"),
                        "市区町村": st.column_config.TextColumn("市区町村", width="medium"),
                        "データ作成日": st.column_config.TextColumn("データ作成日", width="medium"),
                        "アップロード日": st.column_config.TextColumn("アップロード日", width="medium"),
                        "ソース元": st.column_config.TextColumn("ソース元", width="medium"),
                        "text": st.column_config.TextColumn("テキスト", width="large"),
                        "score": st.column_config.NumberColumn("スコア", width="small", format="%.3f")
                    }
                )
            else:
                st.info("データベースにデータがありません。")
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