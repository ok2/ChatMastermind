#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import yaml
import os
import io
import sys
import shutil
import openai
import pathlib
import argcomplete
import argparse
from pprint import PrettyPrinter
from typing import List, Dict, Any, Optional

terminal_size = shutil.get_terminal_size()
terminal_width = terminal_size.columns
pp = PrettyPrinter(width=terminal_width).pprint


def run_print_command(args: argparse.Namespace, config: dict) -> None:
    with open(args.print, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    pp(data)


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


def process_and_display_chat(args: argparse.Namespace,
                             config: dict,
                             dump: bool = False
                             ) -> tuple[list[dict[str, str]], list[str]]:
    tags = args.tags or []
    extags = args.extags or []
    process_tags(config, tags, extags)
    chat = create_chat(args.question, tags, extags, config)
    display_chat(chat, dump)
    return chat, tags


def display_chat(chat, dump=False) -> None:
    if dump:
        pp(chat)
        return
    for message in chat:
        if message['role'] == 'user':
            print('-' * terminal_width)
        if len(message['content']) > terminal_width-len(message['role'])-2:
            print(f"{message['role'].upper()}:")
            print(message['content'])
        else:
            print(f"{message['role'].upper()}: {message['content']}")


def handle_question(args: argparse.Namespace,
                    config: dict,
                    dump: bool = False
                    ) -> None:
    chat, tags = process_and_display_chat(args, config, dump)
    otags = args.output_tags or []
    answers, usage = ai(chat, config, args.number)
    save_answers(args.question, answers, tags, otags)
    print("-" * terminal_width)
    print(f"Usage: {usage}")


def save_answers(question: str,
                 answers: list[str],
                 tags: list[str],
                 otags: Optional[list[str]]
                 ) -> None:
    wtags = otags or tags
    for num, answer in enumerate(answers, start=1):
        title = f'-- ANSWER {num} '
        title_end = '-' * (terminal_width - len(title))
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


def main(args: argparse.Namespace) -> int:
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    openai.api_key = config['openai']['api_key']
    if args.max_tokens:
        config['openai']['max_tokens'] = args.max_tokens
    if args.temperature:
        config['openai']['temperature'] = args.temperature
    if args.model:
        config['openai']['model'] = args.model
    if args.print:
        run_print_command(args, config)
    elif args.question:
        handle_question(args, config)
    elif args.chat_dump:
        process_and_display_chat(args, config, dump=True)
    elif args.chat:
        process_and_display_chat(args, config)
    return 0


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


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description="Handle chats")
    default_config = '.config.yaml'
    group = args_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--print',
                       help='YAML file to print')
    group.add_argument('-q', '--question',
                       help='Question to ask')
    group.add_argument('-D', '--chat-dump',
                       help="Print chat as Python structure",
                       action='store_true')
    group.add_argument('-d', '--chat',
                       help="Print chat as readable text",
                       action='store_true')
    args_parser.add_argument('-c', '--config',
                             help='Config file name.',
                             default=default_config)
    args_parser.add_argument('-m', '--max-tokens',
                             help='Max tokens to use',
                             type=int)
    args_parser.add_argument('-T', '--temperature',
                             help='Temperature to use',
                             type=float)
    args_parser.add_argument('-M', '--model',
                             help='Model to use')
    args_parser.add_argument('-n', '--number',
                             help='Number of answers to produce',
                             type=int,
                             default=3)
    tags_arg = args_parser.add_argument(
        '-t', '--tags',
        nargs='*',
        help='List of tag names',
        metavar='TAGS')
    tags_arg.completer = tags_completer  # type: ignore
    extags_arg = args_parser.add_argument(
        '-e', '--extags',
        nargs='*',
        help='List of tag names to exclude',
        metavar='EXTAGS')
    extags_arg.completer = tags_completer  # type: ignore
    otags_arg = args_parser.add_argument(
        '-o', '--output-tags',
        nargs='*',
        help='List of output tag names, default is input',
        metavar='OTAGS')
    otags_arg.completer = tags_completer  # type: ignore
    argcomplete.autocomplete(args_parser)
    args = args_parser.parse_args()
    sys.exit(main(args))
