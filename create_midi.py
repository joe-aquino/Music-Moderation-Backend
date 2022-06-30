from transcribe import load_model, OnlineTranscriber
import numpy as np
from midiutil import MIDIFile
import base64, io, os
import time as timestamp
import pandas as pd
import wave
import pyaudio
import subprocess as subp
from io import BytesIO
import binascii
import soundfile

# BPM that should be set by the song user is playing
# upd 6/9/22 - this doesn't really matter because we are using seconds
# we can add a "guess_bpm" method or some shit here
BPM = 60

# chunk size
CHUNK = 512
# SET CLIENT TO PCM 16-BIT
# get information about microphone channels - MONO
CHANNELS = 1
# sampling rate
# SET CLIENT TO 16kHz
RATE = 16000

# base64 encoded string comes in as input from JSON
# DOES NOT WORK NECESSARILY
def transcribe_from_string(audio_string):
    # load model and transcriber
    model = load_model('model-180000.pt')
    transcriber = OnlineTranscriber(model, return_roll=False)
    # create a midi file to record to
    MyMIDI = MIDIFile(1)
    # set tempo of the midi file
    MyMIDI.addTempo(0, 0, BPM)
    # decode audio
    audio_bytes = base64.b64decode(audio_string)
    # create a timestamp (for file names)
    ts = timestamp.time()
    # write wav file
    audio_file_name = str(ts) + ".wav"
    # print(audio_bytes)
    with open(audio_file_name, "wb") as audio_file:
        bin_audio = binascii.a2b_base64(audio_bytes[27:])
        filebytes = BytesIO()
        filebytes.write(bin_audio)
        # Copy the BytesIO stream to the output file
        audio_file.write(filebytes.getbuffer())
    # make sure file is in correct format
    data, samplerate = soundfile.read(audio_file_name)
    soundfile.write(audio_file_name, data, 16000, subtype='PCM_16')
    # read wav file
    f = wave.open(audio_file_name, "rb")
    # create audio bytestream
    p = pyaudio.PyAudio()
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                channels = f.getnchannels(),
                rate = f.getframerate(),
                output = True)
    # read first chunk of audio
    buffer = f.readframes(CHUNK)
    frame = 0
    # iterate through the audio by chunk
    while buffer:
        # decode data from buffer
        decoded = np.array(np.frombuffer(buffer, dtype=np.int16) / 32768)
        # transcribe the audio to see what what notes came on and off
        frame_output = transcriber.inference(decoded)
        # when model detects onset of a note
        # write it into the midi file
        for pitch in frame_output[0]:
            # correct the pitch output from the model
            pitch = pitch+21
            # set time in beats to where the note should be inserted
            time = (CHUNK/RATE) * frame * BPM/60
            # insert note into midi: track? 0, instrument? 0, pitch, time in beats, 1/16 note, velocity 64
            MyMIDI.addNote(0, 0, pitch, time, 1/4, 64)
        # read next chunk
        buffer = f.readframes(CHUNK)
        frame += 1

    # close pyaudio stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # save midi file
    midi_file_name = str(ts) + ".mid"
    with open(midi_file_name, "w+b") as output_file:
        MyMIDI.writeFile(output_file)

    return midi_file_name

# this helper method takes care of alignment tool management (because it's so fucked)
def align(user_midi_file_name, reference_midi_file_name):
    # move user midi to alignment folder
    subp.run('mv ' + user_midi_file_name + ' AlignmentTool/' + user_midi_file_name, shell=True)
    # copy reference midi to alignment folder
    subp.run('cp ' + 'reference_midi/' + reference_midi_file_name + ' AlignmentTool/' + reference_midi_file_name, shell=True)
    # TODO: remove this ugly hack
    timestamp.sleep(3)
    # change directory to alignment folder and run alignment on user and reference midi
    subp.run('cd AlignmentTool/ && ./MIDIToMIDIAlign.sh ' + reference_midi_file_name[:-4] + ' ' + user_midi_file_name[:-4], shell=True)

# this hmethod converts beat length (0-1) to vexflow friendly units
def vexflow_length(beat_length):
    vf_length = 'q'
    if beat_length >= 0.03124:
        vf_length = '32'
    if beat_length >= 0.046874:
        vf_length = '32d'
    if beat_length >= 0.0624:
        vf_length = '16'
    if beat_length >= 0.09374:
        vf_length = '16d'
    if beat_length >= 0.124:
        vf_length = '8'
    if beat_length >= 0.1874:
        vf_length = '8d'
    if beat_length >= 0.24:
        vf_length = 'q'
    if beat_length >= 0.374:
        vf_length = 'qd'
    if beat_length >= 0.49:
        vf_length = 'h'
    if beat_length >= 0.74:
        vf_length = 'hd'
    if beat_length >= 0.99:
        vf_length = 'w'

    return vf_length

# this helper method cleans up the directories from generated clutter
def clean_up(user_midi_file_name, reference_midi_file_name):
    # remove wav
    wav_file_name = user_midi_file_name[:-4] + '.wav'
    subp.run('rm ' + wav_file_name, shell=True)

    # remove AlignmentTool output
    user_midi_file_name_base = user_midi_file_name[:-4]
    reference_midi_file_name_base = reference_midi_file_name[:-4]

    subp.run('rm AlignmentTool/' + user_midi_file_name_base + "_corresp.txt", shell=True)
    subp.run('rm AlignmentTool/' + user_midi_file_name_base + "_match.txt", shell=True)
    subp.run('rm AlignmentTool/' + user_midi_file_name_base + "_spr.txt", shell=True)
    subp.run('rm AlignmentTool/' + user_midi_file_name, shell=True)

    subp.run('rm AlignmentTool/' + reference_midi_file_name_base + "_fmt3x.txt", shell=True)
    subp.run('rm AlignmentTool/' + reference_midi_file_name_base + "_hmm.txt", shell=True)
    subp.run('rm AlignmentTool/' + reference_midi_file_name_base + "_spr.txt", shell=True)
    subp.run('rm AlignmentTool/' + reference_midi_file_name, shell=True)

# right now reference midi file name = None and it WILL crash when executed
def extract_errors(user_midi_file_name, reference_midi_file_name="reference_1octave_up.mid"):
    # run alignment tool
    align(user_midi_file_name, reference_midi_file_name)
    # load tables into pandas
    corresp_file_name = 'AlignmentTool/' + user_midi_file_name[:-4] + "_corresp.txt"
    corresp_header = ["id", "onset_time", "spelled_pitch", "integer_pitch", "onset_velocity", "reference_id",
                "reference_onset_time", "reference_spelled_pitch", "reference_integer_pitch", "reference_onset_velocity", "blank"]
    corresp_data = pd.read_csv(corresp_file_name, sep='\t', skiprows=[0], names=corresp_header, index_col=0)

    match_file_name = 'AlignmentTool/' + user_midi_file_name[:-4] + "_match.txt"
    match_header = ["id", "onset_time", "offset_time", "spelled_pitch", "onset_velocity",
                "offset_velocity", "channel", "match_status", "score_time", "note_id",
                "error_index", "skip_index"]
    match_data = pd.read_csv(match_file_name, sep='\t', skiprows=[0,1,2,3], names=match_header, index_col=0)[:-2]

    spr_file_name = 'AlignmentTool/' + reference_midi_file_name[:-4] + "_spr.txt"
    spr_header = ["id", "onset_time", "offset_time", "spelled_pitch", "onset_velocity", "other_velocity", "null"]
    spr_data = pd.read_csv(spr_file_name, sep='\t', skiprows=[0], names=spr_header, index_col=0)
    spr_data['time_diff'] = spr_data.offset_time - spr_data.onset_time

    # this has to be a dictionary of all notes - pitches and time (reference + mistakes)
    # return format:
    # bpm
    # timesig
    # notes: [
    #     measure
    #     pitch_integer
    #     pitch_spelled
    #     onset_time -> seconds from start of measure
    #     length -> note length (like "q", vexflow format)
    #     note_type -> "extra, missing, incorrect, reference"
    # ]

    reference_bpm = 60 # should come from midi, temporarily hardcoded
    reference_timesig_numerator = 4 # should come from midi, temporarily hardcoded
    reference_timesig_denominator = 4 # should come from midi, temporarily hardcoded
    # measure is time / beats per second * reference_timesig_numerator
    measure_func = lambda time : time // (reference_bpm / 60 * reference_timesig_numerator)

    # this is the return array that will be sent to frontend for display with VexFlow
    performance_data = {
        'bpm': reference_bpm,
        'timesig': str(reference_timesig_numerator) + "/" + str(reference_timesig_denominator),
        'notes': []
    }

    # iterate through the user submitted notes
    for idx, row in corresp_data.iterrows():
        # get note info
        pitch_played_spelled = None
        pitch_integer = row['reference_integer_pitch']
        pitch_spelled = row['reference_spelled_pitch']
        onset_time = row['reference_onset_time']
        measure = measure_func(onset_time)
        note_type = "reference"
        length = None

        # check if a pause exists
        if idx != '*' and row['reference_id'] != '*':
            if int(idx) >= 1 and int(row['reference_id']) >= 1:
                # get data about notes
                last_onset = None
                last_offset = None
                current_onset = None

                # the reason why this code is so complex (and generally
                # everything that involves spr_data) is because offset
                # values are stored in there and have to be retrieved
                # through these ridiculous manipulations

                # if current note is a chord, grab one note from it
                if type(spr_data.iloc[int([row['reference_id']][0])]["onset_time"]) == 'list':
                    current_onset = spr_data.iloc[int([row['reference_id']][0])]["onset_time"].values[0]
                else:
                    current_onset = spr_data.iloc[int([row['reference_id']][0])]["onset_time"]

                # if last note is a chord, grab one note from it
                if type(spr_data.iloc[int([row['reference_id']][0])-1]["offset_time"]) == 'list':
                    last_offset = spr_data.iloc[int([row['reference_id']][0])-1]["offset_time"].values[0]
                    last_onset = spr_data.iloc[int([row['reference_id']][0])-1]["onset_time"].values[0]
                else:
                    last_offset = spr_data.iloc[int([row['reference_id']][0])-1]["offset_time"]
                    last_onset = spr_data.iloc[int([row['reference_id']][0])-1]["onset_time"]

                # get time between the notes
                time_diff = current_onset - last_offset
                # if there is time - there is a pause!
                if time_diff > 0:
                    # calculate pause length
                    pause_beat_length = (time_diff / ((reference_bpm / reference_timesig_numerator) / 60)) / 4 / 4
                    pause_length = vexflow_length(pause_beat_length) + 'r'
                    # generate the pause
                    pause = {
                        'measure': measure,
                        'pitch_integer': 0,
                        'pitch_spelled': 'B4',
                        'pitch_played_spelled': 'B4',
                        'onset_time': last_onset+0.01,
                        'length': pause_length,
                        'note_type': 'pause'
                        }

                    # push pause to note array
                    # UNCOMMENT WHEN FRONTEND CAN HANDLE PAUSES
                    performance_data['notes'].append(pause)

        # get note length if reference exists
        if row['reference_id'] != '*':
            time_length = spr_data.iloc[int(row['reference_id'])+1]["time_diff"]
            # beat_length = time_length / measures per second
            # measures per minute = bpm / time signature numerator
            # measure per second = measures per minute / 60 seconds
            # / 4 is an UGLY HACK
            beat_length = (time_length / ((reference_bpm / reference_timesig_numerator) / 60)) / 4 / 4
            length = vexflow_length(beat_length)

        # process extra notes
        if row['reference_id'] == '*':
            note_type = "extra"
            pitch_integer = row['integer_pitch']
            pitch_spelled = row['spelled_pitch']
            # TODO: remove this ugly hack
            # if first note is extra, just assing it default onset time
            if len(performance_data['notes']) > 0:
                onset_time = performance_data['notes'][-1]['onset_time'] + 0.01
            else:
                onset_time = row['onset_time']
            # uncomment to see extra notes (my - Peter's - digital piano is trash
            # and it looks awful in my current setup)
            # measure = measure_func(onset_time)
            length = 'q'
        # process missing notes
        elif idx == '*':
            note_type = "missing"
        # process incorrect pitch
        elif match_data.iloc[[idx]]["error_index"].values[0] == 1:
            note_type = "incorrect"
            pitch_played_spelled = match_data.iloc[[idx]]['spelled_pitch'].values[0]

        # remove if first notes of the piece break
        if onset_time == 0.0 and note_type == "missing":
            note_type = "reference"

        note = {
            'measure': measure,
            'pitch_integer': pitch_integer,
            'pitch_spelled': pitch_spelled,
            'pitch_played_spelled': pitch_played_spelled,
            'onset_time': onset_time,
            'length': length,
            'note_type': note_type
        }

        performance_data['notes'].append(note)

    # remove generated file garbage
    clean_up(user_midi_file_name, reference_midi_file_name)

    # capitalize first letter   
    for dic in performance_data['notes']:
        dic['pitch_spelled'] = dic['pitch_spelled'].capitalize()

    # sort notes of dictionary by onset time and pitch
    performance_data['notes'].sort(key=lambda x: (x['onset_time'], x['pitch_integer']))

    return performance_data

