from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(strict=True)


class ESchoolSchema(CustomBaseModel):
    id: str
    regionName: str


class EUserSchema(CustomBaseModel):
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


# EFullInfo schema
class AbsenceReason(CustomBaseModel):
    value: int
    label: str
    message_label: str = Field(..., alias='messageLabel')


class ChatStub(CustomBaseModel):
    jid: str
    static_chat_url: any = Field(..., alias='staticChatUrl')


class Schedule(CustomBaseModel):
    days: list
    chat_stub: ChatStub = Field(..., alias='chatStub')


class Children(CustomBaseModel):
    person_id: str = Field(..., alias='personId')
    school_id: str = Field(..., alias='schoolId')
    group_id: str = Field(..., alias='groupId')
    schedule: Schedule | None


class CurrentChild(Children):
    has_schedule: bool = Field(..., alias='hasSchedule')
    school_type: str = Field(..., alias='schoolType')


class UserSchedule(CustomBaseModel):
    api_url: str = Field(..., alias='apiUrl')
    children: list[Children]
    current_child: CurrentChild = Field(..., alias='currentChild')
    current_date: str = Field(..., alias='currentDate')


class Subject(CustomBaseModel):
    id: str
    name: str
    knowledge_area: str = Field(..., alias='knowledgeArea')
    subject_mood: any = Field(..., alias='subjectMood')


class MarkMarks(CustomBaseModel):
    id: str
    value: str
    max_value: any = Field(..., alias='maxValue')
    mood: str


class Mark(CustomBaseModel):
    date: str
    lesson_date: any = Field(..., alias='lessonDate')
    subject: Subject
    mark_type: str = Field(..., alias='markType')
    mark_type_text: str = Field(..., alias='markTypeText')
    short_mark_type_text: str = Field(..., alias='shortMarkTypeText')
    is_final: str = Field(..., alias='isFinal')
    marks: list[MarkMarks]
    work_id: str = Field(..., alias='workId')
    number: int
    period_id: str = Field(..., alias='periodId')
    section_id: str = Field(..., alias='sectionId')
    analytics_period: any = Field(..., alias='analyticsPeriod')


class UserMarksChildren(Children):
    marks: list[Mark]
    marks_indicators: list = Field(..., alias='analyticsPeriod')


class UserMarks(CustomBaseModel):
    children: list[UserMarksChildren]
    current_child: CurrentChild = Field(..., alias='currentChild')


class IdNamePageUrl(CustomBaseModel):
    id: str
    name: str
    page_url: str = Field(..., alias='pageUrl')


class School(IdNamePageUrl):
    type: str
    isOo: bool
    isNpoSpo: bool
    avatar_url: str = Field(..., alias='avatarUrl')
    region_ids: list[int] = Field(..., alias='regionIds')


class Group(IdNamePageUrl):
    is_criteria_journal_type: bool = Field(..., alias='isCriteriaJournalType')
    class_teacher_user_id: str = Field(..., alias='classTeacherUserId')
    class_teacher_chat_url: str = Field(..., alias='classTeacherChatUrl')
    class_teacher_jid: str = Field(..., alias='classTeacherJid')
    group_staff_page_url: str = Field(..., alias='groupStaffPageUrl')
    study_year: PositiveInt = Field(..., alias='studyYear')
    parallel: PositiveInt


class Periods(CustomBaseModel):
    id: str
    number: int
    type: str
    date_start: str = Field(..., alias='dateStart')
    date_finish: str = Field(..., alias='dateFinish')
    study_year: PositiveInt = Field(..., alias='studyYear')
    is_current: bool = Field(..., alias='isCurrent')


class ReportingPeriodGroup(CustomBaseModel):
    id: str
    type: str
    periods: list[Periods]


class ContextPersons(CustomBaseModel):
    user_id: str = Field(..., alias='userId')
    person_id: str = Field(..., alias='personId')
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    userAge: PositiveInt = Field(..., alias='userAge')
    avatar_url: str = Field(..., alias='avatarUrl')
    school: School
    group: Group
    reporting_period_group: ReportingPeriodGroup
    class_teacher_avatar_url: str = Field(..., alias='classTeacherAvatarUrl')
    class_teacher_name: str = Field(..., alias='classTeacherName')
    class_teacher_chat_id: str = Field(..., alias='classTeacherChatId')
    have_active_subscription: bool = Field(..., alias='haveActiveSubscription')
    class_teacher_peer_id: any = Field(..., alias='classTeacherPeerId')
    is_msy_popup_available: bool = Field(..., alias='isMsyPopupAvailable')
    is_female: bool = Field(..., alias='isFemale')
    group_name: str = Field(..., alias='groupName')
    journal_link: str = Field(..., alias='journalLink')
    school_id: str = Field(..., alias='schoolId')
    group_id: str = Field(..., alias='groupId')


class UserContextInfo(CustomBaseModel):
    sex: str
    user_id: str = Field(..., alias='userId')
    person_id: str = Field(..., alias='personId')
    first_name: str = Field(..., alias='firstName')
    middle_name: str = Field(..., alias='middleName')
    last_name: str = Field(..., alias='lastName')
    name: str
    avatar_url: str = Field(..., alias='avatarUrl')
    avatar_medium_url: str = Field(..., alias='avatarMediumUrl')
    is_parent: bool = Field(..., alias='isParent')
    is_student: bool = Field(..., alias='isStudent')
    current_culture_code: str = Field(..., alias='currentCultureCode')


class UserContext(CustomBaseModel):
    context_persons: list[ContextPersons] = Field(..., alias='contextPersons')
    current_context_person: ContextPersons = Field(..., alias='currentContextPerson')
    user_context_info: UserContextInfo = Field(..., alias='userContextInfo')


class UserLinksCurrentContext(CustomBaseModel):
    person_id: str = Field(..., alias='personId')
    user_id: str = Field(..., alias='userId')
    school_id: str = Field(..., alias='schoolId')
    group_id: str = Field(..., alias='groupId')
    is_parent: bool = Field(..., alias='isParent')
    feed_prefix: str = Field(..., alias='feedPrefix')


class UserLinks(CustomBaseModel):
    current_context: UserLinksCurrentContext = Field(..., alias='currentContext')


class UserGifts(CustomBaseModel):
    children: list
    gift_types: any = Field(..., alias='giftTypes')


class Banners(CustomBaseModel):
    right300x600: str = Field(..., alias='right300X600')
    mobile: str
    partners_right: str = Field(..., alias='partnersRight')
    vas: str
    smart_sor_soch: str = Field(..., alias='smartSorSoch')


class Analytics(CustomBaseModel):
    person_id: str = Field(..., alias='personId')
    user_id: str = Field(..., alias='userId')
    school_id: str = Field(..., alias='schoolId')
    group_id: str = Field(..., alias='groupId')
    is_criteria_journal_type: bool = Field(..., alias='isCriteriaJournalType')
    base_url: str = Field(..., alias='baseUrl')


class Urls(CustomBaseModel):
    ad_url: str = Field(..., alias='adUrl')
    feedback_url: str = Field(..., alias='feedbackUrl')
    payment_page_url: str = Field(..., alias='paymentPageUrl')
    favorites_url: str = Field(..., alias='favoritesUrl')
    communities_url: str = Field(..., alias='communitiesUrl')
    marks_url: str = Field(..., alias='marksUrl')
    moi_vyz_url: str = Field(..., alias='moiVyzUrl')
    smart_url: str = Field(..., alias='smartUrl')


class Links(CustomBaseModel):
    is_useful_links_component_visible: bool = Field(..., alias='isUsefulLinksComponentVisible')
    mobile_urls_enabled: bool = Field(..., alias='mobileUrlsEnabled')
    mobile_google_play_url: str = Field(..., alias='mobileGooglePlayUrl')
    mobile_app_store_url: str = Field(..., alias='mobileAppStoreUrl')
    analytics_url: str = Field(..., alias='analyticsUrl')


class Experiments(CustomBaseModel):
    user_feed_marks_finger: bool = Field(..., alias='userFeedMarksFinger')
    post_onelove: bool = Field(..., alias='postOnelove')
    post_reactions: bool = Field(..., alias='postReactions')
    post_reactions_click: bool = Field(..., alias='postReactionsClick')
    post_onelike = Field(..., alias='postOnelike')
    public_auto_subscribe: bool = Field(..., alias='publicAutoSubscribe')
    post_survey: bool = Field(..., alias='postSurvey')
    share: bool
    hide_ads: bool = Field(..., alias='hideAds')
    vuz_selection: bool = Field(..., alias='vuzSelection')
    moi_vyz: bool = Field(..., alias='moiVyz')
    vk_messenger: bool = Field(..., alias='vkMessenger')


class VocamateChatbotTutor(CustomBaseModel):
    is_available: bool = Field(..., alias='isAvailable')
    chat_id: any = Field(..., alias='chatId')
    url: str

class BubzChatbotTutor(CustomBaseModel):
    api_key: str = Field(..., alias='apiKey')
    agent_id: int = Field(..., alias='agentId')
    localization: str
    widget_show_delay_seconds: int = Field(..., alias='widgetShowDelaySeconds')
    is_available: bool = Field(..., alias='isAvailable')
    chat_id: any = Field(..., alias='chatId')
    url: str


class SurveyFormInitialState(CustomBaseModel):
    survey_form: any = Field(..., alias='surveyForm')
    survey_form_answer_url: str = Field(..., alias='surveyFormAnswerUrl')
    static_url: str = Field(..., alias='staticUrl')


class MomSaidYesInitialState(CustomBaseModel):
    absence_reasons: list[AbsenceReason] = Field(..., alias='absenceReasons')
    current_study_year_finish_date: datetime = Field(..., alias='currentStudyYearFinishDate')
    is_msy_popup_enabled: bool = Field(..., alias='isMsyPopupEnabled')


class UserStartPageInitialState(CustomBaseModel):
    user_schedule: UserSchedule = Field(..., alias='userSchedule')
    user_marks: UserMarks = Field(..., alias='userMarks')
    user_context: UserContext = Field(..., alias='userContext')
    user_links: UserLinks = Field(..., alias='userLinks')
    user_gifts: UserGifts = Field(..., alias='userGifts')
    banners: Banners
    analytics: Analytics
    analyticsEnabled: bool = Field(..., alias='analyticsEnabled')
    urls: Urls
    chat_enabled: bool = Field(..., alias='chatEnabled')
    vkChatEnabled: bool = Field(..., alias='vkChatEnabled')
    links: Links = Field(..., alias='links')
    environment_prefix: str = Field(..., alias='environmentPrefix')
    experiments: Experiments
    outside_push_banner: any = Field(..., alias='outsidePushBanner')
    vocamate_chatbot_tutor: VocamateChatbotTutor = Field(..., alias='vocamateChatbotTutor')
    bubz_chatbot_tutor: BubzChatbotTutor = Field(..., alias='bubzChatbotTutor')


class EFullInfoSchema(CustomBaseModel):
    survey_form_initial_state: SurveyFormInitialState = Field(
        ..., alias='SURVEY_FORM_INITIAL_STATE'
    )
    mom_said_yes__initial__state: MomSaidYesInitialState = Field(
        ..., alias='MOM_SAID_YES__INITIAL__STATE'
    )
    user__start__page__initial__state: UserStartPageInitialState = Field(
        ..., alias='USER__START__PAGE__INITIAL__STATE'
    )
