<!-- cbr off -->

Costs of Using the OpenAI API
=============================

OpenAI API pricing operates on a "pay for what you use" basis, rather than a fixed monthly plan.
The cost of using Copy**Ai**d primarily depends on the amount of

* text in your source text files, or
* text enabled by [copybreaks](copybreaks.md) inserted into your source text files.

The default request settings (as of version 0.8) use the GPT-4.1 model `gpt-4.1`.
You can expect to spend approximately $0.01 per thousand words using GPT-4.1.

<!-- cbr off -->

Copy**Ai**d will send *entire* files
in the absence of any [copybreak lines](copybreaks.md).
To achieve better copyediting performance and save money,
use [copybreak lines](copybreaks.md) and/or divide large files into smaller ones,
such as by using the `\input` macro in LaTeX.

<!-- cbr off -->

For more details on API pricing, visit the [OpenAI API pricing
page](https://platform.openai.com/docs/pricing).
Note that Copy**Ai**d will incur the input cost of sending the source text
plus the ouput cost of any returned revised text.
