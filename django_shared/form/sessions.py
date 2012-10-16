from django.core.context_processors import request

def getFormFromSession(request, forms, name, initial=None):
    form = request.session.get(name, False)

    if form:
        del request.session[name]
    else:
        if initial:
            form = getattr(forms, name)(initial=initial)
        else:
            form = getattr(forms, name)()

    return form