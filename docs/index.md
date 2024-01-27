<!-- copybreak off -->

# Copy**Ai**d: Copyedit with AI from a CLI

Copy**Ai**d is an open-source command-line interface (CLI) utility
that copyedits text files using the OpenAI API for
[GPT](https://en.wikipedia.org/wiki/Generative_pre-trained_transformer),
a [Large Language Model](https://en.wikipedia.org/wiki/Large_language_model)
capable of frequent, rapid, and extremely inexpensive
[copyediting](https://en.wikipedia.org/wiki/Copy_editing)
(orders of magnitude cheaper than human copyediting).


## Features

* Supports Markdown and LaTeX formats.
* Integrates with text file comparison tools such as `vimdiff` for reviewing and merging AI revisions.
* Enables simultaneous file comparisons across multiple AI revisions.
* Permits customization of programs to run automatically after AI revisions.
* Allows customization of the copyediting instructions sent to OpenAI.


<div class="action-band" markdown>
[Get Started](start.md){ .md-button .md-button--primary }
</div>

!!! alert
    As of November 2023, OpenAI offers $5 in free credit for your first 3 months.
    This can cover copyediting for more than a hundred thousand words.

<!-- copybreak off -->

## Examples

### Simple Example

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid stomp doc.md
Saving revisions to /tmp/copyaid/R?/doc.md
 for source doc.md
$ cat doc.md
Use [this software](http://copyaid.it) to write English well.
```

### Vimdiff Example

With the default configuration, the `heavy` task will request a pair of revisions from
OpenAI and then run `vimdiff` for a 3-way diff of the original source and two revisions.

```bash
$ echo "Use [this sofware](htp://copyaid.it) to wright English good." > doc.md
$ copyaid heavy doc.md
Saving revisions to /tmp/copyaid/R?/doc.md
 for source doc.md
3 files to edit
```
