from io import StringIO
import logging
import sys
from typing import Iterable
from gpt4all import GPT4All

from zulip_digest.zulip import ZulipMessage


def _make_prompt(
    messages: list[ZulipMessage],
    previous_summary: str | None = None,
) -> str:
    prompt = (
        "You are a journalist expert at writing comprehensive neutral summaries of conversations."
        " You do not use any markup, just plain text."
        " The most important thing for me is to be able to understand"
        " 1) how the topic relates to Nix community governance"
        " and 2) what the opinion of the main contributors is."
    )
    if previous_summary:
        prompt += f" Given the following summary:\n\n{previous_summary}"
    prompt += "\n\nPlease write a summary of the following conversation:"
    prompt += "\n---\n"
    prompt += "\n---\n".join(
        f"{message.sender_full_name} said {message.content}" for message in messages
    )
    prompt += "\n---\n"
    prompt += "Summary:\n"
    return prompt


def _chunk_messages(
    messages: list[ZulipMessage], size: int
) -> Iterable[list[ZulipMessage]]:
    i_min = 0
    i_max = size
    while i_min < len(messages):
        yield messages[i_min:i_max]
        i_min = i_max
        i_max += size


def summarize_messages(
    model: GPT4All,
    messages: list[ZulipMessage],
    print_progress: bool = False,
) -> str:
    summary = None
    for i_chunk, message_chunk in enumerate(_chunk_messages(messages, size=10)):
        if print_progress:
            sys.stderr.write(
                f"Chunk {i_chunk+1}/{(len(messages) // 50)+1} ({len(message_chunk)} messages)\n"
            )
        prompt = _make_prompt(message_chunk, summary)
        chunk_summary_generator = model.generate(
            prompt,
            temp=0.2,
            streaming=True,
        )
        chunk_summary_builder = StringIO()
        for i_token, chunk_summary_token in enumerate(chunk_summary_generator):
            chunk_summary_builder.write(chunk_summary_token)
            if print_progress:
                sys.stderr.write(f"Tokens generated : {i_token+1}\r")
        summary = chunk_summary_builder.getvalue()

    assert summary is not None
    return summary
