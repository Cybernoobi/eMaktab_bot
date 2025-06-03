from pydantic import BaseModel, ConfigDict


class ESchoolSchema(BaseModel):
    id: str
    regionName: str


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
    schools: list[ESchoolSchema]
    children: list
    isMethodist: bool
    experimentPRTopic: str

    model_config = ConfigDict(strict=True)

