TAGS_ALLOWED = []
TAGS_REQUIRED = []

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass
