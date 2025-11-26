class CaptchaError(Exception):
    pass


class CaptchaLoadError(CaptchaError):
    pass


class CaptchaVerifyError(CaptchaError):
    pass
