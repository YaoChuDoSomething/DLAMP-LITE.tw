"""A command-line interface for interacting with Ollama models.

This script provides a simple way to list, prompt, and chat with AI models
served by an Ollama instance.

Usage:
    python ollama_cli.py list
    python ollama_cli.py prompt <model_name> "Your prompt here"
    python ollama_cli.py chat <model_name>
"""

import argparse
import sys

try:
    import ollama
except ImportError:
    print(
        "The 'ollama' library is not installed.",
        "Please install it with 'pip install ollama'",
        file=sys.stderr,
    )
    sys.exit(1)


def handle_errors(func):
    """A decorator to handle common API errors."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ollama.ResponseError as e:
            model_name = kwargs.get("model") or (
                args[0] if args else "unknown"
            )
            print(f"Error: {e.error}", file=sys.stderr)
            if e.status_code == 404:
                print(
                    f"Model '{model_name}' not found. "
                    f"Pull it first with 'ollama pull {model_name}'",
                    file=sys.stderr,
                )
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            sys.exit(1)

    return wrapper


@handle_errors
def list_models():
    """Lists available Ollama models."""
    models = ollama.list()["models"]
    if not models:
        print("No models found. Pull a model with 'ollama pull <model_name>'")
        return
    print("Available models:")
    for model in models:
        print(f"- {model['name']}")


@handle_errors
def prompt_model(model, prompt_text, stream):
    """Sends a single prompt to a model."""
    if not prompt_text:
        if sys.stdin.isatty():
            print("Enter your prompt (press Ctrl+D to send):")
        prompt_text = sys.stdin.read().strip()
        if not prompt_text:
            print("Error: Prompt cannot be empty.", file=sys.stderr)
            return

    if stream:
        response_stream = ollama.generate(
            model=model, prompt=prompt_text, stream=True
        )
        for chunk in response_stream:
            print(chunk["response"], end="", flush=True)
        print()
    else:
        response = ollama.generate(model=model, prompt=prompt_text)
        print(response["response"])


@handle_errors
def chat_with_model(model, stream):
    """Starts an interactive chat session with a model."""
    print(f"Starting chat with {model}. Type 'exit' or 'quit' to end.")
    messages = []
    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() in ["exit", "quit"]:
                break

            messages.append({"role": "user", "content": user_input})

            if stream:
                response_stream = ollama.chat(
                    model=model, messages=messages, stream=True
                )
                full_response = ""
                for chunk in response_stream:
                    content = chunk["message"]["content"]
                    print(content, end="", flush=True)
                    full_response += content
                print()
                messages.append(
                    {"role": "assistant", "content": full_response}
                )
            else:
                response = ollama.chat(model=model, messages=messages)
                assistant_response = response["message"]["content"]
                print(assistant_response)
                messages.append(
                    {"role": "assistant", "content": assistant_response}
                )

        except KeyboardInterrupt:
            print("\nExiting chat.")
            break
        except EOFError:
            print("\nExiting chat.")
            break


def main():
    """Main function to parse arguments and call the appropriate function."""
    parser = argparse.ArgumentParser(
        description="A CLI tool to interact with Ollama models."
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # List command
    parser_list = subparsers.add_parser("list", help="List available models.")
    parser_list.set_defaults(func=lambda args: list_models())

    # Prompt command
    parser_prompt = subparsers.add_parser(
        "prompt", help="Send a single prompt to a model."
    )
    parser_prompt.add_argument(
        "model", help="The name of the model to use."
    )
    parser_prompt.add_argument(
        "prompt_text",
        nargs="?",
        default=None,
        help="The prompt text. Reads from stdin if not provided.",
    )
    parser_prompt.add_argument(
        "-s", "--stream", action="store_true", help="Stream the response."
    )
    parser_prompt.set_defaults(
        func=lambda args: prompt_model(
            args.model, args.prompt_text, args.stream
        )
    )

    # Chat command
    parser_chat = subparsers.add_parser(
        "chat", help="Start an interactive chat session."
    )
    parser_chat.add_argument(
        "model", help="The name of the model to use for the chat."
    )
    parser_chat.add_argument(
        "-s", "--stream", action="store_true", help="Stream the response."
    )
    parser_chat.set_defaults(
        func=lambda args: chat_with_model(args.model, args.stream)
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
