def check_url(url: str, https: bool = True) -> str:
    if url.split("//")[0] in ["http", "https"]:
        return url

    if https:
        return "https://" + url
    return "http://" + url

