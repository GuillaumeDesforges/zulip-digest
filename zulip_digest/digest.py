from io import StringIO
import logging
import sys
from gpt4all import GPT4All

from zulip_digest.zulip import ZulipMessage


def _make_prompt(
    messages: list[ZulipMessage],
    previous_summary: str | None = None,
) -> str:
    prompt = ""
    prompt += (
        "You are a journalist expert at writing comprehensive neutral summaries of conversations on social medias."
        "\nYou do not use any markup, just plain text. For example 'Sarah proposes to buy cookies. William agrees Sarah'."
        "\nThe most important thing for me is to be able to understand what the high-level opinion of each user is."
    )

    prompt += "\nNew messages:"
    prompt += "\n---\n"
    prompt += "\n---\n".join(
        f"{message.sender_full_name} posted\n{message.content}" for message in messages
    )
    prompt += "\n---\n"

    if previous_summary:
        prompt += "\nPlease summarize the novel information in the new messages to append to the summary of the conversation:"
        prompt += "\nPrevious summary:"
        prompt += "\n" + previous_summary
        prompt += "\nContinue:"
    else:
        prompt += "\nPlease write a summary of the conversation as bullet points:"
    return prompt


def _chunk_messages(
    messages: list[ZulipMessage],
    max_words: int,
) -> list[list[ZulipMessage]]:
    chunks: list[list[ZulipMessage]] = []
    chunk_word_count = 0
    i_start = 0
    for i_message, message in enumerate(messages):
        if i_message == len(messages) - 1:
            chunks.append(messages[i_start:])
            break
        message_word_count = len(message.content.split())
        if chunk_word_count + message_word_count >= max_words:
            chunks.append(messages[i_start:i_message])
            i_start = i_message
            chunk_word_count = 0
        chunk_word_count += message_word_count
    return chunks


def summarize_messages(
    model: GPT4All,
    messages: list[ZulipMessage],
    print_progress: bool = False,
) -> str:
    summary = None
    chunks = _chunk_messages(messages, max_words=400)
    for i_chunk, message_chunk in enumerate(chunks):
        if print_progress:
            sys.stderr.write(
                f"Chunk {i_chunk+1}/{len(chunks)} ({len(message_chunk)} messages)\n"
            )
        prompt = _make_prompt(message_chunk, summary)
        logging.debug("Prompt:\n%s", prompt)
        chunk_summary_generator = model.generate(
            prompt,
            temp=0.5,
            streaming=True,
        )
        chunk_summary_builder = StringIO()
        for i_token, chunk_summary_token in enumerate(chunk_summary_generator):
            chunk_summary_builder.write(chunk_summary_token)
            if print_progress:
                sys.stderr.write(f"Tokens generated : {i_token+1}\r")
        if summary is None:
            summary = chunk_summary_builder.getvalue()
        else:
            summary += chunk_summary_builder.getvalue()

    assert summary is not None
    return summary
