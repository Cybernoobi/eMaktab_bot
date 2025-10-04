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


class _BasicCurrentChildInfo(_IdsInfo):
    has_schedule: bool = Field(..., alias='hasSchedule')
    school_type: str = Field(..., alias='schoolType')


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


class _BasicMarkInfo(BaseModel):
    id: str
    value: str
    mood: str


class _BasicWorkMarkInfo(BaseModel):
    work_id: str = Field(..., alias='workId')
    marks: list[_BasicMarkInfo]


class _BasicSubjectInfo(BaseModel):
    id: str
    name: str
    knowledge_area: str = Field(..., alias='knowledgeArea')


# __USER__START__PAGE__INITIAL__STATE__
class UserStartPageInitialState(BaseModel):
    class UserSchedule(BaseModel):
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

                        id: str
                        number: int
                        place: Any
                        start_time: datetime = Field(..., alias='startTime')
                        end_time: datetime = Field(..., alias='endTime')
                        hours: Hours
                        is_canceled: bool = Field(..., alias='isCanceled')
                        theme: str
                        meeting: Any
                        smart_work_info: Any = Field(..., alias='smartWorkInfo')
                        subject: _BasicSubjectInfo
                        important_works: list[str] = Field(..., alias='importantWorks')
                        homework: Homework | None
                        smart_homeworks: list[SmartHomework] | list = Field(..., alias='smartHomeworks')
                        has_attachment: bool = Field(..., alias='hasAttachment')
                        work_marks: list[_BasicWorkMarkInfo] | list = Field(..., alias='workMarks')
                        is_empty: bool = Field(..., alias='isEmpty')
                        comment: Any

                    date: datetime
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

        api_url: str = Field(..., alias='apiUrl')
        children: list[Child]
        current_child: _BasicCurrentChildInfo = Field(..., alias='currentChild')
        current_date: datetime = Field(..., alias='currentDate')

    class UserMarks(BaseModel):
        class Child(_IdsInfo):
            class Mark(_BasicWorkMarkInfo):
                class Subject(_BasicSubjectInfo):
                    subject_mood: Any = Field(..., alias='subjectMood')

                class Mark(_BasicMarkInfo):
                    max_value: None | str = Field(..., alias='maxValue')

                date: datetime
                lesson_date: datetime = Field(..., alias='lessonDate')
                subject: Subject
                mark_type: str = Field(..., alias='markType')
                mark_type_text: str = Field(..., alias='markTypeText')
                short_mark_type_text: str = Field(..., alias='shortMarkTypeText')
                is_final: bool = Field(..., alias='isFinal')
                marks: list[Mark]
                number: int
                period_id: str = Field(..., alias='periodId')
                section_id: str = Field(..., alias='sectionId')
                analytics_period: Any = Field(..., alias='analyticsPeriod')

            ratings_marks_info: Any = Field(..., alias='ratingsMarksInfo')
            marks: list[Mark]
            marks_indicators: list = Field(..., alias='marksIndicators')

        children: list[Child]
        current_child: _BasicCurrentChildInfo = Field(..., alias='currentChild')

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


# __TALK__INITIAL__STATE__
class TalkInitialState(BaseModel):
    class User(BaseModel):
        avatar_large: str = Field(..., alias='avatarLarge')
        irrelevant: bool
        created: bool
        sex: str
        is_system: bool = Field(..., alias='isSystem')
        school_name: Any = Field(..., alias='schoolName')
        class_teacher: Any = Field(..., alias='classTeacher')
        chat_type: str = Field(..., alias='chatType')
        school_id: str = Field(..., alias='schoolId')
        is_archive_contact: bool = Field(..., alias='isArchiveContact')
        affiliations: Any
        is_poo_school: bool = Field(..., alias='isPooSchool')
        is_odo_school: bool = Field(..., alias='isOdoSchool')
        jid: str
        type: str
        name: str
        short_name: str = Field(..., alias='shortName')
        avatar: str
        avatar_background: Any = Field(..., alias='avatarBackground')
        unknown: bool
        roles: list[str]
        school_ids: list[str] = Field(..., alias='schoolIds')
        groups: dict[str, Any]
        teacher_groups: dict[str, Any] = Field(..., alias='teacherGroups')
        class_teacher_groups: list = Field(..., alias='classTeacherGroups')
        subjects: Any
        profile_url: str = Field(..., alias='profileUrl')
        is_dnevnik_expert: bool = Field(..., alias='isDnevnikExpert')

    class Urls(BaseModel):
        messenger_url: str = Field(..., alias='messengerUrl')
        favicon_url: str = Field(..., alias='faviconUrl')
        messenger_favicon_url: str = Field(..., alias='messengerFaviconUrl')
        return_url: str = Field(..., alias='returnUrl')
        logo_url: str = Field(..., alias='logoUrl')
        terms_url: str = Field(..., alias='termsUrl')
        host: str
        multi_user_chat_host: str = Field(..., alias='multiUserChatHost')
        feedback_url: str = Field(..., alias='feedbackUrl')
        async_task_api_url: str = Field(..., alias='asyncTaskApiUrl')
        custom_chats_avatars_url: str = Field(..., alias='customChatsAvatarsUrl')
        messenger_archive: Any = Field(..., alias='messengerArchive')
        polls_api_url: str = Field(..., alias='pollsApiUrl')
        polls_url: str = Field(..., alias='pollsUrl')
        chat_url: str = Field(..., alias='chatUrl')
        api_url: str = Field(..., alias='apiUrl')
        mongoose_bosh_host: str = Field(..., alias='mongooseBoshHost')
        mongoose_ws_host: str = Field(..., alias='mongooseWSHost')
        use_bosh: bool = Field(..., alias='useBosh')

    class Metrika(BaseModel):
        user_id: str = Field(..., alias='userId')
        role: str
        source: Any
        page: str

    class UserExperiments(BaseModel):
        survey: bool
        online_status: bool = Field(..., alias='onlineStatus')
        hide_ads: bool = Field(..., alias='hideAds')
        messenger_adaptive_journal: bool = Field(..., alias='messengerAdaptiveJournal')
        messenger_mongoose_archive: bool = Field(..., alias='messengerMongooseArchive')
        messenger_mongoose_notice: bool = Field(..., alias='messengerMongooseNotice')
        schools_in_custom_chats_experiment: list = Field(
            ..., alias='schoolsInCustomChatsExperiment'
        )

    class SchoolsInfoItem(BaseModel):
        id: str
        name: str
        is_odo_school: bool = Field(..., alias='isOdoSchool')
        is_poo_school: bool = Field(..., alias='isPooSchool')

    user: User
    urls: Urls
    environment_prefix: str = Field(..., alias='environmentPrefix')
    metrika: Metrika
    attachment_hosts: list[str] = Field(..., alias='attachmentHosts')
    inactive_tab_connection_timeout_seconds: int = Field(
        ..., alias='inactiveTabConnectionTimeoutSeconds'
    )
    inbox_polling_interval_seconds: int = Field(
        ..., alias='inboxPollingIntervalSeconds'
    )
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
    schools_info: list[SchoolsInfoItem] = Field(..., alias='schoolsInfo')


# __MEDIA_WIDGET__INITIAL__STATE__
class MediaWidgetInitialState(BaseModel):
    api_url: str = Field(..., alias='apiUrl')
    max_upload_file_size: str = Field(..., alias='maxUploadFileSize')
    max_upload_file_size_message: str = Field(..., alias='maxUploadFileSizeMessage')
    grid_preview_experiment: bool = Field(..., alias='gridPreviewExperiment')


# __PUBLIC__CLUBS__INITIAL__STATE__
class PublicClubsInitialState(BaseModel):
    class Metrika(BaseModel):
        page: str

    club_id: Any = Field(..., alias='clubId')
    api_url: str = Field(..., alias='apiUrl')
    environment_prefix: str = Field(..., alias='environmentPrefix')
    default_background_image_url: str = Field(..., alias='defaultBackgroundImageUrl')
    metrika: Metrika


# apiUrls
class ApiUrls(BaseModel):
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


# __WORKS__INITIAL__STATE__
class WorksInitialState(BaseModel):
    api_url: str = Field(..., alias='apiUrl')
    smart_url: str = Field(..., alias='smartUrl')


# __COMPLAINT__INITIAL__STATE__
class ComplaintInitialState(BaseModel):
    api_url: str = Field(..., alias='apiUrl')


# __ALL__INITIAL__STATES__
class EUserAllInitialStates(BaseModel):
    survey_form: SurveyFormInitialState = Field(..., alias='__SURVEY_FORM_INITIAL_STATE__')
    mom_said_yes: MomSaidYesInitialState = Field(..., alias='__MOM_SAID_YES__INITIAL__STATE__')
    user_start_page: UserStartPageInitialState = Field(..., alias='__USER__START__PAGE__INITIAL__STATE__')
    talk: TalkInitialState = Field(..., alias='__TALK__INITIAL__STATE__')
    talk_stub: str = Field(..., alias='__TALK__STUB__INITIAL__STATE__')
    media_widget: MediaWidgetInitialState = Field(..., alias='__MEDIA_WIDGET__INITIAL__STATE__')
    public_clubs: PublicClubsInitialState = Field(..., alias='__PUBLIC__CLUBS__INITIAL__STATE__')
    api_urls: ApiUrls = Field(..., alias='apiUrls')
    works: WorksInitialState = Field(..., alias='__WORKS__INITIAL__STATE__')
    complaint: ComplaintInitialState = Field(..., alias='__COMPLAINT__INITIAL__STATE__')
