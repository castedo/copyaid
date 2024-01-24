<!-- copybreak off -- draft -->

# Copybreaks

For faster and higher quality revisions, you need to break your document into manageable
chunks, either by saving the document as multiple files or using _copybreak lines_.
This is **very important** for LaTeX files.
It is best to use copybreak lines to isolate the paragraphs and sections of text from
the boilerplate scoping LaTeX and the beginning and end of a LaTeX document.
Copybreak lines break up your document into passages that can be independently revised.
The syntax for copybreak lines is configured in the `copyaid.toml` file.
The initial installation (via `copyaid init`) will configure the following syntaxes for
the following two file formats.

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

As an alternative to the long keyword `copybreak`, the abbreviated keyword `cbr` is also initially
configured.

Every `copybreak` line will cause the passages above and below the copybreak line to be
processed independently. A `copybreak on` line will cause the passage that follows to
be processed according to the request settings of the task being run.
A `copybreak off` line will cause the passage that follows to not be sent to an AI API
and will simply be echoed back as-is.
A `copybreak` line without any `on` or `off` will cause the passage that follows to be
handled like the passage before it, but independently.

<!-- copybreak on -->

## Passage Length between Copybreaks

Long passages between copybreaks tend to result in fewer edits made per line.
Conversely, short passages often lead to more edits per line.
