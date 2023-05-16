co<i>py</i><b>AI</b>dit
=======================

Perform copyediting and proofreading
 with the OpenAI (GPT) API from the command line.

Utility [`copyaidit.py`](./copyaidit.py), a single Python file, takes:

* your text file, plus
* a query settings file

and then

1. merges them into an OpenAI API query,
2. queries the OpenAI API service, and
3. writes the (one or more) response choices to text files in separate subdirectories.

#### Notable features

* White space returned from OpenAI is adjusted to be more diff-friendly with
  the original source text.
* Automatic calculation of API max token number based on ratio in settings file.
* Logs the API request sent and response received.


## Example usage

Take your file `mydoc.md` and ask OpenAI GPT to generate three revisions
per the query settings of [set/multi-revise.xml](set/multi-revise.xml).

```
$ copyaidit.py mydoc.md --set set/multi-revise.xml
$ ls R*/mydoc.md
R1/mydoc.md  R2/mydoc.md  R3/mydoc.md
```

Tweak the query settings file to your needs:
 like the prompt sent to GPT, temperature, number of revisions to generate, etc...

* [OpenAI Chat API intro](https://platform.openai.com/docs/guides/chat)
for guidance of prompt text
* [OpenAI API reference](https://platform.openai.com/docs/api-reference/chat)
for details on query settings.


## Example query settings files

The [set/](set/) subdirectory has example query settings files for OpenAI API queries.


## Setup

1. `pip install openai`
2. sign up to use the OpenAI API (the API, not ChatGPT)
3. store your OpenAI API key in a file at `~/.config/qoai/openai_api_key.txt`
4. copy [`copyaidit.py`](./copyaidit.py) to your system
5. run copyaidit.py for command line help
6. Email Castedo to write more documentation and improve installation!


### Optional features

#### Default query settings file

Optionally store a default query settings file at `~/.config/qoai/set/default`.


#### JSOML

Query settings files can be in ubiquitous JSON format
 or niche [JSOML XML](https://gitlab.com/castedo/jsoml/) format.
Long prompts of many lines are easier to read and edit in JSOML format.
Prompt text is written verbatim without any escaping (except for the trigram `]]>`).
For examples, see the `.xml` files in the [set/](set/) subdirectory.

If you want to use JSOML XML instead of JSON, install the jsoml Python package:
```
pip install jsoml
```
For documentation on JSOML visit [gitlab.com/castedo/jsoml](https://gitlab.com/castedo/jsoml).


## FAQ

<dl>

<dt>Does it work with LaTeX files?</dt>
<dd>Yes.</dd>

<dt>Does it work with markdown?</dt>
<dd>Yes.</dd>

<dt>Does it work with Word documents?</dt>
<dd>Probably not.</dd>

</dl>


Acknowledgements
----------------

Inspired and heavily influenced by:

* [manubot-ai-editor](https://github.com/greenelab/manubot-ai-editor/)
* [A publishing infrastructure for AI-assisted academic authoring](https://doi.org/10.1101/2023.01.21.525030)
