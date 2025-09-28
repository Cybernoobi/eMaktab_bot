from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class ESchoolSchema(BaseModel):
    id: str
    regionName: str


class EChildrenSchema(BaseModel):
    age: PositiveInt
    sex: Literal["Male", "Female"]


class EUserSchema(EChildrenSchema):
    preferable_language: str = Field(..., alias='preferableLanguage')
    suitable_cultures: list[str] = Field(..., alias='suitableCultures')
    id: str
    email_hash: str = Field(..., alias='emailHash')
    group: int
    role: Literal["EduStudent", "EduParent"] | str
    common_role: Literal["student", "staff", "parent"] | str = Field(..., alias='commonRole')
    schools: list[ESchoolSchema]
    children: list[EChildrenSchema] | None
    is_methodist: bool = Field(..., alias='isMethodist')
    experimentPRTopic: str

    model_config = ConfigDict(strict=True)


# __STATES_INFO__
class _IdsInfo(BaseModel):
    school_id: str = Field(..., alias='schoolId')
    group_id: str = Field(..., alias='groupId')
    person_id: str = Field(..., alias='personId')


class _IdsAndUserInfo(_IdsInfo):
    user_id: str = Field(..., alias='userId')


class _BasicSchoolOrGroupInfo(BaseModel):
    id: str
    name: str
    page_url: str = Field(..., alias='pageUrl')


class _BasicInfoChild(BaseModel):
    class Child(_IdsInfo):
        class Schedule(BaseModel):
            class Day(BaseModel):
                class DayHomeworksProgress(BaseModel):
                    total_lessons_with_homeworks_count: int = Field(
                        ..., alias='totalLessonsWithHomeworksCount'
                    )
                    completed_lessons_with_homeworks_count: int = Field(
                        ..., alias='completedLessonsWithHomeworksCount'
                    )

                class Lesson(BaseModel):
                    class Hours(BaseModel):
                        start_hour: str = Field(..., alias='startHour')
                        start_minute: str = Field(..., alias='startMinute')
                        end_hour: str = Field(..., alias='endHour')
                        end_minute: str = Field(..., alias='endMinute')

                    class Subject(BaseModel):
                        id: str
                        name: str
                        knowledge_area: str = Field(..., alias='knowledgeArea')

                    class Homework(BaseModel):
                        id: Any
                        text: str
                        is_completed: bool = Field(..., alias='isCompleted')
                        work_is_attach_required: bool = Field(..., alias='workIsAttachRequired')
                        attachments: list
                        user_attachments: list = Field(..., alias='userAttachments')
                        lesson_id: Any = Field(..., alias='lessonId')

                    class SmartHomework(Homework):
                        pass

                    class WorkMark(BaseModel):
                        class Mark(BaseModel):
                            id: str
                            value: str
                            mood: str

                        work_id: str = Field(..., alias='workId')
                        marks: list[Mark]

                    id: str
                    number: int
                    place: Any
                    start_time: str = Field(..., alias='startTime')
                    end_time: str = Field(..., alias='endTime')
                    hours: Hours
                    is_canceled: bool = Field(..., alias='isCanceled')
                    theme: str
                    meeting: Any
                    smart_work_info: Any = Field(..., alias='smartWorkInfo')
                    subject: Subject
                    important_works: list[str] = Field(..., alias='importantWorks')
                    homework: Homework
                    smart_homeworks: list[SmartHomework] = Field(..., alias='smartHomeworks')
                    has_attachment: bool = Field(..., alias='hasAttachment')
                    work_marks: list[WorkMark] = Field(..., alias='workMarks')
                    is_empty: bool = Field(..., alias='isEmpty')
                    comment: Any

                date: str
                utc_offset: int = Field(..., alias='utcOffset')
                has_important_work: bool = Field(..., alias='hasImportantWork')
                day_homeworks_progress: DayHomeworksProgress = Field(
                    ..., alias='dayHomeworksProgress'
                )
                lessons: list[Lesson]
                sor_sochs: list = Field(..., alias='sorSochs')

            class ChatStub(BaseModel):
                jid: str
                static_chat_url: Any = Field(..., alias='staticChatUrl')

            days: list[Day]
            chat_stub: ChatStub = Field(..., alias='chatStub')

        schedule: Schedule

    class CurrentChild(_IdsInfo):
        has_schedule: bool = Field(..., alias='hasSchedule')
        school_type: str = Field(..., alias='schoolType')

    children: list[Child]
    current_child: CurrentChild = Field(..., alias='currentChild')


class _UserBasicInfo(BaseModel):
    user_id: str = Field(..., alias='userId')
    person_id: str = Field(..., alias='personId')
    first_name: str = Field(..., alias='firstName')
    middle_name: str = Field(..., alias='middleName')
    last_name: str = Field(..., alias='lastName')
    avatar_url: str = Field(..., alias='avatarUrl')


class _IdAndType(BaseModel):
    id: str
    type: str


# __USER__START__PAGE__INITIAL__STATE__
class UserStartPageInitialState(BaseModel):
    class UserSchedule(_BasicInfoChild):
        api_url: str = Field(..., alias='apiUrl')
        current_date: str = Field(..., alias='currentDate')

    class UserMarks(_BasicInfoChild):
        pass

    class UserContext(BaseModel):
        class ContextPerson(_IdsInfo, _UserBasicInfo):
            class School(_BasicSchoolOrGroupInfo):
                type: str
                is_oo: bool = Field(..., alias='isOo')
                is_npo_spo: bool = Field(..., alias='isNpoSpo')
                avatar_url: str = Field(..., alias='avatarUrl')
                region_ids: list[int] = Field(..., alias='regionIds')

            class Group(_BasicSchoolOrGroupInfo):
                is_criteria_journal_type: bool = Field(..., alias='isCriteriaJournalType')
                class_teacher_user_id: str = Field(..., alias='classTeacherUserId')
                class_teacher_chat_url: str = Field(..., alias='classTeacherChatUrl')
                class_teacher_jid: str = Field(..., alias='classTeacherJid')
                group_staff_page_url: str = Field(..., alias='groupStaffPageUrl')
                study_year: int = Field(..., alias='studyYear')
                parallel: int

            class ReportingPeriodGroup(_IdAndType):
                class Period(_IdAndType):
                    number: int
                    date_start: str = Field(..., alias='dateStart')
                    date_finish: str = Field(..., alias='dateFinish')
                    study_year: int = Field(..., alias='studyYear')
                    is_current: bool = Field(..., alias='isCurrent')

                periods: list[Period]

            user_age: int = Field(..., alias='userAge')

            school: School
            group: Group
            reporting_period_group: ReportingPeriodGroup = Field(
                ..., alias='reportingPeriodGroup'
            )
            class_teacher_avatar_url: str = Field(..., alias='classTeacherAvatarUrl')
            class_teacher_name: str = Field(..., alias='classTeacherName')
            class_teacher_chat_id: str = Field(..., alias='classTeacherChatId')
            have_active_subscription: bool = Field(..., alias='haveActiveSubscription')
            class_teacher_peer_id: Any = Field(..., alias='classTeacherPeerId')
            is_msy_popup_available: bool = Field(..., alias='isMsyPopupAvailable')
            is_female: bool = Field(..., alias='isFemale')
            group_name: str = Field(..., alias='groupName')
            journal_link: str = Field(..., alias='journalLink')
            ratings_feed_widget: Any = Field(..., alias='ratingsFeedWidget')

        class CurrentContextPerson(ContextPerson):
            pass

        class UserContextInfo(_UserBasicInfo):
            sex: str
            name: str
            avatar_medium_url: str = Field(..., alias='avatarMediumUrl')
            is_parent: bool = Field(..., alias='isParent')
            is_student: bool = Field(..., alias='isStudent')
            current_culture_code: str = Field(..., alias='currentCultureCode')

        context_persons: list[ContextPerson] = Field(..., alias='contextPersons')
        current_context_person: CurrentContextPerson = Field(
            ..., alias='currentContextPerson'
        )
        user_context_info: UserContextInfo = Field(..., alias='userContextInfo')
        group_parents_topic_event_key: str = Field(..., alias='groupParentsTopicEventKey')
        education_type: str = Field(..., alias='educationType')

    class UserLinks(BaseModel):
        class CurrentContext(_IdsAndUserInfo):
            is_parent: bool = Field(..., alias='isParent')
            feed_prefix: str = Field(..., alias='feedPrefix')

        current_context: CurrentContext = Field(..., alias='currentContext')

    class Banners(BaseModel):
        right300_x600: str = Field(..., alias='right300X600')
        mobile: str
        partners_right: str = Field(..., alias='partnersRight')
        vas: str
        smart_sor_soch: str = Field(..., alias='smartSorSoch')

    class FeedEventsWidget(BaseModel):
        children: list

    class Analytics(_IdsAndUserInfo):
        is_criteria_journal_type: bool = Field(..., alias='isCriteriaJournalType')
        base_url: str = Field(..., alias='baseUrl')

    class Urls(BaseModel):
        ad_url: str = Field(..., alias='adUrl')
        feedback_url: str = Field(..., alias='feedbackUrl')
        payment_page_url: str = Field(..., alias='paymentPageUrl')
        favorites_url: str = Field(..., alias='favoritesUrl')
        communities_url: str = Field(..., alias='communitiesUrl')
        marks_url: str = Field(..., alias='marksUrl')
        moi_vyz_url: str = Field(..., alias='moiVyzUrl')
        smart_url: str = Field(..., alias='smartUrl')

    class Links(BaseModel):
        is_useful_links_component_visible: bool = Field(
            ..., alias='isUsefulLinksComponentVisible'
        )
        mobile_urls_enabled: bool = Field(..., alias='mobileUrlsEnabled')
        mobile_google_play_url: str = Field(..., alias='mobileGooglePlayUrl')
        mobile_app_store_url: str = Field(..., alias='mobileAppStoreUrl')
        analytics_url: str = Field(..., alias='analyticsUrl')

    class Experiments(BaseModel):
        user_feed_marks_finger: bool = Field(..., alias='userFeedMarksFinger')
        post_onelove: bool = Field(..., alias='postOnelove')
        post_reactions: bool = Field(..., alias='postReactions')
        post_reactions_click: bool = Field(..., alias='postReactionsClick')
        post_onelike: bool = Field(..., alias='postOnelike')
        public_auto_subscribe: bool = Field(..., alias='publicAutoSubscribe')
        post_survey: bool = Field(..., alias='postSurvey')
        share: bool
        hide_ads: bool = Field(..., alias='hideAds')
        vuz_selection: bool = Field(..., alias='vuzSelection')
        moi_vyz: bool = Field(..., alias='moiVyz')
        vk_messenger: bool = Field(..., alias='vkMessenger')
        is_smart_homework_enabled: bool = Field(..., alias='isSmartHomeworkEnabled')
        is_status_stub_segmented_enabled: bool = Field(
            ..., alias='isStatusStubSegmentedEnabled'
        )
        is_events_widget: bool = Field(..., alias='isEventsWidget')
        is_statistics_entry_points: bool = Field(..., alias='isStatisticsEntryPoints')

    class VocamateChatbotTutor(BaseModel):
        is_available: bool = Field(..., alias='isAvailable')
        chat_id: Any = Field(..., alias='chatId')
        url: str

    class BubzChatbotTutor(BaseModel):
        api_key: str = Field(..., alias='apiKey')
        agent_id: int = Field(..., alias='agentId')
        localization: str
        widget_show_delay_seconds: int = Field(..., alias='widgetShowDelaySeconds')
        is_available: bool = Field(..., alias='isAvailable')
        chat_id: Any = Field(..., alias='chatId')
        url: str

    user_schedule: UserSchedule = Field(..., alias='userSchedule')
    user_marks: UserMarks = Field(..., alias='userMarks')
    user_context: UserContext = Field(..., alias='userContext')
    user_links: UserLinks = Field(..., alias='userLinks')
    banners: Banners
    feed_events_widget: FeedEventsWidget = Field(..., alias='feedEventsWidget')
    analytics: Analytics
    analytics_enabled: bool = Field(..., alias='analyticsEnabled')
    urls: Urls
    chat_enabled: bool = Field(..., alias='chatEnabled')
    vk_chat_enabled: bool = Field(..., alias='vkChatEnabled')
    links: Links
    environment_prefix: str = Field(..., alias='environmentPrefix')
    experiments: Experiments
    partners_recommendation_experiments: list = Field(
        ..., alias='partnersRecommendationExperiments'
    )
    outside_push_banner: Any = Field(..., alias='outsidePushBanner')
    vocamate_chatbot_tutor: VocamateChatbotTutor = Field(
        ..., alias='vocamateChatbotTutor'
    )
    bubz_chatbot_tutor: BubzChatbotTutor = Field(..., alias='bubzChatbotTutor')
    yandex_search_i_frame_url: Any = Field(..., alias='yandexSearchIFrameUrl')
    has_active_mobile_subscription: bool = Field(..., alias="hasActiveMobileSubscription")
    trainers_banner: str = Field(..., alias="trainersBanner")


# __SURVEY_FORM_INITIAL_STATE__
class SurveyFormInitialState(BaseModel):
    survey_form: Any = Field(..., alias='surveyForm')
    survey_form_answer_url: str = Field(..., alias='surveyFormAnswerUrl')
    static_url: str = Field(..., alias='staticUrl')


# __MOM_SAID_YES__INITIAL__STATE__
class MomSaidYesInitialState(BaseModel):
    class AbsenceReason(BaseModel):
        value: int
        label: str
        message_label: str = Field(..., alias='messageLabel')

    absence_reasons: list[AbsenceReason] = Field(..., alias='absenceReasons')
    current_study_year_finish_date: str = Field(..., alias='currentStudyYearFinishDate')
    is_msy_popup_enabled: bool = Field(..., alias='isMsyPopupEnabled')


# __ALL__INITIAL__STATES__
class EUserAllInitialStates(BaseModel):
    mom_said_yes: MomSaidYesInitialState = Field(..., alias='momSaidYesInitialState')
    survey_form: SurveyFormInitialState = Field(..., alias='surveyFormInitialState')
    user_start_page: UserStartPageInitialState = Field(..., alias='userStartPage')


class Test(BaseModel):
    date: datetime
