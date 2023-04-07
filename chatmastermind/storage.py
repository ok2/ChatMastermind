import yaml
import io
import pathlib
from .utils import terminal_width, append_message, message_to_chat
from typing import List, Dict, Any, Optional


def save_answers(question: str,
                 answers: list[str],
                 tags: list[str],
                 otags: Optional[list[str]]
                 ) -> None:
    wtags = otags or tags
    for num, answer in enumerate(answers, start=1):
        title = f'-- ANSWER {num} '
        title_end = '-' * (terminal_width() - len(title))
        print(f'{title}{title_end}')
        print(answer)
        with open(f"{num:02d}.yaml", "w") as fd:
            with io.StringIO() as f:
                yaml.dump({'question': question},
                          f,
                          default_style="|",
                          default_flow_style=False)
                fd.write(f.getvalue().replace('"question":', "question:", 1))
            with io.StringIO() as f:
                yaml.dump({'answer': answer},
                          f,
                          default_style="|",
                          default_flow_style=False)
                fd.write(f.getvalue().replace('"answer":', "answer:", 1))
            yaml.dump({'tags': wtags},
                      fd,
                      default_flow_style=False)


def create_chat(question: Optional[str],
                tags: Optional[List[str]],
                extags: Optional[List[str]],
                config: Dict[str, Any]
                ) -> List[Dict[str, str]]:
    chat = []
    append_message(chat, 'system', config['system'].strip())
    for file in sorted(pathlib.Path(config['db']).iterdir()):
        if file.suffix == '.yaml':
            with open(file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            data_tags = set(data.get('tags', []))
            tags_match = \
                not tags or data_tags.intersection(tags)
            extags_do_not_match = \
                not extags or not data_tags.intersection(extags)
            if tags_match and extags_do_not_match:
                message_to_chat(data, chat)
    if question:
        append_message(chat, 'user', question)
    return chat


def get_tags(config: Dict[str, Any], prefix: Optional[str]) -> List[str]:
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
