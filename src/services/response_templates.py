from typing import Dict, Any, List
from dataclasses import dataclass
from langchain.prompts import ChatPromptTemplate

@dataclass
class ResponseTemplate:
    """回答テンプレートの基本クラス"""
    template: str
    required_fields: List[str]

class ResponseTemplates:
    def __init__(self):
        self.templates = {
            "facility": ResponseTemplate(
                template="""以下の施設情報をお伝えします：

施設名: {name}
住所: {address}
距離: {distance}
営業時間: {business_hours}
その他の情報: {additional_info}

ご不明な点がございましたら、お気軽にお申し付けください。""",
                required_fields=["name", "address", "distance"]
            ),
            "area": ResponseTemplate(
                template="""以下の地域情報をお伝えします：

地域名: {area_name}
治安状況: {safety}
交通アクセス: {transportation}
教育環境: {education}
その他の特徴: {additional_info}

ご不明な点がございましたら、お気軽にお申し付けください。""",
                required_fields=["area_name", "safety", "transportation"]
            ),
            "property": ResponseTemplate(
                template="""以下の物件情報をお伝えします：

物件名: {property_name}
価格: {price}
間取り: {layout}
面積: {area}
設備: {facilities}
その他の特徴: {additional_info}

ご不明な点がございましたら、お気軽にお申し付けください。""",
                required_fields=["property_name", "price", "layout"]
            )
        }

    def get_template(self, question_type: str) -> ResponseTemplate:
        """質問タイプに応じたテンプレートを取得"""
        if question_type not in self.templates:
            raise ValueError(f"Unknown question type: {question_type}")
        return self.templates[question_type]

    def format_response(self, question_type: str, data: Dict[str, Any]) -> str:
        """テンプレートを使用して回答を生成"""
        template = self.get_template(question_type)
        
        # 必須フィールドのチェック
        missing_fields = [field for field in template.required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # テンプレートにデータを適用
        return template.template.format(**data) 