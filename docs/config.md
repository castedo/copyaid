# Configuration

To view help on the current configuration, use the command `copyaid -h`.

On POSIX systems, the default location for the configuration file is
`~/.config/copyaid/copyaid.toml`.
For detailed information on the TOML format, visit [toml.io](https://toml.io).

## Initial Configuration

After running `copyaid init`, a heavily commented initial configuration is created
along with three example [request settings files](requests.md).
Three default tasks make OpenAI API requests:

* `it`: Makes a new API request and runs `vimdiff` on the resulting revisions and the original
  source. Defaults to the request settings file `warm-example.toml`.

* `stomp`: Overwrites the source file with the revision of a new API request.
  Defaults to the request settings file `cold-example.toml`.

* `proof`: If there is no previously saved single revision, a proofreading
  request is made. Defaults to the request settings file `proof-example.toml`.

The following tasks do not make a new API request but operate on saved revisions
from previous API requests:

* `diff`: Runs `diff` on saved revisions.

* `vimdiff`: Runs `vimdiff` on saved revisions.

* `where`: Prints the file locations of the saved revisions.

* `clean`: Deletes saved revisions for given source files.

* `replace`: Overwrites the source file with the saved revision of a prior API request.

* `freeze`: Overwrites the saved revision with a single copy of the source file.
  This is useful when proofreading multiple source files and deciding that a source file
  no longer needs corrections.


## Tasks

A task consists of an optional request to the OpenAI API followed
by an optional chain of *react* commands.

The `request` value for each task specifies the request settings file to be used for
OpenAI API requests. See the [request settings](requests.md) page.

The `clean` setting determines whether saved revisions are reused or
replaced by a new request. If `clean = true`, a request will be made and
any saved revisions will be replaced. Otherwise, a request will be skipped if
a single revision is saved and its contents are identical to the source file.

The `react` value is a list of commands to run on the original source and
the saved results of an OpenAI API request. These saved results are
from the request of a task if specified or previously saved results.
The commands in the list are defined in the `[commands]` section.


## Shell Commands

The `[commands]` section defines the shell command line to execute. The bash expressions:

* `"$0"` expands to the path of the source file, and

* `"$1"` expands to the first saved revision returned by the latest API request.

* `"$@"` expands to all saved revisions returned by the latest API request.

### Diffadapt

One of the shell commands executes the utility `diffadapt`, which is installed with `copyaid`.
The `diffadapt` utility performs two tasks:

* it inserts newline characters into the revision files for better line-by-line diffs with the source file, and
* it checks whether the contents of a revision file consist solely of a codeword (specified by the `-c` option).

If a revision file consists solely of a codeword, it will be replaced entirely
with the source file. This is useful for requests that instruct the OpenAI API to
return only the codeword when there are no text changes.


## OpenAI API Key

The optional `openai_api_key_file` value is the path to a file containing only your
OpenAI API key. This path can be relative to the configuration file.
If this value is not provided, the `OPENAI_API_KEY` environment variable must be set.


## Logging

The optional `log_format` value can be set to `json` or `jsoml` to log the exact request sent and
response received from the OpenAI API.
On most Linux distributions, logs are saved in `~/.local/state/copyaid/log`.
Logs in JSOML are easier to read, diff, and copy-and-paste from than in JSON.
If `jsoml` is chosen, you must install the `jsoml` Python package.

