__author__ = 'yakupadakli'


from django.contrib.auth.decorators import user_passes_test
from django.conf import settings


def anonymous_required(function=None, redirect_url=None):
    """
        This decorator is that if
        page is need to anonymous person, so
        person who logged in does not have to see these page
    :param function:
    :param redirect_url:
    :return:
    """
    if not redirect_url:
        redirect_url = settings.LOGIN_REDIRECT_URL

    decorator = user_passes_test(
        lambda u: u.is_anonymous(),
        login_url=redirect_url
    )

    if function:
        return decorator(function)
    return decorator