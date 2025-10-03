import re

from aiohttp import ClientResponse


def check_url(url: str, https: bool = True) -> str:
    if url.split("//")[0] in ["http", "https"]:
        return url

    if https:
        return "https://" + url
    return "http://" + url


def search_cookie(response: ClientResponse, cookie_key: str) -> str | None:
    for history in response.history:
        if cookie_key in history.cookies:
            return history.cookies.get(cookie_key).value


def extract_js_vars_to_json(code) -> str:
    """Извлекает переменные window.* = { ... } или window.* = "..." и преобразует их в JSON."""
    code = r"{[code]}".replace("[code]", code)

    # 1. Объединение многострочных присвоений в одну строку (упрощение)
    code = code.replace('\n', ' ')

    # 2. Удаление функций
    regex = r'(window\.__COMPLAINT__INITIAL__STATE__.*?;\s*)[\s\S]*'
    replacement = r'\1'
    code = re.sub(regex, replacement, code, flags=re.DOTALL)

    # 3. Очистка сложных фрагментов, которые сломают парсер
    # удаляем оператор spread, так как его нельзя парсить как JSON
    code = code.replace(r'...window.apiUrls,', '')

    # 4. Поиска всех присвоений window.__*
    # Находим все window.__ и меням их на "__
    code = code.replace("window.__", '"__').replace("__ =", '__":')

    # 5. Меням ; на ,
    code = code.replace("};", "},").replace('" ', '",')
    code = code.replace("window.apiUrls =", ', "apiUrls":')

    # Регулярное выражение (ищет ключи с отступом в начале строки)
    API_URLS_REGEX = re.compile(
        r'(\"apiUrls\"|\bapiUrls)\s*:\s*\{([\s\S]*?)(\}\s*[,]?\s*)',
        re.DOTALL
    )

    def quote_keys_in_match(match_obj):
        """
        Функция, которая будет вызвана для каждого совпадения MAIN_REGEX.
        Она берет содержимое блока apiUrls (Группа 2) и квотирует его ключи.
        """
        # match_obj.group(1): Префикс ("apiUrls" или apiUrls)
        # match_obj.group(2): Содержимое блока apiUrls
        # match_obj.group(3): Суффикс (}; или } или },)

        prefix = match_obj.group(1)  # + match_obj.group(3)  # Объединяем "apiUrls" и ": {"
        content = match_obj.group(2)
        # suffix = match_obj.group(4)

        # Применяем KEY_QUOTING_REGEX к содержимому блока (content)
        # Замена: \1 - пробел (отступ), "\2" - ключ в кавычках, : - двоеточие
        # quoted_content = KEY_QUOTING_REGEX.sub(r'\1"\2":', content)

        # Регулярное выражение для поиска ключей: (\s+)([a-zA-Z_][\w]*)\s*:
        regex = r'(\s+)([a-zA-Z_][\w]*)\s*:'

        # Замена: \1 (отступ) + " + \2 (ключ) + " + :
        replacement = r'\1"\2":'

        # Выполняем замену с флагом re.MULTILINE для обработки каждой строки
        quoted_content = re.sub(regex, replacement, content)

        # Снова собираем весь блок
        # + suffix
        res = '[prefix]: {'.replace('[prefix]', prefix) + quoted_content + "},"
        # print(res)
        return res

    # Выполняем замену:
    # Я применил эту логику к js_code_with_apiUrls, чтобы показать, как она работает с Вашим исходным кодом.
    code = API_URLS_REGEX.sub(quote_keys_in_match, code)

    # __WORKS__INITIAL__STATE__
    WORKS__INITIAL__STATE_REGEX = re.compile(
        r'(\"__WORKS__INITIAL__STATE__\"|\__WORKS__INITIAL__STATE__)\s*:\s*\{([\s\S]*?)(\}\s*[,]?\s*)',
        re.DOTALL
    )
    code = WORKS__INITIAL__STATE_REGEX.sub(quote_keys_in_match, code)
    code = code.replace("    ", "").strip()
    code = code.replace(",}", "}")

    code = code[:3].replace(" ", "") + code[3:-1].replace(", }", "}") + "}"

    return code
