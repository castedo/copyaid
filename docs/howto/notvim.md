How to Opt Out of Using Vimdiff
===============================

Copy**AI**d is set up to use `vimdiff` by default for viewing suggested revisions.
If you prefer not to use Vim, you have two options:

* Run default tasks that do not initiate `vimdiff`.
* Customize your `copyaid.toml` configuration file to specify a different program.

Default Tasks
-------------

The default tasks that do not use `vimdiff` include:

* `stomp`: Overwrites the source file with the revised content from a new API request.

* `diff`: Executes `diff` on saved revisions.

* `where`: Prints the file location(s) of the saved revision(s).

* `replace`: Overwrites the source file with the stored revision from a previous API request.


Customize Tasks
---------------

You can customize the `copyaid.toml` configuration file to change the
`it` task to execute an alternative program instead of `vimdiff`.
On most Linux distributions, you can find `copyaid.toml` in the `~/.config/copyaid/`
directory.

Within `copyaid.toml`, the `it` task is defined in the `[tasks.it]` section.
The `react` value specifies the sequence of commands to run after completing the request.
The last command in the `react` sequence is `vim-if-diff`.
The definition of this command is in the `[commands]` section.

You can also add your own new task by copying and modifying the `[tasks.it]` section and
giving it a new name, such as `[tasks.revise]`.

For more details, see the [reference](../reference.md).
