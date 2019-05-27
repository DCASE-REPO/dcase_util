import dcase_util
import tempfile
tmp = tempfile.NamedTemporaryFile('r+', suffix='.txt',delete=False)
dcase_util.utils.Example.event_metadata_container().save(filename=tmp.name)

# Define processing chain
chain = dcase_util.processors.ProcessingChain([
    {
        'processor_name': 'dcase_util.processors.MetadataReadingProcessor',
        'init_parameters': {}
    },
    {
        'processor_name': 'dcase_util.processors.EventRollEncodingProcessor',
        'init_parameters': {
            'label_list': dcase_util.utils.Example.event_metadata_container().unique_event_labels,
            'time_resolution': 0.02,
        }
    }
])

# Do the processing
data = chain.process(
    filename=tmp.name,
    focus_filename='test1.wav'
)

# Plot data
data.plot()