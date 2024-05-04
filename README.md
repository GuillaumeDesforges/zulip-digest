# zulip digest

Turn conversations on Zulip into summaries with "the power of AI"_TM_.

## Usage

Summarize all topics in a stream:

```bash
zulip-digest -s STREAM_NAME
```

Reference:

```console
$ zulip-digest --help
Usage: zulip-digest [OPTIONS]

Options:
  -s, --stream TEXT  Streams to process
  -t, --topic TEXT   Topics to process (only 1 stream allowed)
  --json             Output JSON
  --debug            Enable debug logging
  --help             Show this message and exit.
```

## Install

Requirements: Python 3+

Install from the repository:

```bash
pip install https+git://github.com/GuillaumeDesforges/zulip-digest.git
```

Then create a file `.zuliprc` as specified in the [Zulip documentation](https://zulip.com/api/configuring-python-bindings#configuration-keys-and-environment-variables).

```
[api]
key=<API key from the web interface>
email=<your email address>
site=<your Zulip server's URI>
...
```
