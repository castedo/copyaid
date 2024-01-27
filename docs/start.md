<!-- copybreak off -->

# Get Started


## Setup Steps

### 1) Install the Python Package

```bash
python3 -m pip install copyaid
```

### 2) Sign Up for the OpenAI API

If you do not already have an OpenAI account,
sign up at [platform.openai.com/signup](https://platform.openai.com/signup).

<!-- copybreak off -->

### 3) Set Up Your OpenAI API Key

To create an API key, visit
[platform.openai.com/api-keys](https://platform.openai.com/api-keys).

OpenAI recommends exporting your API key as an environment variable named
`OPENAI_API_KEY`. For instructions, see the
[OpenAI documentation](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key).

Alternatively, you can reference your OpenAI API key from a personalized `copyaid.toml`
configuration file.
To learn how, consult [the reference](reference.md).

<!-- copybreak off -->

### 4) Quick Test

To ensure Copy**Ai**d is installed correctly, run:

```bash
copyaid --help
```

The output should begin with:

```
usage: copyaid [-h] [-c <config>] [-d <dest>] <task> <source> [<source> ...]
```

To verify that your OpenAI API access is working, perform the following test:

```bash
echo "Sofware dokumentashon are helpfull." > test.md
copyaid stomp test.md
# Expected output:
#   OpenAI request for test.md
#   Saving to /tmp/copyaid
cat test.md
# The file should now contain:
#   Software documentation is helpful.
```

<!-- copybreak on -->

Conclusion
----------

You are now ready to perform copyediting [tasks](tasks.md) on your own source text files.
Read the [Tasks page](tasks.md) to learn how.

!!! Warning
    Make sure to use [copybreaks](copybreaks.md) and/or ensure that your document consists
    of small text source files.
