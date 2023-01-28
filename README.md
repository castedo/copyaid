OpenAI Utilities
================

Utility [qoai.py](./qoai.py)
----------------------------

Low level utility to take
* your text file, plus
* query settings file

and then

1. "merge" them into an OpenAI GPT API query
2. query the OpenAI GPT API
3. log the request sent and response received
4. write the N text completions as N text files next to the original text file


### Example Usage

Take your file `mydoc.md` and ask OpenAI GPT to generate three revisions
per the settings of [set/multi-revise.xml](set/multi-revise.xml).

```
$ qoai.py mydoc.md --set set/multi-revise.xml
$ ls mydoc.md*
mydoc.md  mydoc.md.R1  mydoc.md.R2  mydoc.md.R3
```

Tweak the settings file to your needs: like the prompt sent to GPT, number of revisions to
generate, etc...

* [OpenAI API text completion intro](https://beta.openai.com/docs/guides/completion)
for guidance of prompt text
* [OpenAI API text completion refrence](https://beta.openai.com/docs/api-reference/models/retrieve)
for details on settings

The [set/](set/) subdirectory has example settings files for OpenAI text completion queries.


### Some [qoai.py](./qoai.py) features

* External *settings* file determine the OpenAI text completion query settings (no hard coding).
* Automatically calculates OpenAI API max token number based on ratio in settings file.
* Text returned from OpenAI is broken into separate lines to be more diff-friendly with
  the original source text given to qoai.
* OpenAI query settings can be authored in [JSOML XML](https://gitlab.com/castedo/jsoml/) (or
  JSON).  JSOML XML has a syntax that makes it convenient for reading and writing the prompt
  text while still being embedded in JSON-ish data.  The prompt text is written
  verbatim line by line without any escaping (except for the trigram `]]>`).
  An example is [set/grammar.xml](set/grammar.xml).
* Default settings file (`~/.config/qoai/set/default`)


### Installation

The `jsoml` dependency is optional.

1. copy [qoai.py](qoai.py)
2. place a file at `~/.config/qoai/openai_api_key.txt` with the contents of your OpenAI API key
3. run qoai.py for command line help
4. Email Castedo to write more documentation and improve installation!

If you want to use JSOML XML instead of JSON, install [jsoml](https://gitlab.com/castedo/jsoml):
```
python3 -m pip install git+https://gitlab.com/castedo/jsoml.git
```


Acknowledgements
----------------

Inspired and heavily influenced by:

* [manubot-ai-editor](https://github.com/greenelab/manubot-ai-editor/)
* [A publishing infrastructure for AI-assisted academic authoring](https://doi.org/10.1101/2023.01.21.525030)
