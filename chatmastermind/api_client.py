import openai


def openai_api_key(api_key: str) -> None:
    openai.api_key = api_key


def ai(chat: list[dict[str, str]],
       config: dict,
       number: int
       ) -> tuple[list[str], dict[str, int]]:
    response = openai.ChatCompletion.create(
        model=config['openai']['model'],
        messages=chat,
        temperature=config['openai']['temperature'],
        max_tokens=config['openai']['max_tokens'],
        top_p=config['openai']['top_p'],
        n=number,
        frequency_penalty=config['openai']['frequency_penalty'],
        presence_penalty=config['openai']['presence_penalty'])
    result = []
    for choice in response['choices']:  # type: ignore
        result.append(choice['message']['content'].strip())
    return result, dict(response['usage'])  # type: ignore
