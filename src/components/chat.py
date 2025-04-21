import streamlit as st
import json
from datetime import datetime
from src.services.pinecone_service import PineconeService
from src.services.langchain_service import LangChainService
from src.config.settings import (
    DEFAULT_PROMPT_TEMPLATES,
    load_prompt_templates
)
import streamlit.components.v1 as components

def save_chat_history(messages, filename=None):
    """チャット履歴をJSONファイルとして保存"""
    if filename is None:
        filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # メッセージを保存可能な形式に変換
    save_data = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    
    # JSONファイルとして保存
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_chat_history(file):
    """チャット履歴をJSONファイルから読み込み"""
    data = json.load(file)
    return data.get("messages", [])

def get_property_list(pinecone_service: PineconeService) -> list:
    """物件情報の一覧を取得"""
    try:
        # Pineconeから物件情報の一覧を取得
        results = pinecone_service.list_vectors(namespace="property")
        
        if not results:
            return []
            
        properties = []
        for match in results:
            # テキストから物件情報を抽出
            text = match.metadata["text"]
            lines = text.split('\n')
            
            # 物件名と場所を抽出（最初の2行を想定）
            name = lines[0].strip() if len(lines) > 0 else "不明"
            location = lines[1].strip() if len(lines) > 1 else "不明"
            
            properties.append({
                "id": match.id,
                "name": name,
                "location": location,
                "text": text
            })
            
        return properties
    except Exception as e:
        st.error(f"物件情報の取得中にエラーが発生しました: {str(e)}")
        return []

def get_property_info(property_id: str, pinecone_service: PineconeService) -> str:
    """選択された物件の詳細情報を取得"""
    try:
        # Pineconeから物件情報を取得
        result = pinecone_service.get_by_id(property_id, namespace="property")
        
        if not result:
            return "物件情報が見つかりませんでした。"
            
        # テキストを取得
        return result.get("text", "物件情報が見つかりませんでした。")
    except Exception as e:
        return f"物件情報の取得中にエラーが発生しました: {str(e)}"

def render_chat(pinecone_service: PineconeService):
    """チャット機能のUIを表示"""
    st.title("チャット")
    st.write("アップロードしたドキュメントについて質問できます。")

    # LangChainサービスの初期化
    if "langchain_service" not in st.session_state:
        st.session_state.langchain_service = LangChainService()
    
    # プロンプトテンプレートの読み込み（毎回最新の状態を取得）
    st.session_state.prompt_templates = load_prompt_templates()
    
    # サイドバーに履歴管理機能を配置
    with st.sidebar:
        st.header("チャット履歴管理")
        
        # プロンプトテンプレートの選択
        st.header("プロンプトテンプレート")
        template_names = [template["name"] for template in st.session_state.prompt_templates]
        selected_template = st.selectbox(
            "使用するテンプレートを選択",
            template_names,
            index=0
        )
        
        # 物件情報の選択
        st.header("物件情報")
        properties = get_property_list(pinecone_service)
        
        if properties:
            # 物件の選択肢を作成（物件名と場所を表示）
            property_options = [f"{p['name']} - {p['location']}" for p in properties]
            selected_property = st.selectbox(
                "物件を選択",
                options=property_options,
                index=0
            )
            
            # 選択された物件のIDを取得
            selected_property_id = properties[property_options.index(selected_property)]["id"]
            
            # 選択された物件の詳細情報を取得
            st.session_state.property_info = get_property_info(selected_property_id, pinecone_service)
            
            # 物件の詳細情報を表示
            with st.expander("選択中の物件情報"):
                st.markdown(st.session_state.property_info)
        else:
            st.warning("物件情報が登録されていません。")
            st.session_state.property_info = "物件情報が登録されていません。"
        
        # 選択されたテンプレートの内容を表示
        selected_template_data = next(
            template for template in st.session_state.prompt_templates 
            if template["name"] == selected_template
        )
        with st.expander("選択中のテンプレート"):
            st.text_area("システムプロンプト", value=selected_template_data["system_prompt"], disabled=True)
            st.text_area("応答テンプレート", value=selected_template_data["response_template"], disabled=True)
        
        # 履歴の保存 (ローカルダウンロード)
        if st.session_state.messages:
            history_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button(
                label="履歴をダウンロード",
                data=history_json,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_history"
            )
        else:
            st.button("履歴をダウンロード", disabled=True, key="download_history_disabled")
        
        # 履歴の読み込み
        uploaded_file = st.file_uploader("保存した履歴を読み込む", type=['json'])
        if uploaded_file is not None:
            try:
                loaded_messages = load_chat_history(uploaded_file)
                st.session_state.messages = loaded_messages
                st.session_state.langchain_service.clear_memory()
                st.success("履歴を読み込みました")
            except Exception as e:
                st.error(f"履歴の読み込みに失敗しました: {str(e)}")
        
        # 履歴のクリア
        if st.button("履歴をクリア"):
            st.session_state.messages = []
            st.session_state.langchain_service.clear_memory()
            st.success("履歴をクリアしました")
        
        # 履歴の表示
        st.header("会話履歴")
        for i, message in enumerate(st.session_state.messages):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{message['role']}: {message['content'][:50]}...")
                with col2:
                    if st.button("削除", key=f"delete_{i}"):
                        st.session_state.messages.pop(i)
                        st.rerun()
    
    # メインのチャット表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # 詳細情報が含まれている場合は表示
            if "details" in message:
                with st.expander("詳細情報"):
                    st.json(message["details"])

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください"):
        # ユーザーメッセージを表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 選択されたテンプレートを取得
        selected_template_data = next(
            template for template in st.session_state.prompt_templates 
            if template["name"] == selected_template
        )
        
        # LangChainを使用して応答を生成
        with st.spinner("応答を生成中..."):
            response, details = st.session_state.langchain_service.get_response(
                prompt,
                system_prompt=selected_template_data["system_prompt"],
                response_template=selected_template_data["response_template"],
                property_info=st.session_state.get("property_info", "物件情報が見つかりませんでした。")
            )
            
            # アシスタントの応答を表示
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "details": details
            })
            with st.chat_message("assistant"):
                st.markdown(response)
                with st.expander("詳細情報"):
                    st.json(details) 