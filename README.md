# ChatMastermind

ChatMastermind is a Python application that automates conversation with AI, stores question-answer pairs with tags, and composes relevant chat history for the next question.

The project uses the OpenAI API to generate responses and stores the data in YAML files. It also allows you to filter chat history based on tags and supports autocompletion for tags.

## Requirements

- Python 3.6 or higher
- openai
- PyYAML
- argcomplete

You can install these requirements using `pip`:

```bash
pip install -r requirements.txt
```

## Installation

You can install the package with the requirements using `pip`:

```bash
pip install .
```

## Usage

```bash
cmm [-h] [-p PRINT | -q QUESTION | -D | -d] [-c CONFIG] [-m MAX_TOKENS] [-T TEMPERATURE] [-M MODEL] [-n NUMBER] [-t [TAGS [TAGS ...]]] [-e [EXTAGS [EXTAGS ...]]] [-o [OTAGS [OTAGS ...]]]
```

### Arguments

- `-p`, `--print`: YAML file to print.
- `-q`, `--question`: Question to ask.
- `-D`, `--chat-dump`: Print chat as a Python structure.
- `-d`, `--chat`: Print chat as readable text.
- `-c`, `--config`: Config file name (defaults to `.config.yaml`).
- `-m`, `--max-tokens`: Max tokens to use.
- `-T`, `--temperature`: Temperature to use.
- `-M`, `--model`: Model to use.
- `-n`, `--number`: Number of answers to produce (default is 3).
- `-t`, `--tags`: List of tag names.
- `-e`, `--extags`: List of tag names to exclude.
- `-o`, `--output-tags`: List of output tag names (default is the input tags).

### Examples

1. Print the contents of a YAML file:

```bash
cmm -p example.yaml
```

2. Ask a question:

```bash
cmm -q "What is the meaning of life?" -t philosophy -e religion
```

3. Display the chat history as a Python structure:

```bash
cmm -D
```

4. Display the chat history as readable text:

```bash
cmm -d
```

5. Filter chat history by tags:

```bash
cmm -d -t tag1 tag2
```

6. Exclude chat history by tags:

```bash
cmm -d -e tag3 tag4
```

## Configuration

The configuration file (`.config.yaml`) should contain the following fields:

- `openai`:
  - `api_key`: Your OpenAI API key.
  - `model`: The name of the OpenAI model to use (e.g. "text-davinci-002").
  - `temperature`: The temperature value for the model.
  - `max_tokens`: The maximum number of tokens for the model.
  - `top_p`: The top P value for the model.
  - `frequency_penalty`: The frequency penalty value.
  - `presence_penalty`: The presence penalty value.
- `system`: The system message used to set the behavior of the AI.
- `db`: The directory where the question-answer pairs are stored in YAML files.

## Autocompletion

To activate autocompletion for tags, add the following line to your shell's configuration file (e.g., `.bashrc`, `.zshrc`, or `.profile`):

```bash
eval "$(register-python-argcomplete cmm)"
```

After adding this line, restart your shell or run `source <your-shell-config-file>` to enable autocompletion for the `cmm` script.

## License

This project is licensed under the terms of the WTFPL License.