import os
from glob import glob

from ChatDigest.interpret.insights import run_insight_generation
from ChatDigest.interpret.process import process_file
from ChatDigest.interpret.utils import expansion_to_string

for file_path in glob("data/*transcript.txt"):
    # process if the file hasn't been processed yet, otherwise load
    processed_file_path = file_path.replace(".txt", "_processed.txt")
    if not os.path.exists(processed_file_path):
        print(f"Processing {file_path}...")
        text = process_file(file_path)
    else:
        print(f"Loading {processed_file_path}...")
        with open(processed_file_path, "r") as f:
            text = f.read()

    # generate insights and "blogs"
    print("Generating insights...")
    blogs = run_insight_generation(text, model="claude-2")

    # save expansions to file in output folder
    print("Saving expansions...")
    expansion_string = expansion_to_string(blogs)
    basename = os.path.basename(file_path)
    output_path = os.path.join(
        "output", basename.replace("transcript_processed", "insights")
    )
    with open(output_path, "w") as f:
        f.write(expansion_string)
