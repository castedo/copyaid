# Get Started


## Setup Steps

### 1) Install Python Package

```bash
pip install git+https://gitlab.com/castedo/copyaid.git
```

### 2) Install the Default Configuration File

```bash
copyaid init
```

### 3) Sign Up for the OpenAI API

If you do not already have an OpenAI account,
sign up at [platform.openai.com/signup](https://platform.openai.com/signup).

### 4) Save Your OpenAI API Key

Save your OpenAI API key as the contents of the file `~/.config/copyaid/openai_api_key.txt`.
To create an API key, visit
[platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### 5) Quick Test

To ensure Copy**AI**d is installed correctly, run:

```bash
copyaid --help
```

The output should begin with:

```
usage: copyaid [-h] [-c <config>] [-d <dest>] <task> <source> [<source> ...]
```

To check that your OpenAI API access is working, execute the following test:

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

You are set up!
---------------

You're now ready to run Copy**AI**d on your own source text files.
The `it` task defaults to using `vimdiff`.
If you prefer not to use Vim,
see [How To Opt Out of Using Vimdiff](howto/notvim.md).

Be cautious with the `stomp` task as it overwrites the source file without showing the changes first.
It's mainly for testing.

To customize your own tasks, refer to the [configuration page](config.md).

!!! Warning
    The OpenAI model selected in the request settings file
    may require splitting large text files into smaller ones, for instance,
    by using the LaTeX `\input` macro.
    This can also help reduce costs, as OpenAI charges based on the number of tokens (word parts).

