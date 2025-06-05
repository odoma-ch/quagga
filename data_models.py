from pydantic import BaseModel


class KGList(BaseModel):
    kg_id: int
    kg_name: str
    kg_description: str
    kg_url: str
