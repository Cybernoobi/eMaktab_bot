from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(strict=True)


# EFullInfo schema
class IdName(CustomBaseModel):
    id: str
    name: str


class UserBase(CustomBaseModel):
    sex: str
    name: str


class Children(CustomBaseModel):
    class Schedule(CustomBaseModel):
        class ChatStub(CustomBaseModel):
            jid: str
            static_chat_url: Any = Field(..., alias='staticChatUrl')

        days: list
        chat_stub: ChatStub = Field(..., alias='chatStub')

    person_id: str = Field(..., alias='personId')
    school_id: str = Field(..., alias='schoolId')
    group_id: str = Field(..., alias='groupId')
    schedule: Schedule | None


class CurrentChild(Children):
    has_schedule: bool = Field(..., alias='hasSchedule')
    school_type: str = Field(..., alias='schoolType')


class SurveyFormInitialState(CustomBaseModel):
    survey_form: Any = Field(..., alias='surveyForm')
    survey_form_answer_url: str = Field(..., alias='surveyFormAnswerUrl')
    static_url: str = Field(..., alias='staticUrl')


class MomSaidYesInitialState(CustomBaseModel):
    class AbsenceReason(CustomBaseModel):
        value: int
        label: str
        message_label: str = Field(..., alias='messageLabel')

    absence_reasons: list[AbsenceReason] = Field(..., alias='absenceReasons')
    current_study_year_finish_date: datetime = Field(..., alias='currentStudyYearFinishDate')
    is_msy_popup_enabled: bool = Field(..., alias='isMsyPopupEnabled')


class UserStartPageInitialState(CustomBaseModel):
    class UserSchedule(CustomBaseModel):
        api_url: str = Field(..., alias='apiUrl')
        children: list[Children]
        current_child: CurrentChild = Field(..., alias='currentChild')
        current_date: str = Field(..., alias='currentDate')

    class UserContext(CustomBaseModel):
        class ContextPersons(CustomBaseModel):
            class ReportingPeriodGroup(CustomBaseModel):
                class Periods(CustomBaseModel):
                    id: str
                    number: int
                    type: str
                    date_start: str = Field(..., alias='dateStart')
                    date_finish: str = Field(..., alias='dateFinish')
                    study_year: PositiveInt = Field(..., alias='studyYear')
                    is_current: bool = Field(..., alias='isCurrent')

                id: str
                type: str
                periods: list[Periods]

            class School(IdName):
                type: str
                isOo: bool
                isNpoSpo: bool
                avatar_url: str = Field(..., alias='avatarUrl')
                region_ids: list[int] = Field(..., alias='regionIds')
                page_url: str = Field(..., alias='pageUrl')

            class Group(IdName):
                is_criteria_journal_type: bool = Field(..., alias='isCriteriaJournalType')
                class_teacher_user_id: str = Field(..., alias='classTeacherUserId')
                class_teacher_chat_url: str = Field(..., alias='classTeacherChatUrl')
                class_teacher_jid: str = Field(..., alias='classTeacherJid')
                group_staff_page_url: str = Field(..., alias='groupStaffPageUrl')
                study_year: PositiveInt = Field(..., alias='studyYear')
                parallel: PositiveInt

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
            class_teacher_peer_id: Any = Field(..., alias='classTeacherPeerId')
            is_msy_popup_available: bool = Field(..., alias='isMsyPopupAvailable')
            is_female: bool = Field(..., alias='isFemale')
            group_name: str = Field(..., alias='groupName')
            journal_link: str = Field(..., alias='journalLink')
            school_id: str = Field(..., alias='schoolId')
            group_id: str = Field(..., alias='groupId')

        class UserContextInfo(UserBase):
            user_id: str = Field(..., alias='userId')
            person_id: str = Field(..., alias='personId')
            first_name: str = Field(..., alias='firstName')
            middle_name: str = Field(..., alias='middleName')
            last_name: str = Field(..., alias='lastName')
            avatar_url: str = Field(..., alias='avatarUrl')
            avatar_medium_url: str = Field(..., alias='avatarMediumUrl')
            is_parent: bool = Field(..., alias='isParent')
            is_student: bool = Field(..., alias='isStudent')
            current_culture_code: str = Field(..., alias='currentCultureCode')

        context_persons: list[ContextPersons] = Field(..., alias='contextPersons')
        current_context_person: ContextPersons = Field(..., alias='currentContextPerson')
        user_context_info: UserContextInfo = Field(..., alias='userContextInfo')

    class UserMarks(CustomBaseModel):
        class UserMarksChildren(Children):
            class Mark(CustomBaseModel):
                class Subject(IdName):
                    knowledge_area: str = Field(..., alias='knowledgeArea')
                    subject_mood: Any = Field(..., alias='subjectMood')

                class MarkMarks(CustomBaseModel):
                    id: str
                    value: str
                    max_value: Any = Field(..., alias='maxValue')
                    mood: str

                date: str
                lesson_date: Any = Field(..., alias='lessonDate')
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
                analytics_period: Any = Field(..., alias='analyticsPeriod')

            marks: list[Mark]
            marks_indicators: list = Field(..., alias='analyticsPeriod')

        children: list[UserMarksChildren]
        current_child: CurrentChild = Field(..., alias='currentChild')

    class UserLinks(CustomBaseModel):
        class UserLinksCurrentContext(CustomBaseModel):
            person_id: str = Field(..., alias='personId')
            user_id: str = Field(..., alias='userId')
            school_id: str = Field(..., alias='schoolId')
            group_id: str = Field(..., alias='groupId')
            is_parent: bool = Field(..., alias='isParent')
            feed_prefix: str = Field(..., alias='feedPrefix')

        current_context: UserLinksCurrentContext = Field(..., alias='currentContext')

    class UserGifts(CustomBaseModel):
        children: list
        gift_types: Any = Field(..., alias='giftTypes')

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
        post_onelike: bool = Field(..., alias='postOnelike')
        public_auto_subscribe: bool = Field(..., alias='publicAutoSubscribe')
        post_survey: bool = Field(..., alias='postSurvey')
        share: bool
        hide_ads: bool = Field(..., alias='hideAds')
        vuz_selection: bool = Field(..., alias='vuzSelection')
        moi_vyz: bool = Field(..., alias='moiVyz')
        vk_messenger: bool = Field(..., alias='vkMessenger')

    class VocamateChatbotTutor(CustomBaseModel):
        is_available: bool = Field(..., alias='isAvailable')
        chat_id: Any = Field(..., alias='chatId')
        url: str

    class BubzChatbotTutor(CustomBaseModel):
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
    outside_push_banner: Any = Field(..., alias='outsidePushBanner')
    vocamate_chatbot_tutor: VocamateChatbotTutor = Field(..., alias='vocamateChatbotTutor')
    bubz_chatbot_tutor: BubzChatbotTutor = Field(..., alias='bubzChatbotTutor')


class TalkInitialState(CustomBaseModel):
    class User(UserBase):
        avatar_large: str = Field(..., alias='avatarLarge')
        irrelevant: bool
        created: bool
        is_system: bool = Field(..., alias='isSystem')
        school_name: Any = Field(..., alias='schoolName')
        class_teacher: Any = Field(..., alias='classTeacher')
        chat_type: str = Field(..., alias='chatType')
        school_id: str = Field(..., alias='schoolId')
        is_archive_contact: bool = Field(..., alias='isArchiveContact')
        affiliations: Any
        is_poo_school: bool = Field(..., alias='isPooSchool')
        is_odo_school: bool = Field(..., alias='isOdoSchool')
        is_gpt_chat: bool = Field(..., alias='isGptChat')
        jid: str
        type: str
        short_name: str = Field(..., alias='shortName')
        avatar: str
        avatar_background: str = Field(..., alias='avatarBackground')
        unknown: bool
        roles: list[str]
        school_ids: list[str] = Field(..., alias='schoolIds')
        groups: Any
        teacher_groups: Any
        class_teacher_groups: list[str] = Field(..., alias='classTeacherGroups')
        subjects: Any
        profile_url: str = Field(..., alias='profileUrl')
        is_dnevnik_expert: bool = Field(..., alias='isDnevnikExpert')

    class Urls(CustomBaseModel):
        messenger_url: str = Field(..., alias='messengerUrl')
        favicon_url: str = Field(..., alias='faviconUrl')
        message_favicon_url: str = Field(..., alias='messageFaviconUrl')
        return_url: str = Field(..., alias='returnUrl')
        logo_url: str = Field(..., alias='logoUrl')
        terms_url: str = Field(..., alias='termsUrl')
        host: str
        multi_user_chat_host: str = Field(..., alias='multiUserChatHost')
        feedback_url: str = Field(..., alias='feedbackUrl')
        async_task_api_url: str = Field(..., alias='asyncTaskApiUrl')
        custom_chats_avatars_url: str = Field(..., alias='customChatsAvatarsUrl')
        message_archive: Any = Field(..., alias='messageArchive')
        polls_api_url: str = Field(..., alias='pollsApiUrl')
        pools_url: str = Field(..., alias='poolsUrl')
        chat_url: str = Field(..., alias='chatUrl')
        api_url: str = Field(..., alias='apiUrl')
        mongoose_bosh_host: str = Field(..., alias='mongooseBoshHost')
        mongoose_ws_host: str = Field(..., alias='mongooseWsHost')
        use_bosh: bool = Field(..., alias='useBosh')

    class Metrika(CustomBaseModel):
        user_id: str = Field(..., alias='userId')
        role: str
        source: Any
        page: str

    class UserExperiments(CustomBaseModel):
        survey: bool
        online_status: bool = Field(..., alias='onlineStatus')
        hide_ads: bool = Field(..., alias='hideAds')
        messenger_adaptive_journal: bool = Field(..., alias='messengerAdaptiveJournal')
        messenger_mongoose_archive: bool = Field(..., alias='messengerMongooseArchive')
        messenger_mongoose_notice: bool = Field(..., alias='messengerMongooseNotice')
        schools_in_custom_chats_experiment: list = Field(..., alias='schoolsInCustomChatsExperiment')

    class SchoolInfo(IdName):
        is_odo_school: bool = Field(..., alias='isOdoSchool')
        is_poo_school: bool = Field(..., alias='isPooSchool')

    user: User
    urls: Urls
    environment_prefix: str = Field(..., alias='environmentPrefix')
    metrika: Metrika
    attachment_host: list[str] = Field(..., alias='attachmentHost')
    inactive_tab_connection_timeout_seconds: int = Field(..., alias='inactiveTabConnectionTimeoutSeconds')
    inbox_polling_interval_seconds: int = Field(..., alias='inboxPollingIntervalSeconds')
    keep_alive_interval: int = Field(..., alias='keepAliveInterval')
    credentials_poll_interval: int = Field(..., alias='credentialsPollInterval')
    user_experiments: UserExperiments = Field(..., alias='userExperiments')
    unread_count: int = Field(..., alias='unreadCount')
    unread_roles: list = Field(..., alias='unreadRoles')
    roster_versioning_enabled: bool = Field(..., alias='rosterVersioningEnabled')
    roster_cache_ttl: int = Field(..., alias='rosterCacheTTL')
    message_statuses_enabled: bool = Field(..., alias='messageStatusesEnabled')
    show_app_links: bool = Field(..., alias='showAppLinks')
    zero_height: bool = Field(..., alias='zeroHeight')
    notice: Any
    schoolsInfo: list[SchoolInfo]


class MediaWidgetInitialState(CustomBaseModel):
    api_url: str = Field(..., alias='apiUrl')
    max_upload_file_size: int = Field(..., alias='maxUploadFileSize')
    max_upload_file_size_message: int = Field(..., alias='maxUploadFileSizeMessage')
    grid_preview_experiment: bool = Field(..., alias='gridPreviewExperiment')


class PublicClubsInitialState(CustomBaseModel):
    class Metrika(CustomBaseModel):
        page: str

    club_id: int = Field(..., alias='clubId')
    api_url: str = Field(..., alias='apiUrl')
    environment_prefix: str = Field(..., alias='environmentPrefix')
    default_background_image_url: str = Field(..., alias='defaultBackgroundImageUrl')
    metrika: Metrika


class ApiUrls(CustomBaseModel):
    feed: str
    posts: str
    user_link: str = Field(..., alias='userLink')
    analytics: str
    publicclub: str
    user_key_value_storage: str = Field(..., alias='userKeyValueStorage')
    polls_api_url: str = Field(..., alias='pollsApiUrl')
    ratings: str
    vuz: str
    domain: str


class ComplaintInitialState(CustomBaseModel):
    api_url: str = Field(..., alias='apiUrl')


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
    talk__initial__state: TalkInitialState = Field(..., alias='TALK__INITIAL__STATE')
    talk__stub__initial__state: str = Field(..., alias='TALK__STUB__INITIAL__STATE')
    media_widget__initial__state: MediaWidgetInitialState = Field(..., alias='MEDIA_WIDGET__INITIAL__STATE')
    public__clubs__initial__state: PublicClubsInitialState = Field(..., alias='PUBLIC__CLUBS__INITIAL__STATE')
    api_urls: ApiUrls = Field(..., alias='apiUrls')
    complaint__initial__state: ComplaintInitialState = Field(..., alias='COMPLAINT__INITIAL__STATE')
