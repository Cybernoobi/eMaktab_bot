from pydantic import BaseModel


class EUserSchema(BaseModel):
    preferableLanguage: str
    suitableCultures: list[str]
    id: str
    sex: str
    age: int
    emailHash: str
    group: int
    role: str
    commonRole: str
    schools: list[dict[str, str]]
    children: list
    isMethodist: bool
    experimentPRTopic: str
