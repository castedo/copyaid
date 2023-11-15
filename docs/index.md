# Copy**AI**d.it: Copyedit with AI from a CLI

Copy**AI**d is an open-source command line interface (CLI) utility
that copyedits text files using the OpenAI API for
[GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer),
a [Large Language Models](https://en.wikipedia.org/wiki/Large_language_model)
capable of frequent, rapid, and very inexpensive
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

With the default configuration, the `it` task will request a revision from OpenAI and
then run vimdiff to the original source.

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid it doc.md
OpenAI request for doc.md
Saving to /tmp/copyaid
2 files to edit
```

You can customize your configuration file `~/.config/copyaid/copyaid.toml`
to change what OpenAI requests and commands are done by CopyAId tasks.


## Related

Copy**AI**d was inspired by and heavily influenced by:

* [manubot-ai-editor](https://github.com/greenelab/manubot-ai-editor/)
* [A publishing infrastructure for AI-assisted academic authoring](https://doi.org/10.1101/2023.01.21.525030)

If you have a CLI tool that you would like mentioned here,
contact [Castedo Ellerman](https://castedo.com).
