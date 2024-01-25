<!-- copybreak on -->

# Reference

For details on the command-line options, run `copyaid --help`.


## Configuration

To view help for the current configuration, use the command `copyaid -h`.

On POSIX systems, the default location for the configuration file is
`~/.config/copyaid/copyaid.toml`.
For detailed information on the TOML format, visit [toml.io](https://toml.io).

<!-- copybreak off -- ok -->

### Initial Configuration

After running `copyaid init`, a heavily commented initial configuration file is created,
along with three example [request settings files](#request-settings).
Three default tasks make OpenAI API requests:

* `it`: Sends a new API request and, if there are changes, runs `vimdiff`
  to compare the resulting revisions with the original source.
  It defaults to using the request settings file `warm-example.toml`.

* `stomp`: Overwrites the source file with the revision of a new API request.
  Defaults to the request settings file `cold-example.toml`.

* `proof`: Makes an API request for proofreading.
  Defaults to the request settings file `proof-example.toml`.

The following tasks do not make a new API request but work with revisions
saved from previous API requests:

* `diff`: Runs `diff` on the saved revisions.

* `vimdiff`: Runs `vimdiff` on the saved revisions.

* `where`: Prints the file paths of the saved revisions.

* `clean`: Deletes saved revisions for given source files.

* `replace`: Overwrites the source file with the saved revision from a previous API request.

<!-- copybreak off -- ok -->

### File Formats

Each entry in the `formats` table defines the formatting of copybreaks for a
given file format with specific file extensions.
The initial configuration includes formats for Markdown and LaTeX.
Files with the extensions of a configured format will be parsed for copybreak lines.
For more details, see the [copybreaks page](copybreaks.md).

<!-- copybreak off -->

### Tasks

A task consists of an optional request to the OpenAI API followed
by an optional chain of *react* commands.

The `request` value for each task specifies the request settings file to be used for
OpenAI API requests. See the [request settings](#request-settings) section.

The `clean` setting determines whether saved revisions are reused or
replaced by a new request. If `clean = true`, a request will be made and
any saved revisions will be replaced. Otherwise, a request will be skipped if
a single revision is saved and its contents are identical to the source file.

The `react` value is a list of commands to run on the original source and
the saved results of an OpenAI API request. These saved results are
from the request of a task if specified or previously saved results.
The commands in the list are defined in the `[commands]` section.


### Shell Commands

The `[commands]` section defines the shell command line to execute. The bash expressions:

* `"$0"` expands to the path of the source file, and

* `"$1"` expands to the first saved revision returned by the latest API request.

* `"$@"` expands to all saved revisions returned by the latest API request.


### OpenAI API Key

The optional `openai_api_key_file` value is the path to a file containing only your
OpenAI API key. This path can be relative to the configuration file.
If this value is not provided, the `OPENAI_API_KEY` environment variable must be set.


### Logging

The optional `log_format` value can be set to `json` or `jsoml` to log the exact request sent and
response received from the OpenAI API.
On most Linux distributions, logs are saved in `~/.local/state/copyaid/log`.
Logs in JSOML are easier to read, diff, and copy-and-paste from than in JSON.
If `jsoml` is chosen, you must install the `jsoml` Python package.


<!-- copybreak off -->

## Request Settings

Values in a request settings file correspond to values sent to the
[OpenAI API endpoint for chat completion](https://platform.openai.com/docs/api-reference/chat/create).

Upon running `copyaid init` for the first time, it creates `cold-example.toml`,
`warm-example.toml`, and `proof-example.toml` request settings files,
in addition to a `copyaid.toml` configuration file.
On most Linux distributions, these files are located in `~/.config/copyaid/`.

For detailed information on the TOML format, visit [toml.io](https://toml.io).

<!-- copybreak off -->

### Settings

`chat_system`
:   The instructions sent to the OpenAI API.
    This value is sent as the first message in the request.
    It will have the role `system`.
    The source text file is sent as the second message with the role `user`.

`max_tokens_ratio`
:   Modifying this setting is generally unnecessary. It is a ratio used to calculate
    the `max_tokens` parameter for the OpenAI API.
    Copy**AI**d will estimate the number of tokens in the source file
    and multiply that estimate by `max_tokens_ratio` to determine the
    `max_tokens` value for the API request output.

`openai.model`
:   The OpenAI API
    [chat completion compatible model](https://platform.openai.com/docs/models/model-endpoint-compatibility)
    to be used.

`openai.temperature`
:   The sampling temperature for the OpenAI API.
    For more details on this setting, refer to [Hot Copyediting](hot.md).

`openai.n`
:   The optional `n` value specifies the number of parallel revisions to request.
    The default is `n = 1`. In this case, you probably also want `temperature = 0`.

<!-- copybreak off -->

### Older settings

The `chat_system` setting has limited support with GPT-3.
For this older model,
the `prepend` and `append` settings are useful for incorporating the copyediting
instructions as part of the initial message along with the original source text.
These values are added before and after the source text to be revised as the chat
message sent to OpenAI.
