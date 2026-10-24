from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("login")

            if request.user.role not in roles:
                messages.error(
                    request,
                    "You do not have permission to access this page."
                )
                return redirect("dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator