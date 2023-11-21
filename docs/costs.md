Costs of Using the OpenAI API
=============================

OpenAI API pricing operates on a "pay for what you use" basis, rather than a fixed monthly plan.
The cost of using Copy**AI**d primarily depends on the following factors:

* The length of the source text file you are copyediting,
* The GPT model specified in the request settings file, and
* The proportion of your requests that return with no edits.

The default request settings installed by `copyaid init` use the GPT-4 Turbo model `gpt-4-1106-preview`.
You can expect to spend approximately $0.02 to $0.04 per thousand words using GPT-4 Turbo.

Alternatively, you may opt for the cheaper GPT-3 Turbo model,
as demonstrated by [this example request settings file](examples/cold-revise-gpt3.toml).
However, copyediting with GPT-3 may result in lower quality,
and changes in the request text can lead to surprising and unpredictable drops in response quality.
The cost is around $0.005 per thousand words using GPT-3.

As of late 2023, Copy**AI**d sends the *entire* file.
If you are using LaTeX,
consider breaking large files into smaller files and using the `\input` macro.
For Markdown files, different Markdown flavors have various methods for
combining multiple smaller source files into a single output document.

For more details on API pricing, visit the [OpenAI Pricing page](https://openai.com/pricing).
