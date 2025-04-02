import mido

# Load the MIDI file
midi_path = "standard.mid"  # Ensure the correct path
mid = mido.MidiFile(midi_path)

# Extract program changes and channel usage
channel_programs = {}
channel_usage = set()

for track in mid.tracks:
    for msg in track:
        if msg.type == 'program_change':
            channel_programs[msg.channel] = msg.program
        if msg.type in ['note_on', 'note_off']:
            channel_usage.add(msg.channel)

# Display findings
print("Detected program changes per channel:", channel_programs)
print("Channels used in the MIDI:", channel_usage)
print("Number of tracks:", len(mid.tracks))
