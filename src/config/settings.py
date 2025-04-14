"""
アプリケーションの設定を管理するモジュール
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# 環境変数の読み込み
load_dotenv()

# API Keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") or st.secrets.get("pinecone_key")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("openai_api_key")

# Pinecone Settings
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") or st.secrets.get("index_name")
PINECONE_ASSISTANT_NAME = os.getenv("PINECONE_ASSISTANT_NAME") or st.secrets.get("assistant_name")

# Text Processing Settings
CHUNK_SIZE = 500  # テキストを分割する際の1チャンクあたりの文字数
BATCH_SIZE = 100  # Pineconeへのアップロード時のバッチサイズ

# OpenAI Settings
EMBEDDING_MODEL = "text-embedding-ada-002"  # 使用する埋め込みモデル

# Search Settings
DEFAULT_TOP_K = 1000  # デフォルトの検索結果数
SIMILARITY_THRESHOLD = 0.7  # 類似度のしきい値（0-1の範囲）

# Metadata Settings
DEFAULT_CREATION_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # メタデータの作成日が空の場合のデフォルト値

def get_metadata_creation_date(metadata):
    """
    メタデータの作成日を取得する関数
    作成日が空の場合は現在の日時を返す
    """
    if not metadata or "creation_date" not in metadata or not metadata["creation_date"]:
        return DEFAULT_CREATION_DATE
    return metadata["creation_date"]

# Prompt Settings
DEFAULT_SYSTEM_PROMPT = """あなたは親切で丁寧なAIアシスタントです。
ユーザーの質問に対して、以下のルールに従って回答してください：

1. 常に日本語で回答してください
2. 専門的な用語は分かりやすく説明してください
3. 必要に応じて具体例を挙げて説明してください
4. 回答は簡潔かつ明確にしてください
5. ユーザーの理解度に合わせて説明の詳細度を調整してください
"""

DEFAULT_RESPONSE_TEMPLATE = """{question}

回答:
{answer}
"""

# プロンプトテンプレートの設定
DEFAULT_PROMPT_TEMPLATES = [
    {
        "name": "デフォルト",
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "response_template": DEFAULT_RESPONSE_TEMPLATE
    },
    {
        "name": "詳細な回答",
        "system_prompt": """あなたは詳細な説明が得意なAIアシスタントです。
ユーザーの質問に対して、以下のルールに従って回答してください：

1. 常に日本語で回答してください
2. 専門的な用語は分かりやすく説明してください
3. 具体例を必ず挙げて説明してください
4. 回答は詳細かつ丁寧にしてください
5. 必要に応じて図や表を使用して説明してください
""",
        "response_template": """質問: {question}

詳細な回答:
{answer}

補足説明:
{additional_info}
"""
    },
    {
        "name": "簡潔な回答",
        "system_prompt": """あなたは簡潔な回答が得意なAIアシスタントです。
ユーザーの質問に対して、以下のルールに従って回答してください：

1. 常に日本語で回答してください
2. 回答は簡潔に、要点のみを述べてください
3. 専門用語は避け、平易な言葉で説明してください
4. 箇条書きや短い文で回答してください
5. 余計な説明は省いてください
""",
        "response_template": """質問: {question}

回答:
{answer}
"""
    }
]

# プロンプトテンプレートの保存と読み込み
PROMPT_TEMPLATES_FILE = "prompt_templates.json"

def save_prompt_templates(templates):
    """プロンプトテンプレートを保存"""
    with open(PROMPT_TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

def load_prompt_templates():
    """プロンプトテンプレートを読み込み"""
    if os.path.exists(PROMPT_TEMPLATES_FILE):
        with open(PROMPT_TEMPLATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_PROMPT_TEMPLATES.copy()

# デフォルトプロンプトの保存と読み込み
DEFAULT_PROMPTS_FILE = "default_prompts.json"

def save_default_prompts(system_prompt, response_template):
    """デフォルトプロンプトを保存"""
    with open(DEFAULT_PROMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "system_prompt": system_prompt,
            "response_template": response_template
        }, f, ensure_ascii=False, indent=2)

def load_default_prompts():
    """デフォルトプロンプトを読み込み"""
    if os.path.exists(DEFAULT_PROMPTS_FILE):
        with open(DEFAULT_PROMPTS_FILE, "r", encoding="utf-8") as f:
            prompts = json.load(f)
            return prompts["system_prompt"], prompts["response_template"]
    return DEFAULT_SYSTEM_PROMPT, DEFAULT_RESPONSE_TEMPLATE

# デフォルトプロンプトの読み込み
DEFAULT_SYSTEM_PROMPT, DEFAULT_RESPONSE_TEMPLATE = load_default_prompts()

# メタデータ設定
METADATA_CATEGORIES = {
    "大カテゴリ": [
        "物件概要",
        "地域特性・街のプロフィール",
        "教育・子育て",
        "交通・アクセス",
        "安全・防災",
        "行政施策・政策",
        "生活利便性",
        "不動産市場",
        "地域コミュニティ",
        "その他（個別の懸念・特殊事情）"
    ],
    "中カテゴリ": {
        "物件概要": [
            "完成時期",
            "販売開始",
            "建築確認",
            "間取り・仕様",
            "設備・オプション",
            "デザイン・外観",
            "建築会社・デベロッパー",
            "価格・費用",
            "資産価値・売却",
            "契約・手続き"
        ],
        "地域特性・街のプロフィール": [
            "概要・エリア区分",
            "人口・居住特性",
            "街の歴史・地域史",
            "地理的特性",
            "自然環境",
            "地域イベント・伝統行事",
            "都市連携・姉妹都市情報",
            "治安・騒音・環境整備",
            "風景・景観・街並み",
            "観光・地元特産品・名産・グルメ"
        ],
        "教育・子育て": [
            "保育園・幼稚園",
            "小学校・中学校",
            "学童・放課後支援",
            "習い事・塾",
            "子育て支援制度",
            "公園・遊び場",
            "病院・小児科",
            "学区・教育水準",
            "待機児童・入園状況",
            "学校イベント・行事"
        ],
        "交通・アクセス": [
            "最寄り駅・路線",
            "電車の混雑状況",
            "バス路線・本数",
            "駐輪場・駐車場",
            "道路交通量・渋滞",
            "車移動のしやすさ",
            "通勤・通学時間",
            "高速道路・インター",
            "タクシー・ライドシェア",
            "空港・新幹線アクセス"
        ],
        "安全・防災": [
            "防犯カメラ・交番の有無",
            "避難場所・防災拠点",
            "ハザードマップ（洪水・地震）",
            "土砂災害リスク",
            "耐震性・建物強度",
            "火災リスク・消防体制",
            "夜道の安全性",
            "台風・風害・雪害対策",
            "地震・液状化リスク",
            "交通事故・子ども見守り"
        ],
        "行政施策・政策": [
            "市政・行政組織",
            "再開発・都市計画",
            "交通インフラ整備",
            "公共施設運営・市民サービス",
            "ゴミ収集・清掃環境",
            "商業・産業振興策",
            "住宅政策・住環境整備",
            "福祉・医療支援",
            "補助金・助成制度",
            "行政評価・市民参加"
        ],
        "生活利便性": [
            "スーパー・買い物環境",
            "コンビニ・ドラッグストア",
            "銀行・金融機関・郵便局",
            "公共施設",
            "病院・クリニック・夜間救急",
            "文化施設・美術館・劇場",
            "スポーツ施設・ジム",
            "娯楽施設・カラオケ・映画館",
            "飲食店・グルメスポット",
            "宅配サービス・ネットスーパー"
        ],
        "不動産市場": [
            "地価の変動・推移",
            "将来の売却しやすさ",
            "賃貸需要・投資価値",
            "住宅ローン・金利動向",
            "人気エリアの傾向",
            "空き家・中古市場動向",
            "固定資産税・税制優遇",
            "マンション vs 戸建て",
            "住み替え・転勤時の影響",
            "不動産会社の評判・実績"
        ],
        "地域コミュニティ": [
            "自治会・町内会の活動",
            "地域の祭り",
            "ボランティア活動",
            "住民の意識・口コミ",
            "高齢者支援・福祉施設",
            "外国人コミュニティ",
            "風評・悪評の実態",
            "市民幸福度・満足度",
            "地域振興・コミュニティ活性化"
        ],
        "その他（個別の懸念・特殊事情）": [
            "スマートシティ・DX施策",
            "エコ対策・再生可能エネルギー",
            "観光客・短期滞在者の影響",
            "景観条例・建築規制",
            "駐車場問題・車両ルール",
            "宅配便・物流インフラ"
        ]
    },
    "市区町村": [
        "川越市",
        "さいたま市",
        "千葉市",
        "横浜市",
        "川崎市",
        "相模原市",
    ]
} 