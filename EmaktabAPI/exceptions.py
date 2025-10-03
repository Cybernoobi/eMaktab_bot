class ClientNotInTeacher(Exception):
    pass


class InvalidLoginOrPassword(Exception):
    pass


class BadStatusCode(Exception):
    pass


class TeacherPermissionDenied(Exception):
    pass


class NoAuth(Exception):
    pass


class UnknownError(Exception):
    pass