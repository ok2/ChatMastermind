import unittest
import io
import os
import yaml
import argparse
from chatmastermind.utils import terminal_width
from chatmastermind.main import create_parser, handle_question
from chatmastermind.api_client import ai
from chatmastermind.storage import create_chat, save_answers
from unittest import mock
from unittest.mock import patch, MagicMock, Mock


class TestCreateChat(unittest.TestCase):

    def setUp(self):
        self.config = {
            'system': 'System text',
            'db': 'test_files'
        }
        self.question = "test question"
        self.tags = ['test_tag']

    @patch('os.listdir')
    @patch('builtins.open')
    def test_create_chat_with_tags(self, open_mock, listdir_mock):
        listdir_mock.return_value = ['testfile.yaml']
        open_mock.return_value.__enter__.return_value = io.StringIO(yaml.dump(
            {'question': 'test_content', 'answer': 'some answer',
             'tags': ['test_tag']}))

        test_chat = create_chat(self.question, self.tags, None, self.config)

        self.assertEqual(len(test_chat), 4)
        self.assertEqual(test_chat[0],
                         {'role': 'system', 'content': self.config['system']})
        self.assertEqual(test_chat[1],
                         {'role': 'user', 'content': 'test_content'})
        self.assertEqual(test_chat[2],
                         {'role': 'assistant', 'content': 'some answer'})
        self.assertEqual(test_chat[3],
                         {'role': 'user', 'content': self.question})

    @patch('os.listdir')
    @patch('builtins.open')
    def test_create_chat_with_other_tags(self, open_mock, listdir_mock):
        listdir_mock.return_value = ['testfile.yaml']
        open_mock.return_value.__enter__.return_value = io.StringIO(yaml.dump(
            {'question': 'test_content', 'answer': 'some answer',
             'tags': ['other_tag']}))

        test_chat = create_chat(self.question, self.tags, None, self.config)

        self.assertEqual(len(test_chat), 2)
        self.assertEqual(test_chat[0],
                         {'role': 'system', 'content': self.config['system']})
        self.assertEqual(test_chat[1],
                         {'role': 'user', 'content': self.question})

    @patch('os.listdir')
    @patch('builtins.open')
    def test_create_chat_without_tags(self, open_mock, listdir_mock):
        listdir_mock.return_value = ['testfile.yaml', 'testfile2.yaml']
        open_mock.side_effect = (
            io.StringIO(yaml.dump({'question': 'test_content',
                                   'answer': 'some answer',
                                   'tags': ['test_tag']})),
            io.StringIO(yaml.dump({'question': 'test_content2',
                                   'answer': 'some answer2',
                                   'tags': ['test_tag2']})),
        )

        test_chat = create_chat(self.question, [], None, self.config)

        self.assertEqual(len(test_chat), 6)
        self.assertEqual(test_chat[0],
                         {'role': 'system', 'content': self.config['system']})
        self.assertEqual(test_chat[1],
                         {'role': 'user', 'content': 'test_content'})
        self.assertEqual(test_chat[2],
                         {'role': 'assistant', 'content': 'some answer'})
        self.assertEqual(test_chat[3],
                         {'role': 'user', 'content': 'test_content2'})
        self.assertEqual(test_chat[4],
                         {'role': 'assistant', 'content': 'some answer2'})


class TestHandleQuestion(unittest.TestCase):

    def setUp(self):
        self.question = "test question"
        self.args = argparse.Namespace(
            tags=['tag1'],
            extags=['extag1'],
            output_tags=None,
            question=[self.question],
            source=None,
            number=3
        )
        self.config = {
            'setting1': 'value1',
            'setting2': 'value2'
        }

    @patch("chatmastermind.main.create_chat", return_value="test_chat")
    @patch("chatmastermind.main.process_tags")
    @patch("chatmastermind.main.ai", return_value=(["answer1", "answer2", "answer3"], "test_usage"))
    @patch("chatmastermind.utils.pp")
    @patch("builtins.print")
    @patch("chatmastermind.storage.yaml.dump")
    def test_handle_question(self, _, mock_print, mock_pp, mock_ai,
                             mock_process_tags, mock_create_chat):
        open_mock = MagicMock()
        with patch("chatmastermind.storage.open", open_mock):
            handle_question(self.args, self.config, True)
            mock_process_tags.assert_called_once_with(self.args.tags,
                                                      self.args.extags,
                                                      [])
            mock_create_chat.assert_called_once_with(self.question,
                                                     self.args.tags,
                                                     self.args.extags,
                                                     self.config)
            mock_pp.assert_called_once_with("test_chat")
            mock_ai.assert_called_with("test_chat",
                                       self.config,
                                       self.args.number)
            expected_calls = []
            for num, answer in enumerate(mock_ai.return_value[0], start=1):
                title = f'-- ANSWER {num} '
                title_end = '-' * (terminal_width() - len(title))
                expected_calls.append(((f'{title}{title_end}',),))
                expected_calls.append(((answer,),))
            expected_calls.append((("-" * terminal_width(),),))
            expected_calls.append(((f"Usage: {mock_ai.return_value[1]}",),))
            open_mock.assert_has_calls(
                [mock.call(f"{num:02d}.yaml", "w") for num in range(1, 4)] + [
                    mock.call().__enter__(), mock.call().__exit__(None, None, None)] * 3,
                any_order=True)
            self.assertEqual(mock_print.call_args_list, expected_calls)


class TestSaveAnswers(unittest.TestCase):

    def setUp(self):
        self.question = "What is AI?"
        self.answers = ["AI is Artificial Intelligence",
                        "AI is a simulation of human intelligence"]
        self.tags = ["ai", "definition"]

    @patch('sys.stdout', new_callable=io.StringIO)
    def assert_stdout(self, expected_output: str, mock_stdout: io.StringIO):
        save_answers(self.question, self.answers, self.tags, None)
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    def test_save_answers(self):
        try:
            self.assert_stdout(f"-- ANSWER 1 {'-'*(terminal_width()-12)}\n"
                               "AI is Artificial Intelligence\n"
                               f"-- ANSWER 2 {'-'*(terminal_width()-12)}\n"
                               "AI is a simulation of human intelligence\n")
            for idx, answer in enumerate(self.answers, start=1):
                with open(f"{idx:02d}.yaml", "r") as file:
                    data = yaml.safe_load(file)
                    self.assertEqual(data["question"], self.question)
                    self.assertEqual(data["answer"], answer)
                    self.assertEqual(data["tags"], self.tags)
        finally:
            for idx in range(1, len(self.answers) + 1):
                if os.path.exists(f"{idx:02d}.yaml"):
                    os.remove(f"{idx:02d}.yaml")


class TestAI(unittest.TestCase):

    @patch("openai.ChatCompletion.create")
    def test_ai(self, mock_create: MagicMock):
        mock_create.return_value = {
            'choices': [
                {'message': {'content': 'response_text_1'}},
                {'message': {'content': 'response_text_2'}}
            ],
            'usage': {'tokens': 10}
        }

        number = 2
        chat = [{"role": "system", "content": "hello ai"}]
        config = {
            "openai": {
                "model": "text-davinci-002",
                "temperature": 0.5,
                "max_tokens": 150,
                "top_p": 1,
                "n": number,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
        }

        result = ai(chat, config, number)
        expected_result = (['response_text_1', 'response_text_2'],
                           {'tokens': 10})
        self.assertEqual(result, expected_result)


class TestCreateParser(unittest.TestCase):
    def test_create_parser(self):
        with patch('argparse.ArgumentParser.add_mutually_exclusive_group') as mock_add_mutually_exclusive_group:
            mock_group = Mock()
            mock_add_mutually_exclusive_group.return_value = mock_group
            parser = create_parser()
            self.assertIsInstance(parser, argparse.ArgumentParser)
            mock_add_mutually_exclusive_group.assert_called_once_with(required=True)
            mock_group.add_argument.assert_any_call('-p', '--print', help='YAML file to print')
            mock_group.add_argument.assert_any_call('-q', '--question', nargs='*', help='Question to ask')
            mock_group.add_argument.assert_any_call('-D', '--chat-dump', help="Print chat as Python structure", action='store_true')
            mock_group.add_argument.assert_any_call('-d', '--chat', help="Print chat as readable text", action='store_true')
            self.assertTrue('.config.yaml' in parser.get_default('config'))
            self.assertEqual(parser.get_default('number'), 3)
