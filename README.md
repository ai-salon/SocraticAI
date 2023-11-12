![Alt text](https://github.com/IanEisenberg/ChatDigest/blob/main/static/AI_Salon.png?raw=true "AI Salon")


# ChatDigest
Codebase for transcribing and interpreting human conversations. ChatDigest was originally
developed to support modern civil discourse about transformative ideas and technologies,
like those facilitated by the [AI Salon](https://lu.ma/Ai-salon).


## Setup

### Data
Audio files should be put in the "data" folder. Transcriptions and processed transcriptions will
be created in that folder and moved to outputs.

### Environment Variables
You'll need certain environment variables set:
* ANTHROPIC_KEY: anthropic api token, used to interpret transcripts
* ASSEMBLYAI_KEY: Assembly AI api token, used to transcribe

### Configuration
Configuration is set up to automatically expect your files to be places in `data/inputs`. If
you would like a different directory then `data` change it in the configuration file.

### Spacy Setup
We use spacy for named-entity-recognition (NER) to remove names. After downloading spacy you need
to download the specific model we use to run NER.

```python -m spacy download en_core_web_lg```