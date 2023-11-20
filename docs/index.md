# Copy**AI**d.it: Copyedit with AI from a CLI

Copy**AI**d is an open-source command-line interface (CLI) utility
that copyedits text files using the OpenAI API for
[GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer),
a [Large Language Model](https://en.wikipedia.org/wiki/Large_language_model)
capable of frequent, rapid, and extremely inexpensive
[copyediting](https://en.wikipedia.org/wiki/Copy_editing)
(orders of magnitude cheaper than human copyediting).


## Features

* Supports LaTeX, Markdown, and HTML formats.
* Integrates with text file comparison tools like `vimdiff` for reviewing and merging AI revisions.
* Allows customization of the copy-editing instructions sent to OpenAI.
* Enables simultaneous file comparisons across multiple AI revisions.
* Permits customization of programs to run automatically on AI revisions.


<div class="action-band" markdown>
[Get Started](start.md){ .md-button .md-button--primary }
</div>

!!! alert
    As of Nov 2023, OpenAI offers $5 in free credit for your first 3 months.
    This can cover copyediting for more than a hundred thousand words.


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

With the default configuration, the `it` task will request a pair of revisions from
OpenAI and then run `vimdiff` for a 3-way diff of the original source and two revisions.

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid it doc.md
OpenAI request for doc.md
Saving to /tmp/copyaid
3 files to edit
```

