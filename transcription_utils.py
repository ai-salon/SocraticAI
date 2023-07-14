import os

from pyannote.core import Annotation, Segment, Timeline
from pydub import AudioSegment


def get_text_with_timestamp(transcribe_res):
    timestamp_texts = []
    for item in transcribe_res["segments"]:
        start = item["start"]
        end = item["end"]
        text = item["text"]
        timestamp_texts.append((Segment(start, end), text))
    return timestamp_texts


def add_speaker_info_to_text(timestamp_texts, ann=None):
    spk_text = []
    for seg, text in timestamp_texts:
        if ann is None:
            spk = "NONE"
        else:
            spk = ann.crop(seg).argmax()
        spk_text.append((seg, spk, text))
    return spk_text


def merge_cache(text_cache):
    sentence = "".join([item[-1] for item in text_cache])
    spk = text_cache[0][1]
    start = text_cache[0][0].start
    end = text_cache[-1][0].end
    return Segment(start, end), spk, sentence


PUNC_SENT_END = [".", "?", "!"]


def merge_sentence(spk_text):
    merged_spk_text = []
    pre_spk = None
    text_cache = []
    for seg, spk, text in spk_text:
        if spk != pre_spk and pre_spk is not None and len(text_cache) > 0:
            merged_spk_text.append(merge_cache(text_cache))
            text_cache = [(seg, spk, text)]
            pre_spk = spk

        elif text[-1] in PUNC_SENT_END:
            text_cache.append((seg, spk, text))
            merged_spk_text.append(merge_cache(text_cache))
            text_cache = []
            pre_spk = spk
        else:
            text_cache.append((seg, spk, text))
            pre_spk = spk
    if len(text_cache) > 0:
        merged_spk_text.append(merge_cache(text_cache))
    return merged_spk_text


def diarize_text(transcribe_res, diarization_result):
    timestamp_texts = get_text_with_timestamp(transcribe_res)
    spk_text = add_speaker_info_to_text(timestamp_texts, diarization_result)
    res_processed = merge_sentence(spk_text)
    return res_processed


def write_to_txt(spk_sent, file):
    with open(file, "w") as fp:
        for seg, spk, sentence in spk_sent:
            line = f"{seg.start:.2f} {seg.end:.2f} {spk} {sentence}\n"
            fp.write(line)


# Basic Audio utils #


def slice_audio(input_filename, output_filename, start_time, end_time):
    # Time to miliseconds
    start_time = start_time * 1000
    end_time = end_time * 1000

    # Load audio file
    audio = AudioSegment.from_file(input_filename)

    # Slice audio
    sliced_audio = audio[start_time:end_time]

    # Export sliced audio
    sliced_audio.export(output_filename, format="wav")


def is_wav_file(file_path):
    # Check file extension
    if file_path.lower().endswith((".wav")):
        return True

    return False


def convert_m4a_to_wav(input_filename):
    if is_wav_file(input_filename):
        return input_filename
    output_filename = os.path.splitext(input_filename)[0] + ".wav"
    audio = AudioSegment.from_file(input_filename, format="m4a")
    audio.export(output_filename, format="wav")
    return output_filename
