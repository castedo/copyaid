<!-- copybreak off -->

# Copybreaks

For faster and higher-quality revisions, you need to break your document into manageable
chunks. This can be achieved either by saving the document as multiple files or by using _copybreak lines_.
This approach is **very important** for LaTeX files.
It's advisable to use copybreak lines to isolate paragraphs and sections of text from
the boilerplate scoping in LaTeX, as well as the beginning and end of a LaTeX document.
Copybreak lines divide your document into passages that are sent independently to
OpenAI.
The default syntax for copybreak lines in Markdown and LaTeX follows.

<!-- copybreak off -->

### Markdown (`.md` files)

```html
<!-- copybreak -->

<!-- copybreak on -->

<!-- copybreak off -->
```

### Latex (`.tex` files)

```tex
%% copybreak

%% copybreak on

%% copybreak off
```

<!-- copybreak off -- draft -->

As an alternative to the long keyword `copybreak`, the abbreviated keyword `cbr` is also
configured by default.

Every `copybreak` line will cause the passages before and after the copybreak line to be
processed independently. A `copybreak on` line will cause the passage that follows to
be processed according to the request settings of the task being run.
A `copybreak off` line will cause the passage that follows to not be sent to an AI API
and will simply be echoed back as-is.
A `copybreak` line without any `on` or `off` will cause the passage that follows to be
handled like the passage before it, but independently.

<!-- copybreak on -->

## Passage Length Between Copybreaks

Long passages between copybreaks tend to result in fewer edits made per line.
Conversely, short passages often lead to more edits per line.
