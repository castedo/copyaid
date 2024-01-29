<!-- cbr off -->

Costs of Using the OpenAI API
=============================

OpenAI API pricing operates on a "pay for what you use" basis, rather than a fixed monthly plan.
The cost of using Copy**Ai**d primarily depends on the amount of

* text in your source text files, or
* text enabled by [copybreaks](copybreaks.md) inserted into your source text files.

The default request settings (as of version 0.7) use the GPT-4 Turbo model `gpt-4-0125-preview`.
You can expect to spend approximately $0.04 per thousand words using GPT-4 Turbo.

<!-- cbr off -->

As of early 2024, Copy**Ai**d will send *entire* files
in the absence of any [copybreak lines](copybreaks.md).
To save money and achieve better copyediting performance,
use [copybreak lines](copybreaks.md) and/or divide large files into smaller ones,
such as by using the `\input` macro in LaTeX.

Alternatively, you may opt for the cheaper GPT-3 Turbo model,
as demonstrated by [this example request settings file](examples/cold-revise-gpt3.toml).
However, copyediting with GPT-3 will likely result in lower quality,
and changes in the request text can lead to surprising and unpredictable drops in response quality.
The cost is around $0.005 per thousand words using GPT-3.

<!-- cbr off -->

For more details on API pricing, visit the [OpenAI Pricing page](https://openai.com/pricing).
Note that Copy**Ai**d will incur the input cost of sending the source text
plus the ouput cost of any revision text, if edits are made.
