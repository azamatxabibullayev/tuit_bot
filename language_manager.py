user_languages = {}


def get_language(user_id: int) -> str:
    return user_languages.get(user_id, None)


def set_language(user_id: int, lang: str):
    user_languages[user_id] = lang
