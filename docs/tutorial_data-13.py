import dcase_util
# Metadata
meta = dcase_util.containers.MetaDataContainer([
    {
        'filename': 'test1.wav',
        'event_label': 'cat',
        'onset': 1.0,
        'offset': 3.0
    },
    {
        'filename': 'test1.wav',
        'event_label': 'dog',
        'onset': 2.0,
        'offset': 6.0
    },
    {
        'filename': 'test1.wav',
        'event_label': 'speech',
        'onset': 5.0,
        'offset': 8.0
    },
])

# Initilize encoder
event_roll_encoder = dcase_util.data.EventRollEncoder(
    label_list=meta.unique_event_labels,
    time_resolution=0.02
)

# Encode
event_roll = event_roll_encoder.encode(
    metadata_container=meta,
    length_seconds=10.0
)

# Visualize
event_roll.plot()