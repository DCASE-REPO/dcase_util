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
log.title('Acoustic Scene Classification Example / GMM')

# Get dataset class and initialize it
db = dcase_util.datasets.DCASE2013_Scenes_DevelopmentSet(
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
        'features': os.path.join('systems', 'ASC_GMM', 'features'),
        'normalization': os.path.join('systems', 'ASC_GMM', 'normalization'),
        'models': os.path.join('systems', 'ASC_GMM', 'models'),
        'results': os.path.join('systems', 'ASC_GMM', 'results'),
    },
    'feature_extraction': {
        'fs': 44100,
        'win_length_seconds': 0.04,
        'hop_length_seconds': 0.02,
        'spectrogram_type': 'magnitude',
        'window_type': 'hann_symmetric',
        'n_mels': 40,                       # Number of MEL bands used
        'n_mfcc': 20,
        'n_fft': 2048,                      # FFT length
        'fmin': 0,                          # Minimum frequency when constructing MEL bands
        'fmax': 22050,                      # Maximum frequency when constructing MEL band
        'htk': True,                        # Switch for HTK-styled MEL-frequency equation
        'width': 9,
    },
    'feature_stacking': {
        'recipe': 'mfcc; mfcc_delta; mfcc_acceleration',
    },
    'learner': {
        'covariance_type': 'diag',
        'init_params': 'kmeans',
        'max_iter': 40,
        'n_components': 16,
        'n_init': 1,
        'random_state': 0,
        'reg_covar': 0,
        'tol': 0.001
    }
})

# Make sure all paths exists
dcase_util.utils.Path().create(param['path'].values())

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
        'mfcc': dcase_util.features.MfccStaticExtractor(**param['feature_extraction']),
        'mfcc_delta': dcase_util.features.MfccDeltaExtractor(**param['feature_extraction']),
        'mfcc_acceleration': dcase_util.features.MfccAccelerationExtractor(**param['feature_extraction'])
    }

    # Loop over all audio files in the dataset and extract features for them.
    for audio_filename in db.audio_files:
        log.line(os.path.split(audio_filename)[1], indent=2)
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
        log.line('Fold {fold:d}'.format(fold=fold), indent=2)

        for feature_label in feature_label_list:
            # Get filename for the normalization factors
            fold_stats_filename = os.path.join(param.get_path('path.normalization'), 'norm_fold_{fold:d}.{feature_label}.cpickle'.format(
                fold=fold, feature_label=feature_label))

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
        log.line('Fold {fold:d}'.format(fold=fold), indent=2)

        # Get model filename
        fold_model_filename = os.path.join(param['path']['models'], 'model_fold_{fold:d}.cpickle'.format(fold=fold))

        if not os.path.isfile(fold_model_filename) or overwrite:
            normalizer_filenames = {}
            for feature_label in feature_label_list:
                # Get filename for the normalization factors
                normalizer_filenames[feature_label] = os.path.join(param.get_path('path.normalization'),'norm_fold_{fold:d}.{feature_label}.cpickle'.format(
                    fold=fold, feature_label=feature_label
                ))

            repo_normalizer = dcase_util.data.RepositoryNormalizer(
                filename_dict=normalizer_filenames
            )

            # Collect class wise training data
            class_wise_data = {}
            for scene_label in db.scene_labels():
                class_wise_data[scene_label] = []

                # Loop through all training items from specific scene class
                for item in db.train(fold=fold).filter(scene_label=scene_label):
                    # Get feature filename
                    filename_dict = {}
                    for feature_label in feature_label_list:
                        filename_dict[feature_label] = audio_filename_to_feature_filename(
                            audio_filename=item.filename,
                            feature_path=param.get_path('path.features'),
                            feature_label=feature_label
                        )

                    # Load all features.
                    repo = dcase_util.containers.FeatureRepository().load(
                        filename_dict=filename_dict
                    )

                    # Normalize features.
                    repo = repo_normalizer.normalize(repo)

                    # Form feature matrix based on stacking recipe.
                    features = dcase_util.data.Stacker(
                        recipe=param.get_path('feature_stacking.recipe')
                    ).stack(
                        repository=repo
                    )

                    # Store feature data.
                    class_wise_data[scene_label].append(features.data)

            # Initialize model container.
            model = dcase_util.containers.DictContainer(filename=fold_model_filename)

            # Loop though all scene classes and train acoustic model for each
            for scene_label in db.scene_labels():
                log.line('[{scene_label}]'.format(scene_label=scene_label), indent=4)
                # Train acoustic model
                model[scene_label] = GaussianMixture(**param['learner']).fit(numpy.hstack(class_wise_data[scene_label]).T)

            # Save model to the disk
            model.save()

    log.foot()

# Testing
if param.get_path('flow.testing'):
    log.section_header('Testing')

    # Loop over all cross-validation folds and test
    for fold in db.folds():
        log.line('Fold {fold:d}'.format(fold=fold), indent=2)

        # Get model filename
        fold_model_filename = os.path.join(param.get_path('path.models'), 'model_fold_{fold:d}.cpickle'.format(fold=fold))

        # Load model
        model = dcase_util.containers.DictContainer(filename=fold_model_filename).load()

        # Get normalization factor filename
        fold_stats_filename = os.path.join(param.get_path('path.normalization'), 'norm_fold_{fold:d}.cpickle'.format(fold=fold))

        normalizer_filenames = {}
        for feature_label in feature_label_list:
            # Get filename for the normalization factors
            normalizer_filenames[feature_label] = os.path.join(param.get_path('path.normalization'), 'norm_fold_{fold:d}.{feature_label}.cpickle'.format(
                                                   fold=fold, feature_label=feature_label
            ))

        repo_normalizer = dcase_util.data.RepositoryNormalizer(
            filename_dict=normalizer_filenames
        )

        # Get results filename
        fold_results_filename = os.path.join(param.get_path('path.results'), 'res_fold_{fold:d}.txt'.format(fold=fold))
        if not os.path.isfile(fold_results_filename) or overwrite:
            # Initialize results container
            res = dcase_util.containers.MetaDataContainer(filename=fold_results_filename)

            # Loop through all test files from the current cross-validation fold
            for item in db.test(fold=fold):
                # Get feature filenames
                filename_dict = {}
                for feature_label in feature_label_list:
                    filename_dict[feature_label] = audio_filename_to_feature_filename(
                        audio_filename=item.filename,
                        feature_path=param.get_path('path.features'),
                        feature_label=feature_label
                    )

                # Load all features.
                repo = dcase_util.containers.FeatureRepository().load(
                    filename_dict=filename_dict
                )

                # Normalize features.
                repo = repo_normalizer.normalize(repo)

                # Form feature matrix based on stacking recipe.
                features = dcase_util.data.Stacker(recipe=param.get_path('feature_stacking.recipe')).stack(
                    repository=repo)

                # Initialize log likelihoods matrix
                logls = numpy.ones((db.scene_label_count(), features.data.shape[1])) * -numpy.inf

                # Loop through all scene classes and get likelihood for each per frame
                for scene_label_id, scene_label in enumerate(db.scene_labels()):
                    logls[scene_label_id] = model[scene_label].score_samples(features.data.T)

                accumulated_logls = dcase_util.data.ProbabilityEncoder().collapse_probabilities(
                    probabilities=logls,
                    operator='sum'
                )

                estimated_scene_label = dcase_util.data.ProbabilityEncoder(
                    label_list=db.scene_labels()
                ).max_selection(
                    probabilities=accumulated_logls
                )

                # Store result into results container
                res.append(
                    {
                        'filename': item.filename,
                        'scene_label': estimated_scene_label
                    }
                )

            # Save results container
            res.save()
    log.foot()

# Evaluation
if param.get_path('flow.evaluation'):
    log.section_header('Evaluation')
    all_res = []
    overall = []
    class_wise_results = numpy.zeros((len(db.folds()), len(db.scene_labels())))
    for fold in db.folds():
        fold_results_filename = os.path.join(param.get_path('path.results'), 'res_fold_{fold:d}.txt'.format(fold=fold))
        reference_scene_list = db.eval(fold=fold)
        for item_id, item in enumerate(reference_scene_list):
            reference_scene_list[item_id]['file'] = item.filename

        estimated_scene_list = dcase_util.containers.MetaDataContainer(filename=fold_results_filename).load()
        for item_id, item in enumerate(estimated_scene_list):
            estimated_scene_list[item_id]['file'] = item.filename

        evaluator = sed_eval.scene.SceneClassificationMetrics(scene_labels=db.scene_labels())
        evaluator.evaluate(
            reference_scene_list=reference_scene_list,
            estimated_scene_list=estimated_scene_list
        )

        results = dcase_util.containers.DictContainer(evaluator.results())
        all_res.append(results)
        overall.append(results.get_path('overall.accuracy')*100)
        class_wise_accuracy = []

        for scene_label_id, scene_label in enumerate(db.scene_labels()):
            class_wise_accuracy.append(results.get_path(['class_wise', scene_label, 'accuracy', 'accuracy']))
            class_wise_results[fold-1, scene_label_id] = results.get_path(['class_wise', scene_label, 'accuracy', 'accuracy'])

    # Form results table
    cell_data = class_wise_results
    scene_mean_accuracy = numpy.mean(cell_data, axis=0).reshape((1, -1))
    cell_data = numpy.vstack((cell_data, scene_mean_accuracy))
    fold_mean_accuracy = numpy.mean(cell_data, axis=1).reshape((-1, 1))
    cell_data = numpy.hstack((cell_data, fold_mean_accuracy))

    scene_list = db.scene_labels()
    scene_list.extend(['Average'])
    cell_data = [scene_list] + (cell_data*100).tolist()

    column_headers = ['Scene']
    for fold in db.folds():
        column_headers.append('Fold {fold:d}'.format(fold=fold))

    column_headers.append('Average')

    log.table(
        cell_data=cell_data,
        column_headers=column_headers,
        column_separators=[0, 5],
        row_separators=[10],
        indent=2
    )
    log.foot()
