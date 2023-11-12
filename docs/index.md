Copy**AI**d.it: Copy-Editing with AI from the CLI
=================================================

This website is an online resource for command line interface (CLI) users who want to
copy-edit text files, including LaTeX and Markdown files, with AI, specifically [Large
Language Models](https://en.wikipedia.org/wiki/Large_language_model).

Copy**AI**d is an open-source Python utility for performing copy-editing using the OpenAI API.

Simple Example 
--------------

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid stomp doc.md
OpenAI request for doc.md
Saving to /tmp/copyaid
$ cat doc.md
Use [this software](http://copyaid.it) to write English well.
```

Getting Started
---------------

### 1: Install

```bash
pip install git+https://gitlab.com/castedo/copyaid.git
```

### 2: Install the default configuration file

```bash
copyaid init
```

### 3: Sign-up for the OpenAI API

If you do not already have an OpenAI account,
sign up at [platform.openai.com/signup](https://platform.openai.com/signup).

### 4: Save Your OpenAI API Key

Save your OpenAI API key value as `~/.config/copyaid/openai_api_key.txt`.

If you need to create one, visit
[platform.openai.com/api-keys](https://platform.openai.com/api-keys).


More Examples
-------------

Your configuration file `~/.config/copyaid/copyaid.toml` can be customized
for many workflows and many OpenAI prompts. The following examples work
from the default configuration file installed.

If you like to use `vimdiff`, consider

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid it doc.md
OpenAI request for doc.md
Saving to /tmp/copyaid
2 files to edit
```
Vimdiff will be run on the original source and revisions after the OpenAI request.


Another example of a possible workflow:

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid check doc.md
OpenAI request for doc.md
Saving to /tmp/copyaid
Files doc.md and /tmp/copyaid/R1/doc.md differ
$ copyaid diff doc.md 
1c1
< Use [this sofware](htp://copyaid.it) to wright English good.
---
> Use [this software](http://copyaid.it) to write English well.
$ copyaid replace doc.md 
$ cat doc.md
Use [this software](http://copyaid.it) to write English well.
```


FAQ
---

Does it work with LaTeX files?
:   Yes.

Does it work with Markdown?
:   Yes.

Does it work with Word documents?
:   Most likely not.

Where is the source code?
:   Source code available at [gitlab.com/castedo/copyaid](https://gitlab.com/castedo/copyaid).


Related
-------

Inspired and heavily influenced by:

* [manubot-ai-editor](https://github.com/greenelab/manubot-ai-editor/)
* [A publishing infrastructure for AI-assisted academic authoring](https://doi.org/10.1101/2023.01.21.525030)

If you have a CLI tool you would like mentioned here,
contact [Castedo Ellerman](https://castedo.com).
