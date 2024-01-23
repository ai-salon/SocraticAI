import os
from glob import glob

from ChatDigest.utils import get_data_directory

processed_dir = get_data_directory("processed")
processed_transcripts = glob(os.path.join(processed_dir, "*_processed_anon.txt"))

# combine processed transcripts into one file
final_text = ""
for transcript_file in processed_transcripts:
    salon_title = os.path.basename(transcript_file).split("_")[0]
    with open(transcript_file, "r") as f:
        text = f.read()
        final_text += f"#{salon_title}\n---------------------------\n\n{text}\n\n\n"

# write final_text
agent_dir = get_data_directory("agent_inputs")
final_path = os.path.join(agent_dir, "all_processed.txt")
with open(final_path, "w") as f:
    f.write(final_text)
