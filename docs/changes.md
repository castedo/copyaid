<!-- copybreak off -- ok -->

Change History
==============

Version 0.7.1
-------------

* Updated request setting files based on testing with the OpenAI January 2024 preview of
  GPT-4 Turbo.
* Removed the `copy init` pseudo-task.
* Configuration is now set first by the package config, followed by an optional user config file.
* Renamed the configuration command `vim-if-diff` to `edit-if-diff`.


Version 0.6.1 (2024-Jan-24)
---------------------------

* Implemented [copybreaks](copybreaks.md).
* `diffadapt` is now called internally, rather than as an external command.
* Updated the example request settings files with curated prompts.
* Deprecated the 'clean' configuration setting.
