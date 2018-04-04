import dcase_util
import numpy
# Normalization factors
mel_mean = numpy.array([
    -3.26094211, -4.20447522, -4.57860912, -5.11036974, -5.33019526,
    -5.48390484, -5.50473626, -5.54014946, -5.28249358, -5.12090705,
    -5.21508926, -5.3824216, -5.37758142, -5.38829567, -5.4912112,
    -5.55352419, -5.72801733, -6.02412347, -6.41367833, -6.64073975,
    -6.80493457, -6.8717373, -6.88140949, -6.91464104, -7.00929399,
    -7.13497673, -7.36417664, -7.73457445, -8.25007518, -8.79878143,
    -9.22709866, -9.28843908, -9.57054527, -9.82846299, -9.85425306,
    -9.90253041, -9.85194976, -9.62786338, -9.38480217, -9.18478766
])
mel_std = numpy.array([
    0.3450398, 0.47330394, 0.53112192, 0.57607313, 0.66710664,
    0.70052532, 0.79045046, 0.81864229, 0.79422025, 0.76691708,
    0.64798516, 0.59340713, 0.57756029, 0.64032687, 0.70226395,
    0.75670044, 0.80861907, 0.79305124, 0.7289238, 0.75346821,
    0.77785602, 0.7350573, 0.75137917, 0.77171676, 0.80314121,
    0.78965339, 0.79256442, 0.82524546, 0.84596991, 0.76430333,
    0.69690919, 0.69591269, 0.54718615, 0.5277196, 0.61271734,
    0.54482468, 0.42716334, 0.25561558, 0.08991936, 0.06402002
])

mfcc_mean = numpy.array([
    -1.89603847e+02, 4.88930395e+01, -8.37911555e+00,
    2.58522036e+00, 4.51964497e+00, -3.87312873e-01,
    8.97250541e+00, 1.61597737e+00, 1.74111135e+00,
    2.50223131e+00, 3.03385048e+00, 1.34561742e-01,
    1.04119803e+00, -2.57486399e-01, 7.58245525e-01,
    1.11375319e+00, 5.45536494e-01, 7.62699140e-01,
    9.34355519e-01, 1.57158221e-01
])
mfcc_std = numpy.array([
    15.94006483, 2.39593761, 4.78748908, 2.39555341,
    2.66573364, 1.75496556, 2.75005027, 1.5436589,
    1.81070379, 1.39476785, 1.22560606, 1.25575051,
    1.34613239, 1.46778281, 1.19398649, 1.1590474,
    1.1309816, 1.12975486, 0.95503429, 1.01747647
])

# Define processing chain
chain = dcase_util.processors.ProcessingChain([
    {
        'processor_name': 'MonoAudioReadingProcessor',
        'init_parameters': {
            'fs': 44100
        }
    },
    {
        'processor_name': 'RepositoryFeatureExtractorProcessor',
        'init_parameters': {
            'parameters': {
                'mel': {},
                'mfcc': {}
            }
        }
    },
    {
        'processor_name': 'RepositoryNormalizationProcessor',
        'init_parameters': {
            'parameters': {
                'mel': {
                    'mean': mel_mean,
                    'std': mel_std
                },
                'mfcc': {
                    'mean': mfcc_mean,
                    'std': mfcc_std
                }
            }
        }
    },
    {
        'processor_name': 'StackingProcessor',
        'init_parameters': {
            'recipe': 'mel;mfcc=1-19'
        }
    },
    {
        'processor_name': 'AggregationProcessor',
        'init_parameters': {
            'recipe': ['flatten'],
            'win_length_frames': 5,
            'hop_length_frames': 1,
        }
    },
    {
        'processor_name': 'SequencingProcessor',
        'init_parameters': {
            'sequence_length': 50
        }
    },
])
data = chain.process(filename=dcase_util.utils.Example().audio_filename())
data.plot()