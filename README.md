OpenAI Utilities
================


Example Setting for OpenAI text complection queries
---------------------------------------------------

See [set/](set/) subdirectory.



Utility [qoai.py](./qoai.py)
----------------------------

Some features and implementation details that might be of interest:

* External files determine the OpenAI text completion query settings (no hard coding).
* Each output sentence written on its own line, using the [NLTK Python
  library](https://www.nltk.org/).
* OpenAI query settings can be authored in [JSOML](https://gitlab.com/castedo/jsoml/) (or
  JSON).  JSOML has a syntax that makes it convenient for reading and writing the prompt
  text while still being embedded in JSON-ish data.  The prompt text is written
  verbatim line by line without any escaping (except for the trigram `]]>`).
  An example is [set/grammar.xml](set/grammar.xml).

### Installation

The `jsoml` and `nltk` dependencies are optional.

Place a file at `~/.config/openai/api_key.txt` with the contents of your OpenAI API key.

Copy [qoai.py](qoai.py) and run for instructions.



Acknowledgements
----------------

Inspired and heavily influenced by:

* [manubot-ai-editor](https://github.com/greenelab/manubot-ai-editor/)
* [manubot-gpt-manuscript](https://greenelab.github.io/manubot-gpt-manuscript/)
