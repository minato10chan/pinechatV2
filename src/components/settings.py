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
    st.title("⚙️ 設定")
    
    # タブで設定を分類
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 テキスト処理設定",
        "🔍 検索設定",
        "💬 プロンプト設定",
        "🗄️ データベース設定"
    ])
    
    # テキスト処理設定タブ
    with tab1:
        st.markdown("### テキスト処理の基本設定")
        st.markdown("テキストを処理する際の基本的な設定を行います。")
        
        col1, col2 = st.columns(2)
        with col1:
            chunk_size = st.number_input(
                "📏 チャンクサイズ（文字数）",
                min_value=100,
                max_value=2000,
                value=st.session_state.get("chunk_size", CHUNK_SIZE),
                help="テキストを分割する際の1チャンクあたりの文字数。大きすぎると精度が下がり、小さすぎると処理が遅くなります。"
            )
        
        with col2:
            batch_size = st.number_input(
                "📦 バッチサイズ",
                min_value=10,
                max_value=500,
                value=st.session_state.get("batch_size", BATCH_SIZE),
                help="Pineconeへのアップロード時のバッチサイズ。大きすぎるとメモリを消費し、小さすぎると処理が遅くなります。"
            )
        
        st.markdown("---")
        st.markdown("### 現在の設定値")
        st.json({
            "チャンクサイズ": chunk_size,
            "バッチサイズ": batch_size
        })

    # 検索設定タブ
    with tab2:
        st.markdown("### 検索の精度設定")
        st.markdown("検索結果の精度と表示数を調整します。")
        
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.number_input(
                "🔢 検索結果数",
                min_value=1,
                max_value=1000,
                value=st.session_state.get("top_k", DEFAULT_TOP_K),
                help="検索時に返す結果の数。多いほど関連性の低い結果も含まれます。"
            )
        
        with col2:
            similarity_threshold = st.slider(
                "📊 類似度しきい値",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get("similarity_threshold", SIMILARITY_THRESHOLD),
                step=0.05,
                help="この値以上の類似度を持つ結果のみを表示します。高いほど厳密な検索になります。"
            )
        
        st.markdown("---")
        st.markdown("### 現在の設定値")
        st.json({
            "検索結果数": top_k,
            "類似度しきい値": similarity_threshold
        })

    # プロンプト設定タブ
    with tab3:
        st.markdown("### プロンプトテンプレートの管理")
        st.markdown("チャットボットの応答を制御するプロンプトテンプレートを管理します。")
        
        # デフォルトプロンプトの編集
        with st.expander("📌 デフォルトプロンプトの編集", expanded=True):
            st.markdown("#### システムプロンプト")
            st.markdown("チャットボットの基本的な振る舞いを定義します。")
            default_system_prompt = st.text_area(
                "システムプロンプト",
                value=DEFAULT_SYSTEM_PROMPT,
                height=200,
                help="チャットボットの基本的な振る舞いや性格を定義するプロンプトです。"
            )
            
            st.markdown("#### レスポンステンプレート")
            st.markdown("応答の形式を定義します。")
            default_response_template = st.text_area(
                "レスポンステンプレート",
                value=DEFAULT_RESPONSE_TEMPLATE,
                height=200,
                help="応答の形式を定義するテンプレートです。{question}と{answer}は自動的に置換されます。"
            )
            
            if st.button("💾 デフォルトプロンプトを保存", type="primary"):
                save_default_prompts(default_system_prompt, default_response_template)
                st.success("✅ デフォルトプロンプトを保存しました")
                st.rerun()
        
        # 追加プロンプトの管理
        st.markdown("### カスタムプロンプトテンプレート")
        st.markdown("特定の用途に特化したプロンプトテンプレートを管理します。")
        
        prompt_templates = load_prompt_templates()
        
        for template in prompt_templates:
            with st.expander(f"📝 {template['name']}", expanded=False):
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
                    if st.button("💾 保存", key=f"save_{template['name']}"):
                        template['name'] = new_name
                        template['system_prompt'] = new_system_prompt
                        template['response_template'] = new_response_template
                        save_prompt_templates(prompt_templates)
                        st.success("✅ プロンプトテンプレートを保存しました")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ 削除", key=f"delete_{template['name']}"):
                        prompt_templates.remove(template)
                        save_prompt_templates(prompt_templates)
                        st.success("✅ プロンプトテンプレートを削除しました")
                        st.rerun()
        
        # 新しいプロンプトテンプレートの追加
        with st.expander("➕ 新しいプロンプトテンプレートの追加", expanded=False):
            new_template_name = st.text_input("テンプレート名")
            new_template_system_prompt = st.text_area(
                "システムプロンプト",
                height=200
            )
            new_template_response_template = st.text_area(
                "レスポンステンプレート",
                height=200
            )
            
            if st.button("➕ 新しいテンプレートを追加", type="primary"):
                if new_template_name and new_template_system_prompt and new_template_response_template:
                    prompt_templates.append({
                        "name": new_template_name,
                        "system_prompt": new_template_system_prompt,
                        "response_template": new_template_response_template
                    })
                    save_prompt_templates(prompt_templates)
                    st.success("✅ 新しいプロンプトテンプレートを追加しました")
                    st.rerun()
                else:
                    st.error("❌ すべてのフィールドを入力してください")

    # データベース設定タブ
    with tab4:
        st.markdown("### データベースの状態")
        st.markdown("Pineconeデータベースの状態を確認します。")
        
        if st.button("🔄 データベースの状態を確認", type="primary"):
            try:
                # インデックスの統計情報を取得
                stats = pinecone_service.get_index_stats()
                
                st.markdown("#### 📊 データベースの概要")
                st.json(stats)
                
                # データを取得
                data = pinecone_service.get_index_data()
                
                if data:
                    st.markdown("#### 📋 データベースの内容")
                    # データフレームを作成
                    df = pd.DataFrame(data)
                    
                    # ファイルごとにグループ化して集計
                    df_grouped = df.groupby('filename').agg({
                        'chunk_id': 'count',
                        'main_category': 'first',
                        'sub_category': 'first',
                        'city': 'first',
                        'created_date': 'first',
                        'upload_date': 'first',
                        'source': 'first'
                    }).reset_index()
                    
                    # 列名の日本語対応
                    column_names = {
                        'filename': 'ファイル名',
                        'chunk_id': 'チャンク数',
                        'main_category': '大カテゴリ',
                        'sub_category': '中カテゴリ',
                        'city': '市区町村',
                        'created_date': 'データ作成日',
                        'upload_date': 'アップロード日',
                        'source': 'ソース元'
                    }
                    
                    # 列名を日本語に変換
                    df_grouped = df_grouped.rename(columns=column_names)
                    
                    # データフレームを表示
                    st.dataframe(
                        df_grouped,
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("ℹ️ データベースにデータがありません。")
                    
            except Exception as e:
                st.error(f"❌ データベースの状態取得に失敗しました: {str(e)}")
                st.error(f"🔍 エラーの詳細: {type(e).__name__}")
                import traceback
                st.error(f"📜 スタックトレース:\n{traceback.format_exc()}")

    # 設定の保存ボタン
    st.markdown("---")
    if st.button("💾 すべての設定を保存", type="primary"):
        st.session_state.update({
            "chunk_size": chunk_size,
            "batch_size": batch_size,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        })
        st.success("✅ 設定を保存しました。") 