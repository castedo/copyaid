Change History
==============

Version 0.8.1 (2026-Jan-16)
---------------------------

* Updated the default model to GPT-4.1.
* Added configuration for the reStructuredText format.

Version 0.7.1 (2024-Jan-27)
---------------------------

* Updated request setting files based on testing with the OpenAI January 2024 preview of
  GPT-4 Turbo.
* Removed the `copy init` pseudo-task.
* Renamed the 'it' task to 'light'.
* Renamed default request settings files.
* Configuration is now set first by the package config, followed by an optional user config file.
* Renamed the configuration command `vim-if-diff` to `edit-if-diff`.


Version 0.6.1 (2024-Jan-24)
---------------------------

* Implemented [copybreaks](copybreaks.md).
* `diffadapt` is now called internally, rather than as an external command.
* Updated the example request settings files with curated prompts.
* Deprecated the 'clean' configuration setting.
