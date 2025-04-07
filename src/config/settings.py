"""
アプリケーションの設定を管理するモジュール
"""

import streamlit as st

# API Keys
PINECONE_API_KEY = st.secrets["pinecone_key"]
OPENAI_API_KEY = st.secrets["openai_api_key"]

# Pinecone Settings
PINECONE_INDEX_NAME = st.secrets["index_name"]

# Text Processing Settings
CHUNK_SIZE = 500  # テキストを分割する際の1チャンクあたりの文字数
BATCH_SIZE = 100  # Pineconeへのアップロード時のバッチサイズ

# OpenAI Settings
EMBEDDING_MODEL = "text-embedding-ada-002"  # 使用する埋め込みモデル

# Search Settings
DEFAULT_TOP_K = 10  # デフォルトの検索結果数
SIMILARITY_THRESHOLD = 0.7  # 類似度のしきい値（0-1の範囲）

# Prompt Settings
DEFAULT_SYSTEM_PROMPT = """あなたは親切なアシスタントです。
質問に対して、提供された文脈に基づいて回答してください。
文脈に含まれていない情報については、推測せずに「その情報は提供された文脈に含まれていません」と回答してください。"""

DEFAULT_RESPONSE_TEMPLATE = """検索結果に基づいて回答します：

{context}

この回答は、アップロードされたドキュメントの内容に基づいています。"""

# デフォルトのプロンプトテンプレート
DEFAULT_PROMPT_TEMPLATES = [
    {
        "name": "標準プロンプト",
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "response_template": DEFAULT_RESPONSE_TEMPLATE
    },
    {
        "name": "簡潔な回答",
        "system_prompt": """あなたは簡潔で要点を押さえた回答をするアシスタントです。
質問に対して、提供された文脈から最も重要な情報を選び、簡潔に回答してください。""",
        "response_template": """要点をまとめます：

{context}"""
    },
    {
        "name": "詳細な回答",
        "system_prompt": """あなたは詳細な説明をするアシスタントです。
質問に対して、提供された文脈から関連する情報を全て含め、詳細に回答してください。""",
        "response_template": """詳細な回答を提供します：

{context}

この回答は、アップロードされたドキュメントの内容に基づいています。
必要に応じて、関連する情報を追加で提供します。"""
    }
] 