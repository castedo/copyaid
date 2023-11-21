# OpenAI API Request Settings

Values in a request settings file correspond to values sent to the
[OpenAI API endpoint for chat completion](https://platform.openai.com/docs/api-reference/chat/create).

Upon running `copyaid init` for the first time, it creates `cold-example.toml`,
`warm-example.toml`, and `proof-example.toml` request settings files,
in addition to a `copyaid.toml` configuration file.
On most Linux distributions, these files are located in `~/.config/copyaid/`.

For detailed information on the TOML format, visit [toml.io](https://toml.io).


## Settings

`chat_system`
:   The instructions sent to the OpenAI API.
    This value is sent as the first message in the request.
    It will have role `system`.
    The source text file is sent as the second message with the role `user`.

`max_tokens_ratio`
:   It is generally unnecessary to modify this setting. It is a ratio used to calculate
    the OpenAI API `max_tokens` parameter.
    Copy**AI**d will estimate the number of tokens in the source file
    and multiply that estimate by `max_tokens_ratio` to determine the
    `max_tokens` value for the API request output.

`openai.n`
:   The `n` value specifies the number of candidate revisions to save.
    If you choose `n = 1`, you probably also want `temperature = 0`.

`openai.temperature`
:   OpenAI API sampling temperature.
    For more details on this setting, refer to [Hot Copyediting](hot.md).

`openai.model`
:   The OpenAI API
    [chat completion compatible model](https://platform.openai.com/docs/models/model-endpoint-compatibility)
    to be used.


## Older settings

The `chat_system` setting has limited support with GPT-3.
For this older model,
the `prepend` and `append` settings are useful for incorporating the copyediting
instructions as part of the initial message along with the original source text.
These values are added before and after the source text to be revised as the chat
message sent to OpenAI.

