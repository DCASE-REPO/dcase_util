#!/usr/bin/env python
# -*- coding: utf-8 -*-
from IPython import embed

# ===================================================================================
# Dataset initialization
# ===================================================================================
import os
import dcase_util

# Setup logging
dcase_util.utils.setup_logging()

log = dcase_util.ui.FancyLogger()
log.title('Acoustic Scene Classification Example / GMM')

# Create dataset object and set dataset to be stored under 'data' directory.
db = dcase_util.datasets.DCASE2013_Scenes_DevelopmentSet(
    data_path='datasets'
)

# Initialize dataset (download, extract and prepare it).
db.initialize()

# Show dataset information
db.show()

# ===================================================================================
# Feature extraction
# ===================================================================================

log.section_header('Feature Extraction')

# Prepare feature extractor
extractor = dcase_util.features.MfccStaticExtractor(
    fs=44100,
    win_length_seconds=0.04,
    hop_length_seconds=0.02,
    n_mfcc=14
)
# Define feature storage path
feature_storage_path = os.path.join('systems', 'ASC_GMM_SIMPLE', 'features')

# Make sure path exists
dcase_util.utils.Path().create(feature_storage_path)

# Loop over all audio files in the dataset and extract features for them.
for audio_filename in db.audio_files:
    # Show some progress
    log.line(os.path.split(audio_filename)[1], indent=2)

    # Get filename for feature data from audio filename
    feature_filename = os.path.join(
        feature_storage_path,
        os.path.split(audio_filename)[1].replace('.wav', '.cpickle')
    )

    # Load audio data
    audio = dcase_util.containers.AudioContainer().load(
        filename=audio_filename,
        mono=True,
        fs=extractor.fs
    )

    # Extract features and store them into FeatureContainer, and save it to the disk
    features = dcase_util.containers.FeatureContainer(
        filename=feature_filename,
        data=extractor.extract(audio.data),
        time_resolution=extractor.hop_length_seconds
    ).save()

log.foot()

# ===================================================================================
# Feature normalization
# ===================================================================================

log.section_header('Feature Normalization')

# Define normalization data storage path
normalization_storage_path = os.path.join('systems', 'ASC_GMM_SIMPLE', 'normalization')

# Make sure path exists
dcase_util.utils.Path().create(normalization_storage_path)

# Loop over all cross-validation folds and calculate mean and std for the training data
for fold in db.folds():
    # Show some progress
    log.line('Fold {fold:d}'.format(fold=fold), indent=2)

    # Get filename for the normalization factors
    fold_stats_filename = os.path.join(
        normalization_storage_path,
        'norm_fold_{fold:d}.cpickle'.format(fold=fold)
    )

    # Normalizer
    normalizer = dcase_util.data.Normalizer(filename=fold_stats_filename)

    # Loop through all training data
    for item in db.train(fold=fold):
        # Get feature filename
        feature_filename = os.path.join(
            feature_storage_path,
            os.path.split(item.filename)[1].replace('.wav', '.cpickle')
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

# ===================================================================================
# Model learning
# ===================================================================================

log.section_header('Learning')

# Imports
from sklearn.mixture import GaussianMixture
import numpy

# Define model data storage path
model_storage_path = os.path.join('system_data', 'model')

# Make sure path exists
dcase_util.utils.Path().create(model_storage_path)

# Loop over all cross-validation folds and learn acoustic models
for fold in db.folds():
    # Show some progress
    log.line('Fold {fold:d}'.format(fold=fold), indent=2)

    # Get model filename
    fold_model_filename = os.path.join(
        model_storage_path,
        'model_fold_{fold:d}.cpickle'.format(fold=fold)
    )

    # Get filename for the normalizer
    fold_stats_filename = os.path.join(
        normalization_storage_path,
        'norm_fold_{fold:d}.cpickle'.format(fold=fold)
    )

    # Normalizer
    normalizer = dcase_util.data.Normalizer().load(filename=fold_stats_filename)

    # Collect class wise training data
    class_wise_data = {}
    for scene_label in db.scene_labels():
        class_wise_data[scene_label] = []

        # Loop through all training items from specific scene class
        for item in db.train(fold=fold).filter(scene_label=scene_label):
            # Get feature filename
            feature_filename = os.path.join(
                feature_storage_path,
                os.path.split(item.filename)[1].replace('.wav', '.cpickle')
            )

            # Load all features.
            features = dcase_util.containers.FeatureContainer().load(
                filename=feature_filename
            )

            # Normalize features.
            normalizer.normalize(features)

            # Store feature data.
            class_wise_data[scene_label].append(features.data)

    # Initialize model container.
    model = dcase_util.containers.DictContainer(filename=fold_model_filename)

    # Loop though all scene classes and train acoustic model for each
    for scene_label in db.scene_labels():
        # Show some progress
        log.line('[{scene_label}]'.format(scene_label=scene_label), indent=4)

        # Train acoustic model
        model[scene_label] = GaussianMixture(
            n_components=8
        ).fit(
            numpy.hstack(class_wise_data[scene_label]).T
        )

    # Save model to the disk
    model.save()

log.foot()

# ===================================================================================
# Testing
# ===================================================================================


log.section_header('Testing')

# Define model data storage path
results_storage_path = os.path.join('systems', 'ASC_GMM_SIMPLE', 'results')

# Make sure path exists
dcase_util.utils.Path().create(results_storage_path)

# Loop over all cross-validation folds and test
for fold in db.folds():
    # Show some progress
    log.line('Fold {fold:d}'.format(fold=fold), indent=2)

    # Get model filename
    fold_model_filename = os.path.join(
        model_storage_path,
        'model_fold_{fold:d}.cpickle'.format(fold=fold)
    )

    # Load model
    model = dcase_util.containers.DictContainer().load(
        filename=fold_model_filename
    )

    # Get filename for the normalizer
    fold_stats_filename = os.path.join(
        normalization_storage_path,
        'norm_fold_{fold:d}.cpickle'.format(fold=fold)
    )

    # Normalizer
    normalizer = dcase_util.data.Normalizer().load(filename=fold_stats_filename)

    # Get results filename
    fold_results_filename = os.path.join(results_storage_path, 'res_fold_{fold:d}.txt'.format(fold=fold))

    # Initialize results container
    res = dcase_util.containers.MetaDataContainer(filename=fold_results_filename)

    # Loop through all test files from the current cross-validation fold
    for item in db.test(fold=fold):
        # Get feature filename
        feature_filename = os.path.join(
            feature_storage_path,
            os.path.split(item.filename)[1].replace('.wav', '.cpickle')
        )

        # Load all features.
        features = dcase_util.containers.FeatureContainer().load(
            filename=feature_filename
        )

        # Normalize features.
        normalizer.normalize(features)

        # Initialize log likelihoods matrix
        logls = numpy.ones((db.scene_label_count(), features.frames)) * -numpy.inf

        # Loop through all scene classes and get likelihood for each per frame
        for scene_label_id, scene_label in enumerate(db.scene_labels()):
            logls[scene_label_id] = model[scene_label].score_samples(features.data.T)

        # Accumulate log likelihoods
        accumulated_logls = dcase_util.data.ProbabilityEncoder().collapse_probabilities(
            probabilities=logls,
            operator='sum'
        )

        # Estimate scene label based on max likelihood.
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

# ===================================================================================
# Evaluation
# ===================================================================================

log.section_header('Evaluation')

# Imports
import sed_eval

all_res = []
overall = []
class_wise_results = numpy.zeros((len(db.folds()), len(db.scene_labels())))
for fold in db.folds():
    # Get results filename
    fold_results_filename = os.path.join(
        results_storage_path,
        'res_fold_{fold:d}.txt'.format(fold=fold)
    )

    # Get reference scenes
    reference_scene_list = db.eval(fold=fold)
    for item_id, item in enumerate(reference_scene_list):
        # Modify data for sed_eval
        reference_scene_list[item_id]['file'] = item.filename

    # Load estimated scenes
    estimated_scene_list = dcase_util.containers.MetaDataContainer().load(
        filename=fold_results_filename
    )

    for item_id, item in enumerate(estimated_scene_list):
        # Modify data for sed_eval
        estimated_scene_list[item_id]['file'] = item.filename

    # Initialize evaluator
    evaluator = sed_eval.scene.SceneClassificationMetrics(scene_labels=db.scene_labels())

    # Evaluate estimated against reference.
    evaluator.evaluate(
        reference_scene_list=reference_scene_list,
        estimated_scene_list=estimated_scene_list
    )

    # Get results
    results = dcase_util.containers.DictContainer(evaluator.results())

    # Store fold-wise results
    all_res.append(results)
    overall.append(results.get_path('overall.accuracy') * 100)

    # Get scene class-wise results
    class_wise_accuracy = []
    for scene_label_id, scene_label in enumerate(db.scene_labels()):
        class_wise_accuracy.append(results.get_path(['class_wise', scene_label, 'accuracy', 'accuracy']))
        class_wise_results[fold - 1, scene_label_id] = results.get_path(
            ['class_wise', scene_label, 'accuracy', 'accuracy'])

# Form results table
cell_data = class_wise_results
scene_mean_accuracy = numpy.mean(cell_data, axis=0).reshape((1, -1))
cell_data = numpy.vstack((cell_data, scene_mean_accuracy))
fold_mean_accuracy = numpy.mean(cell_data, axis=1).reshape((-1, 1))
cell_data = numpy.hstack((cell_data, fold_mean_accuracy))

scene_list = db.scene_labels()
scene_list.extend(['Average'])
cell_data = [scene_list] + (cell_data * 100).tolist()

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
