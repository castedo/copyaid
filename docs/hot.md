Hot Copyediting
===============

After running `copyaid init` following a new installation,
the `stomp` and `it` tasks are configured to use the example request settings files
`cold-example.toml` and `warm-example.toml`, respectively.
On most Linux distributions, these files are located in `~/.config/copyaid/`.


Cold Requests
-------------

A "cold" request is defined by the following settings:

```
[openai]
n = 1
temperature = 0
```

The setting `n = 1` instructs OpenAI to return only one revision.
The setting `temperature = 0` instructs OpenAI to provide its best single choice for
the request.

Here is a description for `temperature` from the
[OpenAI API reference](https://platform.openai.com/docs/api-reference/chat/create):

> What sampling temperature to use, between 0 and 2.
> Higher values like 0.8 will make the output more random,
> while lower values like 0.2 will make it more focused and deterministic.


Hot Requests
------------

Conversely, hot requests have a `temperature` setting above zero,
indicating that OpenAI will generate output from a range of possible choices.
Setting `n = 2` instructs OpenAI to return two revisions, and Copy**AI**d will save
and display both revisions alongside the original text.
For instance, a Copy**AI**d task using `vimdiff` will present a 3-way comparison.

If no `seed` setting is specified,
the choices will be selected randomly.
The higher the temperature,
the greater the variation in the revisions from each other and the original text.

Using settings like these
allows you to evaluate whether to integrate a revision,
particularly if OpenAI suggests the same revision in both randomly generated outputs.

```
[openai]
n = 2
temperature = 0.1
```

A higher temperature, such as `0.5`,
can be useful for exploring significantly different rewordings
of text and new ideas for substantial revisions.
You can achieve similar effects by modifying
the wording of the prompt; for example,
by changing "revise" to "rewrite" in `chat_system` prompt of a request settings file.

