from flask import request


def form_get(arg, default=None):
    val = request.form.get(arg, default)
    if not val:
        raise KeyError(f'Form parameter {arg} is missing.')
    return val


def args_get(arg, default=None):
    val = request.args.get(arg, default)
    if not val:
        raise KeyError(f'Argument {arg} is missing.')
    return val
