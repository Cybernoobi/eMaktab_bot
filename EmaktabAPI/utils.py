import re

from aiohttp import ClientResponse
import ujson

from .schemas import EFullInfoSchema


def check_url(url: str, https: bool = True) -> str:
    if url.split("//")[0] in ["http", "https"]:
        return url

    if https:
        return "https://" + url
    return "http://" + url


def search_cookie(response: ClientResponse, cookie_key: str) -> str:
    for history in response.history:
        if cookie_key in history.cookies:
            return history.cookies.get(cookie_key).value


def full_info_to_class(full_info: str):  # -> EFullInfoSchema
    spl = '#'*20

    cleaned_text = re.sub(r'\.\.\.window\.apiUrls,', '', full_info)
    cleaned_text = re.sub(r'(\w+):', r'"\1":', cleaned_text)

    if survey_match := re.search(r'__SURVEY_FORM_INITIAL_STATE__\s*=\s*({.*?});', full_info):
        survey_dict = ujson.loads(survey_match.group(1))
        # print(f"survey_dict: {survey_dict} \n{spl}\n")

    if mom_match := re.search(r'__MOM_SAID_YES__INITIAL__STATE__\s*=\s*({.*?});', full_info):
        mom_dict = ujson.loads(mom_match.group(1))
        # print(f"mom_dict: {mom_dict} \n{spl}\n")

    if user_start_page_match := re.search(r'__USER__START__PAGE__INITIAL__STATE__\s*=\s*({.*?});', full_info):
        user_start_page_dict = ujson.loads(user_start_page_match.group(1))
        # print(f"user_start_page_dict: {user_start_page_dict} \n{spl}\n")

    if talk_match := re.search(r'__TALK__INITIAL__STATE__\s*=\s*({.*?});', full_info):
        talk_dict = ujson.loads(talk_match.group(1))
        print(f"talk_dict: {talk_dict} \n{spl}\n")

    if talk_stub_match := re.search(r'__TALK__STUB__INITIAL__STATE__\s*=\s*.*?\"(.*)\"', full_info):
        talk_stub_str = talk_stub_match.group(1)
        print(f"talk_stub_str: {talk_stub_str} \n{spl}\n")

    if media_widget_match := re.search(r'__MEDIA_WIDGET__INITIAL__STATE__\s*=\s*({.*?});', full_info):
        media_widget_dict = ujson.loads(media_widget_match.group(1))
        print(f"media_widget_dict: {media_widget_dict} \n{spl}\n")

    if public_clubs_match := re.search(r'__PUBLIC__CLUBS__INITIAL__STATE__\s*=\s*({.*?}})', full_info):
        public_clubs_dict = ujson.loads(public_clubs_match.group(1))
        print(f"public_clubs_dict: {public_clubs_dict} \n{spl}\n")

    if api_urls_match := re.search(r'apiUrls\s*=\s*({[\s\S]*?})', cleaned_text):
        print(api_urls_match.group(1))
        # api_urls_dict = ujson.loads(api_urls_match.group(1))
        # print(f"api_urls_dict: {api_urls_dict} \n{spl}\n")

    if complaint_match := re.search(r'__COMPLAINT__INITIAL__STATE__\s*=\s*({.*?});', full_info):
        complaint_dict = ujson.loads(complaint_match.group(1))
        print(f"complaint_dict: {complaint_dict} \n{spl}\n")
