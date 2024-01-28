<!-- cbr off -->

How to Adjust Request Settings
==============================

Request settings files control the details of the instructions sent to OpenAI,
along with the source text.
These settings can impact the:

* English dialect used,
* handling of text formatting,
* OpenAI request temperature, and
* copyediting weight (how light or heavy).

<!-- cbr off -->

Steps
-----


### 1) Determine Config File Locations

Determine the file locations of the default configuration and your personal
configuration by using the `--help` option.

```bash
copyaid --help
```

You will see two lines of output similar to the following:
```
Default config: /tmp/copyaid/package/copyaid.toml
User config: /home/wang/.config/copyaid/copyaid.toml
```

### 2) Copy Config Lines

Choose a task you want to use as a starting point.
For the purpose of this guide, let's assume the task is named `foo`.
Copy the following three lines from the default config file to the user configuration file.
If the user configuration file does not exist, create it.

```
[tasks.foo]
request = "foobar.toml"
react = ["edit-if-diff"]
```

Note that the `request` key refers to a request settings file within the default package
config directory.

<!-- cbr off -->

### 3) Copy the Request Settings File

This guide illustrates a request settings file named `foobar.toml`.
Copy this file from the default config directory to the directory where your
user configuration is located.


### 4) Modify the New Request Settings File

Edit the new copy of `foobar.toml` to make your desired adjustments.
For example, you might want to change the `chat_system` value to `British` instead of
`American`.
Or, if you're working with LaTeX files, you might replace `Markdown and
HTML` with `LaTeX`.

Another setting you may want to adjust is the `temperature` setting in `foobar.toml`.
For more information, see the explanation of [hot copyediting](../hot.md).

Lastly, to reduce the weight of the default `heavy` request setting, replace `Improve`
with `Revise` in the system prompt (`chat_system`).


### 5) Choose a New Task Name (Optional)

You may want to choose a different task name so that you can still use the default
settings of `foo`.
If you want to have a new task name, such as `baz`,
then change the first line of your copied config lines to:
```
[task.bar]
```

For more details, see the [reference](../reference.md).
