# Configuration

To view help on the current configuration, use the command `copyaid -h`.

On POSIX systems, the default location for the configuration file is
`~/.config/copyaid/copyaid.toml`.
For detailed information on the TOML format, visit [toml.io](https://toml.io).

## Initial Configuration

After running `copyaid init`, a heavily commented initial configuration is created.
It sets up some basic tasks:

* `it`: Makes a new API request and runs `vimdiff` on the resulting revisions and original
source.

* `stomp`: Overwrites the source file with the revision of a new API request.

The following tasks DO NOT make a new API request. They only operate on saved revisions
from previous API requests:

* `diff`: Runs diff on saved revisions.

* `vimdiff`: Runs vimdiff on saved revisions.

* `where`: Prints the file location(s) of the saved revision(s).

* `replace`: Overwrites the source file with the saved revision of a prior API request.


## Tasks

A task consists of an optional request to the OpenAI API followed
by an optional chain of *react* commands.

The `request` value for each task specifies the request settings file to be used for
OpenAI API requests. See the [request settings](requests.md) page.

The `react` value is a list of commands to be run on the original source and
the saved results of an OpenAI API request. These saved results are
from the request of a task if specified or saved results from running another task.
The commands in the list are defined in the `[commands]` section.


## Shell Commands

The `[commands]` section defines the shell command line to execute. The bash expression:

* `"$0"` will expand to the path of the source file, and
* `"$@"` will expand to the saved revisions returned by the latest API request.


## OpenAI API Key

The optional `openai_api_key_file` value is the path to a file containing only your
OpenAI API key. This path can be relative to the configuration file.
If this value is not provided, then the `OPENAI_API_KEY` environment variable must be set.

## Logging

The optional `log_format` value can be set to `json` or `jsoml` to log the exact request sent and
response received from the OpenAI API.
On most Linux distributions, the logs will be saved in `~/.local/state/copyaid/log`.
It is easier to read, diff, and copy-and-paste source text lines as-is from these logs in JSOML than in JSON.
If `jsoml` is chosen, you must install the `jsoml` Python package.

