# OpenAI API Request Settings

Values in a request settings file correspond to values sent to the
[OpenAI API endpoint for chat completion](https://platform.openai.com/docs/api-reference/chat/create).
Most values correspond directly, but some indirectly determine certain OpenAI request values.

When `copyaid init` is initially run, it creates a new `cold-example.toml` request settings file
in addition to a `copyaid.toml` configuration file.

Users can adjust the `prepend` value to modify the copyediting
instructions sent to OpenAI. This value is added at the beginning of the original source text
being revised.


## Hot vs Cold Requests

The `cold-example.toml` file includes the following settings:

```
[openai]
n = 1
temperature = 0
```

With these *cold* settings, OpenAI will return a single best revision.
By changing the `temperature` value to a number closer to `1`, OpenAI will
randomly suggest a revision from multiple candidate revisions.
The value of `n` determines the number of candidate revisions that are saved.
Running *hot* settings such as `temperature = 0.5` and `n = 2` can be useful
for evaluating multiple AI suggestions and the degree of confidence in those AI
suggestions.
