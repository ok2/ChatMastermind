#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import yaml
import sys
import argcomplete
import argparse
from .utils import terminal_width, pp, process_tags, display_chat
from .storage import save_answers, create_chat, get_tags
from .api_client import ai, openai_api_key


def run_print_command(args: argparse.Namespace, config: dict) -> None:
    with open(args.print, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    pp(data)


def process_and_display_chat(args: argparse.Namespace,
                             config: dict,
                             dump: bool = False
                             ) -> tuple[list[dict[str, str]], str, list[str]]:
    tags = args.tags or []
    extags = args.extags or []
    otags = args.output_tags or []
    process_tags(tags, extags, otags)

    question_parts = []
    question_list = args.question if args.question is not None else []
    source_list = args.source if args.source is not None else []

    for question, source in zip(question_list, source_list):
        with open(source) as r:
            question_parts.append(f"{question}\n\n```\n{r.read().strip()}\n```")

    if len(question_list) > len(source_list):
        for question in question_list[len(source_list):]:
            question_parts.append(question)
    else:
        for source in source_list[len(question_list):]:
            with open(source) as r:
                question_parts.append(f"```\n{r.read().strip()}\n```")

    question = '\n\n'.join(question_parts)

    chat = create_chat(question, tags, extags, config)
    display_chat(chat, dump)
    return chat, question, tags


def handle_question(args: argparse.Namespace,
                    config: dict,
                    dump: bool = False
                    ) -> None:
    chat, question, tags = process_and_display_chat(args, config, dump)
    otags = args.output_tags or []
    answers, usage = ai(chat, config, args.number)
    save_answers(question, answers, tags, otags)
    print("-" * terminal_width())
    print(f"Usage: {usage}")


def tags_completer(prefix, parsed_args, **kwargs):
    with open(parsed_args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return get_tags(config, prefix)


def create_parser() -> argparse.ArgumentParser:
    default_config = '.config.yaml'
    parser = argparse.ArgumentParser(
        description="ChatMastermind is a Python application that automates conversation with AI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--print', help='YAML file to print')
    group.add_argument('-q', '--question', nargs='*', help='Question to ask')
    group.add_argument('-D', '--chat-dump', help="Print chat as Python structure", action='store_true')
    group.add_argument('-d', '--chat', help="Print chat as readable text", action='store_true')
    parser.add_argument('-c', '--config', help='Config file name.', default=default_config)
    parser.add_argument('-m', '--max-tokens', help='Max tokens to use', type=int)
    parser.add_argument('-T', '--temperature', help='Temperature to use', type=float)
    parser.add_argument('-M', '--model', help='Model to use')
    parser.add_argument('-n', '--number', help='Number of answers to produce', type=int, default=3)
    parser.add_argument('-s', '--source', nargs='*', help='Source add content of a file to the query')
    tags_arg = parser.add_argument('-t', '--tags', nargs='*', help='List of tag names', metavar='TAGS')
    tags_arg.completer = tags_completer  # type: ignore
    extags_arg = parser.add_argument('-e', '--extags', nargs='*', help='List of tag names to exclude', metavar='EXTAGS')
    extags_arg.completer = tags_completer  # type: ignore
    otags_arg = parser.add_argument('-o', '--output-tags', nargs='*', help='List of output tag names, default is input', metavar='OTAGS')
    otags_arg.completer = tags_completer  # type: ignore
    argcomplete.autocomplete(parser)
    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    openai_api_key(config['openai']['api_key'])

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


if __name__ == '__main__':
    sys.exit(main())
