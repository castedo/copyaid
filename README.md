co<i>py</i><b>AI</b>d
=====================

Perform copyediting and proofreading with the OpenAI (GPT) API from the command line.

Visit [copyaid.it](https://copyaid.it) for documentation.

Technical Details
-----------------

Documentation is built from the `copyaid.it` branch of this repository.

Some notable features of CopyAId are:

* White space returned from OpenAI is adjusted to be more diff-friendly with
  the original source text.
* Automatic calculation of API max token number based on ratio in settings file.
* Logs the API request sent and response received.
