![Alt text](https://github.com/IanEisenberg/SocraticAI/blob/main/static/AI_Salon.png?raw=true "AI Salon")


# SocraticAI
Codebase for transcribing and interpreting human conversations. SocraticAI was originally
developed to support modern civil discourse about transformative ideas and technologies,
like those facilitated by the [AI Salon](https://lu.ma/Ai-salon).


## Setup

### Installation
Install the repo from source:

```pip install git+https://github.com/IanEisenberg/SocraticAI.git```

### Data
Audio files should be put in the "data" folder. Transcriptions and processed transcriptions will
be created in that folder and moved to outputs.

### Environment Variables
You'll need certain environment variables set:
* ANTHROPIC_KEY: anthropic api token, used to interpret transcripts
* ASSEMBLYAI_KEY: Assembly AI api token, used to transcribe
You can set these in a '.env' file in your project.

### Configuration
Configuration is set up to automatically expect your files to be places in `data/inputs`. If
you would like a different directory then `data` change it in the configuration file.

### Spacy Setup
We use spacy for named-entity-recognition (NER) to remove names. After downloading spacy you need
to download the specific model we use to run NER.

```python -m spacy download en_core_web_lg```

## Command Line Interface (CLI)

You can install the repo in your python environment with:
`pip install -e .` if you are in the parent directory.

After installing the repo, you can use the CLI by calling `SocraticAI`.

For instance, to see all commands you can get help by running 

```SocraticAI -h```

- stats               Stats on repo
- full_run            Transcribe and generate_insights
- generate            Generate insights from a transcript
- generate_multi      Generate insights from multiple transcripts
- transcribe          Transcribe a single file
- transcribe_multi    Transcribe multiple files