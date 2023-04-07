import shutil
import yaml
import pathlib
from pprint import PrettyPrinter
from typing import List, Dict


def terminal_width() -> int:
    return shutil.get_terminal_size().columns


def pp(*args, **kwargs) -> None:
    return PrettyPrinter(width=terminal_width()).pprint(*args, **kwargs)


def process_tags(config: dict, tags: list, extags: list) -> None:
    print(f"Tags: {', '.join(tags)}")
    if len(extags) > 0:
        print(f"Excluding tags: {', '.join(extags)}")
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


def tags_completer(prefix, parsed_args, **kwargs):
    with open(parsed_args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    result = []
    for file in sorted(pathlib.Path(config['db']).iterdir()):
        if file.suffix == '.yaml':
            with open(file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            for tag in data.get('tags', []):
                if prefix and len(prefix) > 0:
                    if tag.startswith(prefix):
                        result.append(tag)
                else:
                    result.append(tag)
    return list(set(result))
