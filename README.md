![Alt text](https://github.com/ai-salon/SocraticAI/blob/main/static/logo.png?raw=true "AI Salon")


# SocraticAI
Codebase for transcribing and interpreting human conversations. SocraticAI was originally
developed to support modern civil discourse about transformative ideas and technologies,
like those facilitated by the [AI Salon](https://aisalon.xyz/).

## Setup

### Installation
Install the repo from source:

```pip install git+https://github.com/ai-salon/SocraticAI.git```

### Data
Audio files should be put in the "data" folder. Transcriptions and processed transcriptions will
be created in that folder and moved to outputs.

### Environment Variables
You'll need certain environment variables set:
* MODEL_TYPE: either 'openai' or 'anthropic'. Set the corresponding key below.
* (Optional) ANTHROPIC_KEY: anthropic api token, used to interpret transcripts
* (Optional) OPENAI_KEY: openai api token, used to interpret transcripts
* ASSEMBLYAI_KEY: Assembly AI api token, used to transcribe
You can set these in a '.env' file in your project.

### Configuration
Configuration is set up to automatically expect your files to be places in `data/inputs`. If
you would like a different directory then `data` change it in the configuration file.

### Spacy Setup
We use spacy for named-entity-recognition (NER) to remove names. After downloading spacy you need
to download the specific model we use to run NER.

```python -m spacy download en_core_web_lg```

### Poetry Setup and Usage
This project uses Poetry for dependency management and packaging. To get started with Poetry:

1. First, [install Poetry](https://python-poetry.org/docs/#installation) if you haven't already.

2. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/ai-salon/SocraticAI.git
cd SocraticAI
```

3. Install dependencies using Poetry:
```bash
poetry install
```

4. Activate the virtual environment:
```bash
poetry shell
```

5. Run commands within the Poetry environment:
```bash
# Instead of: poetry run SocraticAI -h
SocraticAI -h
```

Common Poetry commands:
- `poetry add package-name`: Add a new dependency
- `poetry update`: Update dependencies to their latest versions
- `poetry build`: Build the project
- `poetry env info`: Show information about the virtual environment

## Command Line Interface (CLI)

After installing the repo, you can use the CLI by calling `poetry run SocraticAI`.

For instance, to see all commands you can get help by running 

```poetry run SocraticAI -h```

- stats               Stats on repo
- full_run            Transcribe and generate_insights
- generate            Generate insights from a transcript
- generate_multi      Generate insights from multiple transcripts
- transcribe          Transcribe a single file
- transcribe_multi    Transcribe multiple files