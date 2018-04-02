import dcase_util
meta_container_events = dcase_util.containers.MetaDataContainer(
    [
        {
            'filename': 'file1.wav',
            'event_label': 'speech',
            'onset': 1.0,
            'offset': 2.0,
        },
        {
            'filename': 'file1.wav',
            'event_label': 'speech',
            'onset': 2.05,
            'offset': 2.5,
        },
        {
            'filename': 'file1.wav',
            'event_label': 'speech',
            'onset': 5.1,
            'offset': 5.15,
        },
        {
            'filename': 'file1.wav',
            'event_label': 'footsteps',
            'onset': 3.1,
            'offset': 4.15,
        },
        {
            'filename': 'file1.wav',
            'event_label': 'dog',
            'onset': 2.6,
            'offset': 3.6,
        },
    ]
)
event_roll = meta_container_events.to_event_roll()

# Plot
event_roll.plot()