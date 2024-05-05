from io import StringIO
import logging
import sys
from typing import Callable
from gpt4all import GPT4All

from zulip_digest.zulip import ZulipMessage


def _chunk_texts[T](
    elements: list[T],
    to_str: Callable[[T], str],
    max_words: int,
) -> list[list[T]]:
    chunks: list[list[T]] = []
    chunk_word_count = 0
    i_start = 0
    for i, element in enumerate(elements):
        if i == len(elements) - 1:
            chunks.append(elements[i_start:])
            break
        text_word_count = len(to_str(element).split())
        if chunk_word_count + text_word_count >= max_words:
            chunks.append(elements[i_start:i])
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

    prompt += "\nI need you to re-organize these reports."
    prompt += "\nWrite executive summary of the propositions and arguments from the following reports."

    prompt += "\n".join(f"\n---\n{summary}" for summary in conversation_summaries)

    prompt += "\nSummary:"

    return prompt


def summarize_messages(
    model: GPT4All,
    stream_name: str,
    topic_name: str,
    messages: list[ZulipMessage],
    print_progress: bool = False,
) -> str:
    conversation_summaries: list[str] = []
    chunks = _chunk_texts(
        elements=messages,
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
        conversation_summary = chunk_summary_builder.getvalue()
        conversation_summaries.append(conversation_summary)
        logging.debug(
            "Summary:\n%s",
        )

    summary_prompt = _make_final_summary_prompt(
        conversation_summaries=conversation_summaries,
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

    return summary
