import shutil
from pprint import PrettyPrinter
from typing import List, Dict


def terminal_width() -> int:
    return shutil.get_terminal_size().columns


def pp(*args, **kwargs) -> None:
    return PrettyPrinter(width=terminal_width()).pprint(*args, **kwargs)


def process_tags(tags: list[str], extags: list[str], otags: list[str]) -> None:
    printed_messages = []

    if tags:
        printed_messages.append(f"Tags: {', '.join(tags)}")
    if extags:
        printed_messages.append(f"Excluding tags: {', '.join(extags)}")
    if otags:
        printed_messages.append(f"Output tags: {', '.join(otags)}")

    if printed_messages:
        print("\n".join(printed_messages))
        print()


def append_message(chat: List[Dict[str, str]],
                   role: str,
                   content: str
                   ) -> None:
    chat.append({'role': role, 'content': content.replace("''", "'")})


def message_to_chat(message: Dict[str, str],
                    chat: List[Dict[str, str]]
                    ) -> None:
    append_message(chat, 'user', message['question'])
    append_message(chat, 'assistant', message['answer'])


def display_chat(chat, dump=False) -> None:
    if dump:
        pp(chat)
        return
    for message in chat:
        if message['role'] == 'user':
            print('-' * (terminal_width()))
        if len(message['content']) > terminal_width() - len(message['role']) - 2:
            print(f"{message['role'].upper()}:")
            print(message['content'])
        else:
            print(f"{message['role'].upper()}: {message['content']}")
