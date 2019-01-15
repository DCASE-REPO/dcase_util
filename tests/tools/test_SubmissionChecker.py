""" Unit tests for Challenge tools """

import os
import tempfile

import nose.tools

from dcase_util.tools import SubmissionChecker


def test_submissionchecker_parameter_file():
    sc = SubmissionChecker(entry_label='Heittola_TUT_task1_1', class_labels=['label1', 'label2'], file_count=2)
    tmp = tempfile.NamedTemporaryFile('r+', suffix='.yaml',  dir=tempfile.gettempdir(), delete=False)
    try:
        tmp.write('submission:\n')
        tmp.write('  label: Heittola_TUT_task1_1\n')
        tmp.write('  name: DCASE2017 baseline system\n')
        tmp.write('  abbreviation: Baseline\n')
        tmp.write('  authors: \n')
        tmp.write('    - lastname: Heittola\n')
        tmp.write('      firstname: Toni\n')
        tmp.write('      email: toni.heittola@tut.fi\n')
        tmp.write('      corresponding: true\n')
        tmp.write('      affiliation: \n')
        tmp.write('        abbreviation: TUT\n')
        tmp.write('        institute: Tampere University of Technology\n')
        tmp.write('        department: Laboratory of Signal Processing\n')
        tmp.write('        location: Tampere, Finland\n')
        tmp.write('system:\n')
        tmp.write('  description:\n')
        tmp.write('    input_channels: mono\n')
        tmp.write('    input_sampling_rate: 44.1kHz\n')
        tmp.write('    acoustic_features: log-mel energies\n')
        tmp.write('    data_augmentation: null\n')
        tmp.write('    machine_learning_method: MLP\n')
        tmp.write('    decision_making: majority vote \n')
        tmp.write('  source_code: https://github.com/TUT-ARG/DCASE2017-baseline-system\n')
        tmp.write('results:\n')
        tmp.write('  development_dataset:\n')
        tmp.write('    overall:\n')
        tmp.write('      accuracy: 74.8\n')
        tmp.write('    class_wise:\n')
        tmp.write('      label1:\n')
        tmp.write('        accuracy: 74.8\n')
        tmp.write('      label2:\n')
        tmp.write('        accuracy: 74.8\n')
        tmp.close()
        data, error_log = sc._parameter_file(filename=tmp.name)

        nose.tools.assert_dict_equal(
            data.get_path('results.development_dataset.class_wise'),
            {'label1': {'accuracy': 74.8}, 'label2': {'accuracy': 74.8}}
        )

    finally:
        try:
            tmp.close()
            os.unlink(tmp.name)
        except:
            pass

