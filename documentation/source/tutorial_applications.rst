.. _tutorial_applications:

Application examples
--------------------

Acoustic scene classifier
=========================

This tutorial shows how to build simple acoustic scene classifier with utilities
available in `dcase_util`. Acoustic scene classifier application contains usually following stages:

- **Dataset initialization stage**, make use dataset is downloaded and ready to be used.
- **Feature extraction stage**, acoustic features are extracted for all audio files in the development dataset and stores to the disk for easier access later
- **Feature normalization stage**, go though training material per cross-validation fold and calculate mean and standard deviation for acoustic features to normalize feature data later
- **Learning stage**, go through training material per cross-validation fold, and learn acoustic model.
- **Testing stage**, go through testing material per cross-validation fold, and estimate scene class for each sample.
- **Evaluation**, evaluate system output against ground truth.

This examples uses acoustic scene dataset published for DCASE2013 (10 scene classes), static MFCCs as features, and
GMM as classifier. Example is showing only bare minimum code needed, usual development system requires better
parametrization to make system development easier.

Full code example can be found `examples/asc_gmm_simple.py`.

Dataset initialization
::::::::::::::::::::::

This examples uses acoustic scene dataset published for DCASE2013, dataset class to handle this class is delivered
with the dcase_utils: `dcase_util.datasets.DCASE2013_Scenes_DevelopmentSet`.

Dataset needs to be downloaded first, extracted to disk, and prepared for usage::

    import os
    import dcase_util
    # Setup logging
    dcase_util.utils.setup_logging()

    log = dcase_util.ui.FancyLogger()
    log.title('Acoustic Scene Classification Example / GMM')

    # Create dataset object and set dataset to be stored under 'data' directory.
    db = dcase_util.datasets.DCASE2013_Scenes_DevelopmentSet(
        data_path='data'
    )

    # Initialize dataset (download, extract and prepare it).
    db.initialize()

    # Show dataset information
    db.show()
    # DictContainer :: Class
    #   audio_source                      : Field recording
    #   audio_type                        : Natural
    #   authors                           : D. Giannoulis, E. Benetos, D. Stowell, and M. D. Plumbley
    #   microphone_model                  : Soundman OKM II Klassik/studio A3 electret microphone
    #   recording_device_model            : Unknown
    #   title                             : IEEE AASP CASA Challenge - Public Dataset for Scene Classification Task
    #   url                               : https://archive.org/details/dcase2013_scene_classification
    #
    # MetaDataContainer :: Class
    #   Filename                          : data/DCASE2013-acoustic-scenes-development/meta.txt
    #   Items                             : 100
    #   Unique
    #     Files                           : 100
    #     Scene labels                    : 10
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         bus                        10
    #         busystreet                 10
    #         office                     10
    #         openairmarket              10
    #         park                       10
    #         quietstreet                10
    #         restaurant                 10
    #         supermarket                10
    #         tube                       10
    #         tubestation                10

Feature extraction
::::::::::::::::::

Usually it is most efficient to extract features for all audio files and store them on disk, rather than extracting
them each time when acoustic features are needed. Example how to do this::

    log.section_header('Feature Extraction')

    # Prepare feature extractor
    extractor = dcase_util.features.MfccStaticExtractor(
        fs=44100,
        win_length_seconds=0.04,
        hop_length_seconds=0.02,
        n_mfcc=14
    )
    # Define feature storage path
    feature_storage_path = os.path.join('system_data', 'features')

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

Feature normalization
:::::::::::::::::::::

In this stage, training material is gone through per cross-validation fold and mean & standard deviation are calculated
for acoustic features. These normalization factors are used to normalize feature data before using it in
the learning and testing stages.

Code::

    log.section_header('Feature Normalization')

    # Define normalization data storage path
    normalization_storage_path = os.path.join('system_data', 'normalization')

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

Model learning
::::::::::::::

In this stage, training material is gone though per cross-validation fold, and acoustic model is learned and stored.

Code::

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

Testing
:::::::

In this stage, testing material is gone through per cross-validation fold, and scene class is estimated for
each test sample.

Code::

    log.section_header('Testing')

    # Define model data storage path
    results_storage_path = os.path.join('system_data', 'results')

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

Evaluation
::::::::::

In this stage, system output is evaluated against ground truth delivered with the dataset.

Code::

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
        overall.append(results.get_path('overall.accuracy')*100)

        # Get scene class-wise results
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

Results::

       Scene                | Fold 1   Fold 2   Fold 3   Fold 4   Fold 5 | Average
       -------------------- | ------   ------   ------   ------   ------ | -------
       bus                  | 100.00   100.00   100.00   100.00   100.00 |  100.00
       busystreet           | 100.00    33.33    33.33   100.00    66.67 |   66.67
       office               |  66.67   100.00   100.00    66.67   100.00 |   86.67
       openairmarket        |  66.67   100.00     0.00    66.67   100.00 |   66.67
       park                 |  33.33    33.33     0.00    33.33    33.33 |   26.67
       quietstreet          |  66.67   100.00    33.33    66.67    66.67 |   66.67
       restaurant           |  66.67     0.00    66.67     0.00    33.33 |   33.33
       supermarket          |  33.33     0.00    33.33     0.00    33.33 |   20.00
       tube                 | 100.00    33.33    33.33    66.67    66.67 |   60.00
       tubestation          |   0.00    66.67    66.67     0.00     0.00 |   26.67
       -------------------- | ------   ------   ------   ------   ------ | -------
       Average              |  63.33    56.67    46.67    50.00    60.00 |   55.33