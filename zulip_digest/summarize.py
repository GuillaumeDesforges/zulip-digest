from io import StringIO
import logging
import sys
from typing import Callable
from gpt4all import GPT4All
from zulip_digest.api import ZulipMessage
from zulip_digest.model import ZulipTopicExport


def _chunk_texts[T](
    items: list[T],
    to_str: Callable[[T], str],
    max_words: int,
) -> list[list[T]]:
    """
    Split a list of items into chunks of items such that the total number of words in each chunk is less than max_words.
    """
    chunks: list[list[T]] = []
    chunk_word_count = 0
    i_start = 0
    for i, item in enumerate(items):
        if i == len(items) - 1:
            chunks.append(items[i_start:])
            break
        text_word_count = len(to_str(item).split())
        if chunk_word_count + text_word_count >= max_words:
            chunks.append(items[i_start:i])
            i_start = i
            chunk_word_count = 0
        chunk_word_count += text_word_count
    return chunks


def _make_message_summary_prompt(
    stream_name: str,
    topic_name: str,
    messages: list[ZulipMessage],
) -> str:
    prompt = ""
    prompt += "You are a journalist expert at writing comprehensive neutral summaries of conversations on social medias."

    prompt += f"\nYou received new messages in channel '{stream_name}'/'{topic_name}':"
    prompt += "\n---\n"
    prompt += "\n---\n".join(
        f"{message.sender_full_name} posted\n{message.content}" for message in messages
    )
    prompt += "\n---\n"

    prompt += "\nWrite a summary of the propositions and arguments."
    prompt += "\nDon't forget to include the name of the person who posted the proposition or argument."

    prompt += "\nSummary:"

    return prompt


def _make_final_summary_prompt(
    conversation_summaries: list[str],
) -> str:
    prompt = ""
    prompt += "You are a journalist expert at writing comprehensive neutral summaries of conversations on social medias."

    prompt += (
        "\nI need you to re-organize these reports into one single executive summary."
    )

    prompt += "\n".join(f"\n{summary}" for summary in conversation_summaries)

    prompt += "\nSummary:"

    return prompt


def summarize_topic_export(
    model: GPT4All,
    stream_name: str,
    topic_name: str,
    topic_export: ZulipTopicExport,
    print_progress: bool = False,
) -> str:
    chunk_summaries: list[str] = []
    chunks = _chunk_texts(
        items=topic_export.messages,
        max_words=400,
        to_str=lambda message: message.content,
    )
    for i_chunk, chunk in enumerate(chunks):
        if print_progress:
            sys.stderr.write(
                f"Chunk {i_chunk+1}/{len(chunks)} ({len(chunk)} messages)\n"
            )
            sys.stderr.flush()
        chunk_summar_prompt = _make_message_summary_prompt(
            stream_name=stream_name,
            topic_name=topic_name,
            messages=chunk,
        )
        logging.debug("Prompt:\n%s", chunk_summar_prompt)
        chunk_summary_generator = model.generate(
            chunk_summar_prompt,
            temp=0.5,
            streaming=True,
        )
        chunk_summary_builder = StringIO()
        for i_token, chunk_summary_token in enumerate(chunk_summary_generator):
            chunk_summary_builder.write(chunk_summary_token)
            if print_progress:
                sys.stderr.write(f"Tokens generated : {i_token+1}\r")
                sys.stderr.flush()
        chunk_summary = chunk_summary_builder.getvalue()
        chunk_summaries.append(chunk_summary)
        logging.debug("Summary:\n%s", chunk_summary)

    summary_prompt = _make_final_summary_prompt(
        conversation_summaries=chunk_summaries,
    )
    logging.debug("Prompt:\n%s", summary_prompt)
    summary_generator = model.generate(
        prompt=summary_prompt,
        temp=0.5,
        max_tokens=512,
        streaming=True,
    )
    summary_builder = StringIO()
    for i_token, summary_token in enumerate(summary_generator):
        summary_builder.write(summary_token)
        if print_progress:
            sys.stderr.write(f"Tokens generated : {i_token+1}\r")
            sys.stderr.flush()
    summary = summary_builder.getvalue()
    logging.debug("Summary:\n%s", summary)

    return summary
