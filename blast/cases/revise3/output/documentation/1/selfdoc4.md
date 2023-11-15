# Copy**AI**d.it: Copyedit with AI from a CLI

Copy**AI**d is an open-source command line interface (CLI) that allows you to copyedit source text files using AI, such as OpenAI [GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer)
[Large Language Models](https://en.wikipedia.org/wiki/Large_language_model) (LLMs).
These AI models are capable of frequent, rapid, and very inexpensive
[copyediting](https://en.wikipedia.org/wiki/Copy_editing).

## Features

* Supports text in LaTeX, Markdown, and HTML formats.
* Use it with text file comparison tools like vimdiff to review and merge AI revisions.
* Customize the exact copy-editing instructions sent to OpenAI.
* Perform simultaneous file comparisons across multiple AI revisions.
* Customize which programs are automatically run on AI revisions.


<div class="action-band" markdown>
[Get Started](start.md){ .md-button .md-button--primary }
</div>


## Examples

### Simple Example

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid stomp doc.md
OpenAI request for doc.md
Saving to /tmp/copyaid
$ cat doc.md
Use [this software](http://copyaid.it) to write English well.
```

### Vimdiff Example

You can customize your configuration file `~/.config/copyaid/copyaid.toml` for various
workflows and OpenAI prompts. The following examples work with
the default configuration file installed.

If you prefer using `vimdiff`, consider the following:

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid it doc.md
OpenAI request for doc.md
Saving to /tmp/copyaid
2 files to edit
```

Vimdiff will be run on the original source and revisions after the OpenAI request.

### Workflow Example

Here's an example workflow with multiple steps:

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


## Related

Copy**AI**d was inspired by and heavily influenced by:

* [manubot-ai-editor](https://github.com/greenelab/manubot-ai-editor/)
* [A publishing infrastructure for AI-assisted academic authoring](https://doi.org/10.1101/2023.01.21.525030)

If you have a CLI tool that you would like mentioned here,
please contact [Castedo Ellerman](https://castedo.com).
