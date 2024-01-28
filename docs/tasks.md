<!-- cbr off -->

Copy**Ai**d Tasks
=================

Copy**Ai**d performs various _tasks_ depending on the task you specify on the command line.
To view how tasks are configured, run the following command:
```
copyaid --help
```

Different tasks trigger different requests to OpenAI for revisions of source text,
or possibly no request at all.
A fundamental consideration in choosing which task to execute is the _weight_ of its request.

<!-- cbr off -->

Copyediting Weight
------------------

Copyediting weight refers to the likelihood of a request leading to revisions in the text.
A light request will tend to change little of the text,
while a heavy request will significantly alter the text.

The default task settings offer three levels of copyediting weight:

`copyaid proof`:
:   This request represents the lightest weight
    and _loosely_ corresponds to proofreading.

`copyaid light`:
:   This copyediting request will make more changes than `proof` but remains relatively light.

`copyaid heavy`:
:   This copyediting request has the highest propensity to make revisions,
    so much so that it will even revise text that has resulted from this
    request. "Copy-storming" might be an apt description for this level of
    copyediting weight.


Lastly, the `stomp` task is configured by default to use the same light weight as the
`light` task but reacts to the revisions differently by overwriting the source text
file.

### Request Weight and Copybreaks

The amount of text in a source text file, or between [copybreak lines](copybreaks.md),
will similarly influence the likelihood of revisions.
Smaller amounts of text are more likely to receive revisions per line.

<!-- cbr off -->

Task Reactions
--------------

Tasks consist of two stages: an optional _request_ stage and a _react_ stage.
Both stages operate on revisions of your source text files.
Tasks such as `proof`, `light`, `heavy`, and `stomp` will save
revisions resulting from requests made to OpenAI.

As indicated by `copyaid --help`, some tasks do not make requests.
These tasks, such as `where`,
only operate on the source and saved revision files.
The task `where` simply prints the file paths to saved revisions
of the given source file.

How a task operates on source and revision files is listed by `copyaid --help`
as _react commands_.
They are shell commands based on the file paths to source and saved revision files.

<!-- cbr off -->

Customization
-------------

Tasks are fully customizable by editing your configuration file and request prompt
settings files. You can configure new tasks or modify existing ones.
For more details, consult the [configuration reference](reference.md)
and the guide on how to [Adjust Request Settings](howto/adjust_request.md).
If you want to use LaTeX or British English, you will need to customize your request
prompts.

The reactions of tasks can also be customized.
For an example, see [How To Opt Out of Using Vimdiff](howto/notvim.md).

For more details, consult the [configuration reference page](reference.md).
