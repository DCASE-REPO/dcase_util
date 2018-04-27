#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dcase_util
dcase_util.utils.setup_logging()

import numpy
import os
import sed_eval
from sklearn.mixture import GaussianMixture


def audio_filename_to_feature_filename(audio_filename, feature_path, feature_label):
    return os.path.join(
        feature_path,
        os.path.split(audio_filename)[1].replace('.wav', '.' + feature_label + '.cpickle')
    )


log = dcase_util.ui.FancyLogger()
log.title('Audio Tagging Example / GMM')
log.line()

# Get dataset class and initialize it
db = dcase_util.datasets.CHiMEHome_DomesticAudioTag_DevelopmentSet(
    data_path='datasets'
)
db.initialize()

overwrite = False

param = dcase_util.containers.ParameterContainer({
    'flow': {
      'feature_extraction': True,
      'feature_normalization': True,
      'learning': True,
      'testing': True,
      'evaluation': True
    },
    'path': {
        'features': os.path.join('systems', 'TAG_GMM', 'features'),
        'normalization': os.path.join('systems', 'TAG_GMM', 'normalization'),
        'models': os.path.join('systems', 'TAG_GMM', 'models'),
        'results': os.path.join('systems', 'TAG_GMM', 'results'),
    },
    'feature_extraction': {
        'fs': 16000,
        'win_length_seconds': 0.04,
        'hop_length_seconds': 0.02,
        'spectrogram_type': 'magnitude',
        'window_type': 'hann_symmetric',
        'n_mels': 40,                       # Number of MEL bands used
        'n_mfcc': 14,
        'n_fft': 2048,                      # FFT length
        'fmin': 0,                          # Minimum frequency when constructing MEL bands
        'fmax': 16000,                      # Maximum frequency when constructing MEL band
        'htk': True,                        # Switch for HTK-styled MEL-frequency equation
    },
    'feature_stacking': {
        'recipe': 'mfcc=1-13',
    },
    'learner': {
        'covariance_type': 'diag',
        'init_params': 'kmeans',
        'max_iter': 40,
        'n_components': 8,
        'n_init': 1,
        'random_state': 0,
        'reg_covar': 0,
        'tol': 0.001
    },
    'recognizer': {
        'binarization': {
            'threshold': 200,
        },
        'probability_collapsing': {
          'window_length': 1.0,     # seconds
        },
        'event_post_processing': {
            'minimum_event_length': 0.1,    # seconds
            'minimum_event_gap': 0.1        # seconds
        }
    }
})

# Make sure all paths exists
dcase_util.utils.Path().create(list(param['path'].values()))

# Expand the feature recipe
param.set_path(
    path='feature_stacking.recipe',
    new_value=dcase_util.utils.VectorRecipeParser().parse(param.get_path('feature_stacking.recipe'))
)
feature_label_list = param.get_path('feature_stacking.recipe').get_field('label')

# Feature extraction
if param.get_path('flow.feature_extraction'):
    log.section_header('Feature Extraction')

    # Prepare feature extractor
    extractors = {
        'mfcc': dcase_util.features.MfccStaticExtractor(**param['feature_extraction'])
    }

    # Loop over all audio files in the dataset and extract features for them.
    for audio_filename in db.audio_files:
        log.line(os.path.split(audio_filename)[1], indent=4)

        for feature_label in feature_label_list:
            # Get filename for feature data from audio filename
            feature_filename = audio_filename_to_feature_filename(
                audio_filename=audio_filename,
                feature_path=param.get_path('path.features'),
                feature_label=feature_label,
            )

            if not os.path.isfile(feature_filename) or overwrite:
                # Load audio data
                audio = dcase_util.containers.AudioContainer().load(
                    filename=audio_filename,
                    mono=True,
                    fs=param.get_path('feature_extraction.fs')
                )

                # Extract features and store them into FeatureContainer, and save it to the disk
                features = dcase_util.containers.FeatureContainer(
                    filename=feature_filename,
                    data=extractors[feature_label].extract(audio.data),
                    time_resolution=param.get_path('feature_extraction.hop_length_seconds')
                ).save()

    log.foot()

# Feature normalization
if param.get_path('flow.feature_normalization'):
    log.section_header('Feature Normalization')

    # Loop over all cross-validation folds and calculate mean and std for the training data
    for fold in db.folds():
        log.line('Fold {fold:d}'.format(fold=fold), indent=4)

        for feature_label in feature_label_list:
            # Get filename for the normalization factors
            fold_stats_filename = os.path.join(param.get_path('path.normalization'), 'norm_fold_{fold:d}.{feature_label}.cpickle'.format(
                fold=fold, feature_label=feature_label
            ))

            if not os.path.isfile(fold_stats_filename) or overwrite:
                normalizer = dcase_util.data.Normalizer(filename=fold_stats_filename)

                # Loop through all training data
                for item in db.train(fold=fold):
                    # Get feature filename
                    feature_filename = audio_filename_to_feature_filename(
                        audio_filename=item.filename,
                        feature_path=param.get_path('path.features'),
                        feature_label=feature_label
                    )

                    # Load feature matrix
                    features = dcase_util.containers.FeatureContainer().load(
                        filename=feature_filename
                    )

                    # Accumulate statistics
                    normalizer.accumulate(features.data)

                # Finalize and save
                normalizer.finalize().save()

    log.foot()

# Learning
if param.get_path('flow.learning'):
    log.section_header('Learning')

    # Loop over all cross-validation folds and learn acoustic models
    for fold in db.folds():
        log.line('Fold {fold:d}'.format(fold=fold), indent=4)

        # Get model filename
        fold_model_filename = os.path.join(param['path']['models'], 'model_fold_{fold:d}.cpickle'.format(fold=fold))

        if not os.path.isfile(fold_model_filename) or overwrite:
            normalizer_filenames = {}
            for feature_label in feature_label_list:
                # Get filename for the normalization factors
                normalizer_filenames[feature_label] = os.path.join(param.get_path('path.normalization'),'norm_fold_{fold:d}.{feature_label}.cpickle'.format(
                    fold=fold, feature_label=feature_label))

            repo_normalizer = dcase_util.data.RepositoryNormalizer(
                filename=normalizer_filenames
            )

            training_material = db.train(fold=fold)

            feature_data = {}
            target_data = {}
            # Loop through all training items from specific scene class
            for audio_filename in training_material.unique_files:
                # Get feature filename
                filename_dict = {}
                for feature_label in feature_label_list:
                    filename_dict[feature_label] = audio_filename_to_feature_filename(
                        audio_filename=audio_filename,
                        feature_path=param.get_path('path.features'),
                        feature_label=feature_label
                    )
                # Load all features.
                repo = dcase_util.containers.FeatureRepository(filename=filename_dict).load()

                # Normalize features.
                repo = repo_normalizer.normalize(repo)

                # Form feature matrix based on stacking recipe.
                features = dcase_util.data.Stacker(
                    recipe=param.get_path('feature_stacking.recipe')
                ).stack(
                    repository=repo
                )

                # Store feature data
                feature_data[audio_filename] = features

                # Get targets
                targets = dcase_util.data.ManyHotEncoder(
                    label_list=db.tags(),
                    time_resolution=features.time_resolution
                ).encode(
                    label_list=training_material.filter(filename=audio_filename)[0].tags,
                    length_frames=features.frames
                )

                # Store event roll
                target_data[audio_filename] = targets

            # Initialize model container
            model = dcase_util.containers.DictContainer(filename=fold_model_filename)
            for tag_id, tag_label in enumerate(db.tags()):
                log.line('[{tag_label}]'.format(tag_label=tag_label), indent=4)

                data_positive = []
                data_negative = []

                for audio_filename in sorted(list(feature_data.keys())):
                    activity_matrix = target_data[audio_filename].data

                    positive_frames = numpy.where(activity_matrix[tag_id, :] == 1)[0]
                    negative_frames = numpy.where(activity_matrix[tag_id, :] == 0)[0]

                    # Store positive examples
                    if any(positive_frames):
                        data_positive.append(
                            feature_data[audio_filename].get_frames(frame_ids=positive_frames)
                        )

                    # Store negative examples
                    if any(negative_frames):
                        data_negative.append(
                            feature_data[audio_filename].get_frames(frame_ids=negative_frames)
                        )

                model[tag_label] = {
                    'positive' : GaussianMixture(**param['learner']).fit(numpy.hstack(data_positive).T),
                    'negative' : GaussianMixture(**param['learner']).fit(numpy.hstack(data_negative).T),
                }

            # Save model to the disk
            model.save()

    log.foot()

# Testing
if param.get_path('flow.testing'):
    log.section_header('Testing')

    # Loop over all cross-validation folds and test
    for fold in db.folds():
        log.line('Fold {fold:d}'.format(fold=fold), indent=4)

        # Get model filename
        fold_model_filename = os.path.join(param.get_path('path.models'), 'model_fold_{fold:d}.cpickle'.format(fold=fold))

        # Load model
        model = dcase_util.containers.DictContainer(filename=fold_model_filename).load()

        normalizer_filenames = {}
        for feature_label in feature_label_list:
            # Get filename for the normalization factors
            normalizer_filenames[feature_label] = os.path.join(param.get_path('path.normalization'), 'norm_fold_{fold:d}.{feature_label}.cpickle'.format(
                fold=fold, feature_label=feature_label
            ))

        repo_normalizer = dcase_util.data.RepositoryNormalizer(
            filename=normalizer_filenames
        )

        # Get results filename
        fold_results_filename = os.path.join(param.get_path('path.results'), 'res_fold_{fold:d}.txt'.format(fold=fold))
        if not os.path.isfile(fold_results_filename) or overwrite:
            # Initialize results container
            res = dcase_util.containers.MetaDataContainer(filename=fold_results_filename)

            # Loop through all test files from the current cross-validation fold
            for audio_filename in db.test(fold=fold).unique_files:
                # Get feature filenames
                filename_dict = {}
                for feature_label in feature_label_list:
                    filename_dict[feature_label] = audio_filename_to_feature_filename(
                        audio_filename=audio_filename,
                        feature_path=param.get_path('path.features'),
                        feature_label=feature_label
                    )

                # Load all features.
                repo = dcase_util.containers.FeatureRepository(filename=filename_dict).load()

                # Normalize features.
                repo = repo_normalizer.normalize(repo)

                # Form feature matrix based on stacking recipe.
                features = dcase_util.data.Stacker(
                    recipe=param.get_path('feature_stacking.recipe')
                ).stack(
                    repository=repo
                )

                # Initialize likelihood matrices for positive and negative side
                frame_probabilities_positive = numpy.empty((db.tag_count(), features.frames))
                frame_probabilities_negative = numpy.empty((db.tag_count(), features.frames))
                frame_probabilities_positive[:] = numpy.nan
                frame_probabilities_negative[:] = numpy.nan

                # Loop through all event classes and get likelihood for each per frame.
                for tag_id, tag_label in enumerate(db.tags()):
                    if model[tag_label]['positive']:
                        frame_probabilities_positive[tag_id, :] = model[tag_label]['positive'].score_samples(
                            features.data.T
                        )

                    if model[tag_label]['negative']:
                        frame_probabilities_negative[tag_id, :] = model[tag_label]['negative'].score_samples(
                            features.data.T
                        )

                current_results = dcase_util.containers.ProbabilityContainer()

                probabilities = frame_probabilities_positive - frame_probabilities_negative

                # Accumulate probabilities inside sliding window.
                probabilities = dcase_util.data.ProbabilityEncoder().collapse_probabilities(
                    probabilities=probabilities,
                    operator='sum'
                )

                # Loop through all event classes and get likelihood for each per frame.
                for tag_id, tag_label in enumerate(db.tags()):
                    current_results.append(
                        {
                            'filename': db.absolute_to_relative_path(audio_filename),
                            'label': tag_label,
                            'probability': probabilities[tag_id]
                        }
                    )

                # Store current results
                res += current_results

            # Save results container
            res.save()
    log.foot()


# Evaluation
if param.get_path('flow.evaluation'):
    log.section_header('Evaluation')
    class_wise_eer = numpy.zeros((db.fold_count, db.tag_count()))
    for fold in db.folds():
        fold_results_filename = os.path.join(param.get_path('path.results'), 'res_fold_{fold:d}.txt'.format(fold=fold))

        reference = db.eval(fold=fold)
        for item_id, item in enumerate(reference):
            item.filename = db.absolute_to_relative_path(item.filename)

        estimated = dcase_util.containers.ProbabilityContainer(filename=fold_results_filename).load()
        for item_id, item in enumerate(estimated):
            item.filename = db.absolute_to_relative_path(item.filename)

        evaluator = sed_eval.audio_tag.AudioTaggingMetrics(tags=db.tags())
        evaluator.evaluate(
            reference_tag_list=reference,
            estimated_tag_probabilities=estimated
        )

        results = dcase_util.containers.DictContainer(evaluator.results())
        for tag_id, tag_label in enumerate(db.tags()):
            class_wise_eer[fold - 1, tag_id] = results['class_wise'][tag_label]['eer']['eer']

    cell_data = class_wise_eer
    tag_mean_accuracy = numpy.nanmean(cell_data, axis=0).reshape((1, -1))
    cell_data = numpy.vstack((cell_data, tag_mean_accuracy))
    fold_mean_accuracy = numpy.nanmean(cell_data, axis=1).reshape((-1, 1))
    cell_data = numpy.hstack((cell_data, fold_mean_accuracy))

    tag_list = db.tags()
    tag_list.extend(['Average'])
    cell_data = [tag_list] + cell_data.tolist()

    column_headers = ['Tag']
    for fold in db.folds():
        column_headers.append('Fold {fold:d}'.format(fold=fold))

    column_headers.append('AVG')

    log.table(
        cell_data=cell_data,
        column_headers=column_headers,
        column_separators=[0, 5],
        row_separators=[7],
        indent=2
    )

    log.foot()
