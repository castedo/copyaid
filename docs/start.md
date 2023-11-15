# Get Started


## Setup Steps

### 1) Install Python Package

```bash
pip install git+https://gitlab.com/castedo/copyaid.git
```

### 2) Install the default configuration file

```bash
copyaid init
```

### 3) Sign up for the OpenAI API

If you do not already have an OpenAI account,
sign up at [platform.openai.com/signup](https://platform.openai.com/signup).

### 4) Save Your OpenAI API Key

Save your OpenAI API key value as `~/.config/copyaid/openai_api_key.txt`.
If you need to create one, visit
[platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### 5) Quick Test

Perform a quick check to make sure Copy**AI**d is installed properly.

```bash
copyaid --help
```

You should see output starting with the following line:

```
usage: copyaid [-h] [-c <config>] [-d <dest>] <task> <source> [<source> ...]
```

To make sure your OpenAI API access is working correctly, perform the following test
workflow:

```
$ echo "Sofware dockumentashun are helpfull." > test.md
$ copyaid stomp test.md
OpenAI request for test.md
Saving to /tmp/copyaid
$ cat test.md
Software documentation is helpful.
```

You are setup!
--------------

You are now ready to run Copy**AI**d on your own source text files.

!!! Warning
    Depending on which OpenAI model you use,
    you may need to break down large text files into multiple smaller text files.
    For example, by using the LaTeX `\input` macro to include multiple smaller files.
    You may want to do this regardless to save on cost. OpenAI charges by the word
    (technically by token).

