<!-- cbr on -->

How to Opt Out of Using Vimdiff
===============================

By default, many Copy**AI**d tasks will run `vimdiff` when AI requests result in
revisions to source text files.
This guide will explain how to configure Copy**AI**d to react differently.

Objective
---------

To have a personalized user configuration file so that Copy**AI**d tasks will
not run `vimdiff`.


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

Copy the following two lines from the default config file to the user configuration file.
If the user configuration file does not exist, create it.

```
[commands]
edit-if-diff = 'diff -qs "$0" "$@" || vimdiff "$0" "$@"'
```

The internal command named `edit-if-diff` is referenced by many Copy**AI**d tasks as a
reaction to revisions returned by AI requests.


### 3) Modify User Config Lines

In your user configuration file, modify the `edit-if-diff` command line
by removing the last half so that it becomes:

```
[commands]
edit-if-diff = 'diff -qs "$0" "$@"'
```

Alternatively, you may replace `vimdiff` with another application.
The `"$0"` expression will expand to the source file location, and the
`"$@"` expression will expand to include all revisions returned by an AI request
(which could be more than one).

For more details, see the [reference](../reference.md).
