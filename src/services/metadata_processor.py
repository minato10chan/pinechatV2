from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

@dataclass
class MetadataField:
    """メタデータフィールドの定義"""
    name: str
    description: str
    required: bool = False

class MetadataProcessor:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(model_name=model_name)
        
        # 質問タイプごとのメタデータフィールド定義
        self.metadata_fields = {
            "facility": [
                MetadataField("name", "施設名", True),
                MetadataField("address", "住所", True),
                MetadataField("distance", "距離", True),
                MetadataField("business_hours", "営業時間"),
                MetadataField("additional_info", "その他の情報")
            ],
            "area": [
                MetadataField("area_name", "地域名", True),
                MetadataField("safety", "治安状況", True),
                MetadataField("transportation", "交通アクセス", True),
                MetadataField("education", "教育環境"),
                MetadataField("additional_info", "その他の特徴")
            ],
            "property": [
                MetadataField("property_name", "物件名", True),
                MetadataField("price", "価格", True),
                MetadataField("layout", "間取り", True),
                MetadataField("area", "面積"),
                MetadataField("facilities", "設備"),
                MetadataField("additional_info", "その他の特徴")
            ]
        }

    def extract_metadata(self, question_type: str, text: str) -> Dict[str, Any]:
        """テキストからメタデータを抽出"""
        if question_type not in self.metadata_fields:
            raise ValueError(f"Unknown question type: {question_type}")
        
        fields = self.metadata_fields[question_type]
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""以下のテキストから、{question_type}に関する情報を抽出してください。
必要なフィールド:
{chr(10).join([f"- {field.name}: {field.description} {'(必須)' if field.required else ''}" for field in fields])}

JSON形式で出力してください。"""),
            ("human", text)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        # ここでJSONをパースして辞書に変換
        # 実際の実装では、より堅牢なJSONパース処理が必要
        return eval(response)  # 注意: 実際の実装では安全なJSONパースを使用すること

    def validate_metadata(self, question_type: str, metadata: Dict[str, Any]) -> bool:
        """メタデータの検証"""
        if question_type not in self.metadata_fields:
            return False
        
        fields = self.metadata_fields[question_type]
        required_fields = [field.name for field in fields if field.required]
        
        return all(field in metadata for field in required_fields)

    def get_metadata_fields(self, question_type: str) -> List[MetadataField]:
        """質問タイプに応じたメタデータフィールドを取得"""
        if question_type not in self.metadata_fields:
            raise ValueError(f"Unknown question type: {question_type}")
        return self.metadata_fields[question_type] 