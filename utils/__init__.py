class UserDataIsNoneError(Exception):
    pass

class IncorrectLoginOrPasswordError(Exception):
    pass


class TemporaryPasswordError(Exception):
    pass


class NotSubscribedError(Exception):
    pass

class CaptchaError(Exception):
    pass


class IncorrectUserCookieError(Exception):
    pass