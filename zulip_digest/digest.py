import logging
from gpt4all import GPT4All

from zulip_digest.zulip import ZulipMessage


def summarize_messages(
    model: GPT4All,
    messages: list[ZulipMessage],
):
    prompt = (
        "You are a journalist expert at writing neutral summaries of conversations."
    )
    prompt += "Summarize the following conversation."
    prompt += "\n\n".join(
        f"{message.sender_full_name} said {message.content}" for message in messages
    )
    logging.debug(prompt)

    summary = model.generate(prompt=prompt, temp=0.5)

    return summary
