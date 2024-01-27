<!-- cbr off -->

Hot Copyediting
===============

The default configurations of the `stomp` and `light` tasks are set to make "cold"
requests.
In contrast, the `heavy` task is configured by default to make "hot" requests.

<!-- cbr off -->

Cold Requests
-------------

A "cold" request refers to the type of request one might naturally expect a computer to handle.
The response is (usually) consistent,
exhibiting (mostly) deterministic behavior.
Such a request will have the following settings:

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


<!-- cbr off -->

Hot Requests
------------

Conversely, hot requests have a `temperature` setting above zero,
indicating that OpenAI will generate output from a range of possible choices.

```
[openai]
n = 2
temperature = 0.4
```

Setting `n = 2` instructs OpenAI to return two revisions, and Copy**Ai**d will save
and can present a 3-way comparison between both revisions alongside the original text.

If no `seed` setting is specified,
the choices will be selected randomly.
The higher the temperature,
the greater the variation in the revisions from each other and the original text.

Using settings like these
allows you to evaluate whether to integrate a revision,
particularly if OpenAI suggests the same revision in both randomly generated outputs.

A higher temperature, such as `0.8`,
can be useful for exploring significantly different rewordings
of text and new ideas for substantial revisions.
