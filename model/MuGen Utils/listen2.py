import mido

# Load the MIDI file
input_midi = "standard.mid"  # Change to your actual MIDI file
output_midi = "standard_fixed.mid"

mid = mido.MidiFile(input_midi)

# Define the correct program assignments
program_changes = {
    0: 54,  # Channel 0 -> Sound 54
    1: 17,  # Channel 1 -> Sound 17
    3: 53,  # Channel 3 -> Sound 53
    4: 94,  # Channel 4 -> Sound 94
    5: 46   # Channel 5 -> Sound 46
}

for track in mid.tracks:
    new_events = []
    for msg in track:
        new_events.append(msg)  # Keep original messages

        # If this is a program change, insert a bank select message before it
        if msg.type == 'program_change' and msg.channel in program_changes:
            # Ensure the correct program is set
            new_events.append(mido.Message('control_change', channel=msg.channel, control=0, value=0))  # Bank Select MSB
            new_events.append(mido.Message('program_change', channel=msg.channel, program=program_changes[msg.channel]))  

    track[:] = new_events  # Update track with new messages

# Save the modified MIDI file
mid.save(output_midi)
print(f"Fixed MIDI saved as: {output_midi}")
