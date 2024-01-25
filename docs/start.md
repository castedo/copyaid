<!-- copybreak off -->

# Get Started


## Setup Steps

### 1) Install Python Package

```bash
python3 -m pip install copyaid
```

### 2) Install the Default Configuration File

```bash
copyaid init
```

On most Linux distributions and macOS, your configuration file will be installed at
`~/.config/copyaid/copyaid.toml`.

### 3) Sign Up for the OpenAI API

If you do not already have an OpenAI account,
sign up at [platform.openai.com/signup](https://platform.openai.com/signup).

### 4) Set Up Your OpenAI API Key

To create an API key, visit
[platform.openai.com/api-keys](https://platform.openai.com/api-keys).

OpenAI recommends exporting your API key as an environment variable named
`OPENAI_API_KEY`. For instructions, see the
[OpenAI documentation](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key).

Alternatively, you can reference your OpenAI API key
in your `copyaid.toml` configuration file.
To do this, save your OpenAI API key as the contents of the file
`~/.config/copyaid/openai_api_key.txt` and then uncomment the line
`# openai_api_key_file` in the configuration file from step 2.

### 5) Quick Test

To ensure Copy**AI**d is installed correctly, run:

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

<!-- copybreak off -->

Conclusion
----------

You're now ready to run Copy**AI**d on your own source text files.
The `it` task defaults to using `vimdiff`.
If you prefer not to use Vim,
see [How To Opt Out of Using Vimdiff](howto/notvim.md).

Be cautious with the `stomp` task as it overwrites the source file without showing the changes first.
It's mainly for testing.

The `it` task defaults to a "warm" copyedit. You might prefer adjusting the request
temperature to a cold zero or a hotter temperature.
To learn about the differences, read the [Hot Copyediting page](hot.md).

To customize your tasks, refer to the [reference page](reference.md).

!!! Warning
    Be sure to use [copybreaks](copybreaks.md) and/or ensure that your document consists
    of small text source files.
