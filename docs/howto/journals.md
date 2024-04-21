<!-- copybreak off -->

How to Comply with Journal Policies
===================================

Journals have varying Large Language Model (LLM) policies,
many of which have changed since 2023
to clarify the acceptable use of LLMs.
This guide explains how to comply with the policies of a specific example:
[the journal GENETICS](https://academic.oup.com/genetics).
The LLM policy of this journal is representative of many others in 2024.
Like many other journals,
[GENETICS requires disclosure of how an LLM is used](
https://academic.oup.com/genetics/pages/general-instructions#ManuscriptPreparation
):

> Manuscript Preparation
>
> ...
>
> Materials and Methods
>
> ...
>
> If you have used Large Language Models (LLMs), such as ChatGPT, please provide full
> technical specifications of the LLM used (name, version, model, source) and method of
> application (query structure, syntax).

<!-- copybreak off -->

## Request Settings Files

When you run a CopyAid task to edit a file,
you use a *request settings file*.
This file provides a full technical specification of the LLM used.
The `chat_system` setting within this file is the system message used in the request
query sent to an LLM service, such as OpenAI.
The query structure consists of this system message followed by the text to be edited.


Most users will simply use the request settings files included in the CopyAid Python
package. Some may opt for [customized request settings](adjust_request.md).
Regardless,
executing `copyaid --help` will reveal which CopyAid tasks correspond to which request settings
files.

### Packaged Request Settings

CopyAid 0.7 includes three request setting files.
The permalinks to these files in the Software Heritage Archive are:

* [`proofread.toml`](https://archive.softwareheritage.org/swh:1:cnt:3abfe022b8737201b0703e3a60713e2f0f1d369f;origin=https://pypi.org/project/copyaid/;visit=swh:1:snp:514f46e925dab625126e86cedbcb4dacefcaf8ed;anchor=swh:1:rel:b315578d707c6e67e2917154cd8a3640523c742e;path=/copyaid-0.7.1/copyaid/config/proofread.toml)
* [`light.toml`](https://archive.softwareheritage.org/swh:1:cnt:f952774f53fa63bd4aa07b430b4b52ec1849457e;origin=https://pypi.org/project/copyaid/;visit=swh:1:snp:514f46e925dab625126e86cedbcb4dacefcaf8ed;anchor=swh:1:rel:b315578d707c6e67e2917154cd8a3640523c742e;path=/copyaid-0.7.1/copyaid/config/light.toml)
* [`heavy.toml`](https://archive.softwareheritage.org/swh:1:cnt:2e7f1e0152133fbc843d91c523e85f290373690a;origin=https://pypi.org/project/copyaid/;visit=swh:1:snp:514f46e925dab625126e86cedbcb4dacefcaf8ed;anchor=swh:1:rel:b315578d707c6e67e2917154cd8a3640523c742e;path=/copyaid-0.7.1/copyaid/config/heavy.toml)


<!-- copybreak on -->

## Optional Disclosures

Some journals may require or be interested in additional disclosures.
Three potential options include:

1. Edits suggested by the request settings files for a reference example of text,
2. Git history of commits made to the source text by the author, and
3. History of edits suggested by CopyAid on past drafts.

Based on personal communications with the managing editor of a journal,
the first option is considered more useful than the latter two.
A concern with the latter two options is the potential confusion that may arise from
examining changes to drafts prior to submission versus changes to the manuscript after
submission.
Personal experience using CopyAid suggests that an exhaustive history of all suggested edits
would be akin to an exhaustive list of spelling/grammar auto-corrections
from text editor software.

<!-- copybreak off -->

## Example Journal LLM Policies

* <https://academic.oup.com/genetics/pages/general-instructions>
* <https://www.science.org/content/blog-post/change-policy-use-generative-ai-and-large-language-models>
* <https://www.pnas.org/post/update/pnas-policy-for-chatgpt-generative-ai>
* <https://icml.cc/Conferences/2023/llm-policy>


## Reference Example Edits by Packaged Request Settings Files

The request settings files included in the CopyAid 0.7 package are the result of analyses
from automated testing. The following examples are from this testing, which used
the lead sections of the Wikipedia articles on Earth and Antarctica around the time they
were designated as Wikipedia Featured Articles.

* <a href="https://gitlab.com/castedo/copyblast/-/tree/main/inputs/wikipara-md">Example text to edit</a>
* <a href="https://gitlab.com/castedo/copyblast/-/tree/main/sys2b/proof-fm-doc-f2-us-e1/out1/wikipara-md">Revision by proofread.toml</a>
* <a href="https://gitlab.com/castedo/copyblast/-/tree/main/sys2b/cpydt-fm-doc-f2-us-e1/out1/wikipara-md">Revision by light.toml</a>
* <a href="https://gitlab.com/castedo/copyblast/-/tree/main/sys2b/impr-fm-doc-f2-us-e1/out1/wikipara-md">Revision by heavy.toml</a>


## Acknowledgements

These guidelines were motivated by questions arising from Manubot AI Editor
(Pividori M, Greene CS. A publishing infrastructure for AI-assisted academic authoring.
bioRxiv. 2023. [doi:10.1101/2023.01.21.525030](https://doi.org/10.1101/2023.01.21.525030)).

