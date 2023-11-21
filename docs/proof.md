Proofreading
============

After running `copyaid init` following a new installation,
the `proof` task is configured to use the example proofreading request settings file
`proofread.toml`.
The `proof` task works well with multiple simultaneous source files:

```
copyaid proof *.md
```

After correcting all error in the source text file to match a saved revision,
rerunning `copyaid proof` will not trigger another OpenAI API request.
Instead,
Copy**AI**d will simply indicate that the saved revision and the source text are identical.

!!! tip
    If a proofreading results in an unwanted "correction",
    you can edit away the mis-correction *in the saved revision* to match the source
    text as you prefer.
    The next time you run `copyaid proof` on that file, it will confirm that the source
    text and the "saved revision" are identical.

The proofreading request settings file is tuned to be the opposite of a hot copyedit.
A hot copyedit is meant for early draft stages when you are open to various suggested edits.
Conversely, a proofread is for the later stages of writing when you want
to minimize edits and focus solely on spelling and grammar errors. The proofread
configuration also allows you to rerun `copyaid proof` multiple times; if the
source text matches the previous saved revision, it will bypass the OpenAI API request.

If you want to force a proofread request to the OpenAI API, you can run `copyaid clean`
to remove the saved revision file.
