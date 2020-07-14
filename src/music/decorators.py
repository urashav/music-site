from django.http import HttpResponseForbidden

def restful(method):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.method.upper() == method.upper():
                return func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('403 Forbidden')
        return wrapper
    return decorator