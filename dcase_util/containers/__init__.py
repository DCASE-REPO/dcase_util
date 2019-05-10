# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Containers
==========
Classes for data containers. The aim of these data containers it to wrap the data with useful
set of method to access and to manipulate the data, as well as load and store it.

These containers are inherited from standard Python containers (e.g. object, list, and
dictionary) to allow them to be used together with other tools and libraries.

Basic containers
::::::::::::::::


ObjectContainer
---------------

*dcase_util.containers.ObjectContainer*

Container class for object inherited from standard object class.

Examples how to inherit class from ObjectContainer:

.. code-block:: python
    :linenos:

    class Multiplier(dcase_util.containers.ObjectContainer):
        def __init__(self, multiplier=None, **kwargs):
            super(Multiplier, self).__init__(**kwargs)
            self.multiplier = multiplier

        def __str__(self):
            ui = dcase_util.ui.FancyStringifier()
            output = super(Multiplier, self).__str__()
            output+= ui.data(field='multiplier', value=self.multiplier)
            return output

        def multiply(self, data):
            return self.multiplier * data

    m = Multiplier(10)
    m.show()
    # Multiplier :: Class
    #   multiplier                        : 10

    print(m.multiply(5))
    # 50

    # Save object
    m.save('test.cpickle')

    # Load object
    m2 = Multiplier().load('test.cpickle')

    print(m2.multiply(5))
    # 50

    m2.show()
    # Multiplier :: Class
    #   filename                          : test.cpickle
    #   multiplier                        : 10

.. autosummary::
    :toctree: generated/

    ObjectContainer
    ObjectContainer.load
    ObjectContainer.save
    ObjectContainer.show
    ObjectContainer.log

DictContainer
-------------

*dcase_util.containers.DictContainer*

Dictionary container class inherited from standard dict class.

Usage examples:

.. code-block:: python
    :linenos:

    import dcase_util

    d = dcase_util.containers.DictContainer(
        {
            'test': {
                'field1': 1,
                'field2': 2,
            },
            'test2': 100
        }
    )
    d.show()
    # DictContainer
    #   test
    #     field1                          : 1
    #     field2                          : 2
    #   test2                             : 100

    print(d.get_path('test.field1'))
    # 1

    print(d.get_path(['test', 'field1']))
    # 1

    print(d.get_path('test2'))
    # 100

    d.set_path('test.field2', 200)
    print(d.get_path('test.field2'))
    # 200

    print(d.get_leaf_path_list())
    # ['test.field1', 'test.field2', 'test2']

    print(d.get_leaf_path_list(target_field_startswith='field'))
    # ['test.field1', 'test.field2']

    d.show()
    # DictContainer
    #   test
    #     field1                          : 1
    #     field2                          : 200
    #   test2                             : 100

.. autosummary::
    :toctree: generated/

    DictContainer
    DictContainer.load
    DictContainer.save
    DictContainer.show
    DictContainer.log
    DictContainer.get_path
    DictContainer.set_path
    DictContainer.get_leaf_path_list
    DictContainer.merge
    DictContainer.get_hash_for_path
    DictContainer.get_hash

ListContainer
-------------

*dcase_util.containers.ListContainer*

List container class inherited from standard list class.

.. autosummary::
    :toctree: generated/

    ListContainer
    ListContainer.load
    ListContainer.save
    ListContainer.show
    ListContainer.log
    ListContainer.update

ListDictContainer
-----------------

*dcase_util.containers.ListDictContainer*

List of dictionaries container class inherited from standard list class.

Usage examples:

.. code-block:: python
    :linenos:

    import dcase_util
    ld = dcase_util.containers.ListDictContainer(
        [
            {
                'field1': 1,
                'field2': 2,
            },
            {
                'field1': 3,
                'field2': 4,
            },
        ]
    )
    ld.show()
    # ListDictContainer
    # [0] =======================================
    #    DictContainer
    #      field1                            : 1
    #      field2                            : 2
    #
    # [1] =======================================
    #    DictContainer
    #      field1                            : 3
    #      field2                            : 4

    print(ld.search(key='field1', value=3))
    # DictContainer
    #   field1                            : 3
    #   field2                            : 4

    print(ld.get_field(field_name='field2'))
    # [2, 4]

.. autosummary::
    :toctree: generated/

    ListDictContainer
    ListDictContainer.load
    ListDictContainer.save
    ListDictContainer.show
    ListDictContainer.log
    ListDictContainer.search
    ListDictContainer.get_field

RepositoryContainer
-------------------

*dcase_util.containers.RepositoryContainer*

Container class for repository, inherited from `dcase_util.containers.DictContainer`.

.. autosummary::
    :toctree: generated/

    RepositoryContainer
    RepositoryContainer.load
    RepositoryContainer.save
    RepositoryContainer.show
    RepositoryContainer.log

TextContainer
-------------

*dcase_util.containers.TextContainer*

Container class for text, inherited from `dcase_util.containers.ListContainer`.

.. autosummary::
    :toctree: generated/

    TextContainer
    TextContainer.load
    TextContainer.save
    TextContainer.show
    TextContainer.log

Data containers
:::::::::::::::

DataContainer
-------------

*dcase_util.containers.DataContainer*

Container class for data, inherited from `dcase_util.containers.ObjectContainer`.

.. autosummary::
    :toctree: generated/

    DataContainer
    DataContainer.load
    DataContainer.save
    DataContainer.show
    DataContainer.log
    DataContainer.data
    DataContainer.shape
    DataContainer.length
    DataContainer.frames
    DataContainer.push_processing_chain_item
    DataContainer.focus_start
    DataContainer.focus_stop
    DataContainer.stats
    DataContainer.reset_focus
    DataContainer.get_focused
    DataContainer.freeze
    DataContainer.get_frames
    DataContainer.plot

DataArrayContainer
------------------

*dcase_util.containers.DataArrayContainer*

Container class for data, inherited from `dcase_util.containers.DataContainer`.

.. autosummary::
    :toctree: generated/

    DataArrayContainer
    DataArrayContainer.load
    DataArrayContainer.save
    DataArrayContainer.show
    DataArrayContainer.log
    DataArrayContainer.data
    DataArrayContainer.shape
    DataArrayContainer.length
    DataArrayContainer.frames
    DataArrayContainer.push_processing_chain_item
    DataArrayContainer.focus_start
    DataArrayContainer.focus_stop
    DataArrayContainer.stats
    DataArrayContainer.reset_focus
    DataArrayContainer.get_focused
    DataArrayContainer.freeze
    DataArrayContainer.get_frames
    DataArrayContainer.plot

DataMatrix2DContainer
---------------------

*dcase_util.containers.DataMatrix2DContainer*

DataMatrix2DContainer is data container for two-dimensional data matrix (numpy.ndarray).

Basic usage examples:

.. code-block:: python
    :linenos:

    # Initialize container with random matrix 10x100, and set time resolution to 20ms
    data_container = dcase_util.containers.DataMatrix2DContainer(
      data=numpy.random.rand(10,100),
      time_resolution=0.02
    )

    # When storing, e.g., acoustic features, time resolution corresponds to feature extraction frame hop length.

    # Access data matrix directly
    print(data_container.data.shape)
    # (10, 100)

    # Show container information
    data_container.show()
    # DataMatrix2DContainer :: Class
    #   Data
    #     data                            : matrix (10,100)
    #     Dimensions
    #       time_axis                     : 1
    #       data_axis                     : 0
    #     Timing information
    #       time_resolution               : 0.02 sec
    #   Meta
    #     stats                           : Calculated
    #     metadata                        : -
    #     processing_chain                : -
    #   Duration
    #       Frames                        : 100
    #       Seconds                       : 2.00 sec

The container has focus mechanism to flexibly capture only part of the
data matrix. Focusing can be done based on time (in seconds, if time
resolution is defined), or based on frame ids.

Examples using focus mechanism, accessing data and visualizing data:

.. code-block:: python
    :linenos:

    # Using focus to get part data between 0.5 sec and 1.0 sec
    print(data_container.set_focus(start_seconds=0.5, stop_seconds=1.0).get_focused().shape)
    # (10, 25)

    # Using focus to get part data between frame 10 and 50
    print(data_container.set_focus(start=10, stop=50).get_focused().shape)
    # (10, 40)

    # Resetting focus and accessing full data matrix
    data_container.reset_focus()
    print(data_container.get_focused().shape)
    # (10, 100)

    # Access frames 1, 2, 10, and 30
    data_container.get_frames(frame_ids=[1,2,10,30])

    # Access frames 1-5, and only first value per column
    data_container.get_frames(frame_ids=[1,2,3,4,5], vector_ids=[0])

    # Transpose matrix
    transposed_data = data_container.T
    print(transposed_data.shape)
    # (100, 10)

    # Plot data
    data_container.plot()

.. autosummary::
    :toctree: generated/

    DataMatrix2DContainer
    DataMatrix2DContainer.load
    DataMatrix2DContainer.save
    DataMatrix2DContainer.show
    DataMatrix2DContainer.log
    DataMatrix2DContainer.data
    DataMatrix2DContainer.shape
    DataMatrix2DContainer.length
    DataMatrix2DContainer.frames
    DataMatrix2DContainer.vector_length
    DataMatrix2DContainer.push_processing_chain_item
    DataMatrix2DContainer.focus_start
    DataMatrix2DContainer.focus_stop
    DataMatrix2DContainer.T
    DataMatrix2DContainer.stats
    DataMatrix2DContainer.reset_focus
    DataMatrix2DContainer.get_focused
    DataMatrix2DContainer.freeze
    DataMatrix2DContainer.get_frames
    DataMatrix2DContainer.plot

DataMatrix3DContainer
---------------------

*dcase_util.containers.DataMatrix3DContainer*

.. autosummary::
    :toctree: generated/

    DataMatrix3DContainer
    DataMatrix3DContainer.load
    DataMatrix3DContainer.save
    DataMatrix3DContainer.show
    DataMatrix3DContainer.log
    DataMatrix3DContainer.data
    DataMatrix3DContainer.length
    DataMatrix3DContainer.frames

BinaryMatrix2DContainer
-----------------------

*dcase_util.containers.BinaryMatrix2DContainer*

.. autosummary::
    :toctree: generated/

    BinaryMatrix2DContainer
    BinaryMatrix2DContainer.load
    BinaryMatrix2DContainer.save
    BinaryMatrix2DContainer.show
    BinaryMatrix2DContainer.log
    BinaryMatrix2DContainer.data
    BinaryMatrix2DContainer.length
    BinaryMatrix2DContainer.frames
    BinaryMatrix2DContainer.pad
    BinaryMatrix2DContainer.plot

DataRepository
--------------

*dcase_util.containers.DataRepository*

DataRepository is container which can be used to store multiple other data containers.
Repository stores data with two level information: label and stream. The label is higher level key and stream is
second level one. Repositories can be used, for example, to store multiple different acoustic features all related
to same audio signal. Stream id can be used to store features extracted from different audio channels.
Later features can be access using extractor label and stream id.

Usage examples:

.. code-block:: python
    :linenos:

    # Initialize container with data
    data_repository = dcase_util.containers.DataRepository(
        data={
            'label1': {
                'stream0': {
                    'data': 100
                },
                'stream1': {
                    'data': 200
                }
            },
            'label2': {
                'stream0': {
                    'data': 300
                },
                'stream1': {
                    'data': 400
                }
            }
        }
    )
    # Show container information::
    data_repository. show()
    # DataRepository :: Class
    #     Repository info
    #       Item class                    : DataMatrix2DContainer
    #       Item count                    : 2
    #       Labels                        : ['label1', 'label2']
    #     Content
    #       [label1][stream1]             : {'data': 200}
    #       [label1][stream0]             : {'data': 100}
    #       [label2][stream1]             : {'data': 400}
    #       [label2][stream0]             : {'data': 300}

    # Accessing data inside repository
    data_repository.get_container(label='label1',stream_id='stream1')
    # {'data': 200}

    # Setting data
    data_repository.set_container(label='label3',stream_id='stream0', container={'data':500})
    data_repository. show()
    # DataRepository :: Class
    #     Repository info
    #       Item class                    : DataMatrix2DContainer
    #       Item count                    : 3
    #       Labels                        : ['label1', 'label2', 'label3']
    #     Content
    #       [label1][stream1]             : {'data': 200}
    #       [label1][stream0]             : {'data': 100}
    #       [label2][stream1]             : {'data': 400}
    #       [label2][stream0]             : {'data': 300}
    #       [label3][stream0]             : {'data': 500}


.. autosummary::
    :toctree: generated/

    DataRepository
    DataRepository.load
    DataRepository.get_container
    DataRepository.set_container
    DataRepository.push_processing_chain_item
    DataRepository.plot

Audio containers
::::::::::::::::

AudioContainer
--------------

*dcase_util.containers.AudioContainer*

AudioContainer is data container for multi-channel audio. It reads many
formats (WAV, FLAC, M4A, WEBM) and writes WAV and FLAC files. Downloading
audio content directly from Youtube is also supported.

Basic usage examples:

.. code-block:: python
    :linenos:

    # Generating two-channel audio
    audio_container = dcase_util.containers.AudioContainer(fs=44100)
    t = numpy.linspace(0, 2, 2 * audio_container.fs, endpoint=False)
    x1 = numpy.sin(220 * 2 * numpy.pi * t)
    x2 = numpy.sin(440 * 2 * numpy.pi * t)
    audio_container.data = numpy.vstack([x1, x2])

    audio_container.show()
    # AudioContainer :: Class
    #  Sampling rate                     : 44100
    #     Channels                        : 2
    #   Duration
    #     Seconds                         : 2.00 sec
    #     Milliseconds                    : 2000.00 ms
    #     Samples                         : 88200 samples

    # Loading audio file
    audio_container = dcase_util.containers.AudioContainer().load(
      filename=dcase_util.utils.Example.audio_filename()
    )

    # Loading audio content from Youtube
    audio_container = dcase_util.containers.AudioContainer().load_from_youtube(
      query_id='2ceUOv8A3FE',
      start=1,
      stop=5
    )

The container has focus mechanism to flexibly capture only part of the audio
data while keeping full audio signal intact. Focusing can be done based on time
(in seconds, if time resolution is defined), or based on sample ids. Focusing
can be done to single channel or mixdown (mono) channels. Audio containers
content can be replaced with focus segment by freezing it.

Examples using focus segment mechanism:

.. code-block:: python
    :linenos:

    # Using focus to get part data between 0.5 sec and 1.0 sec
    print(audio_container.set_focus(start_seconds=0.5, stop_seconds=1.0).get_focused().shape)
    # (2, 22050)

    # Using focus to get part data starting 5 sec with 2 sec duration
    print(audio_container.set_focus(start_seconds=5, duration_seconds=2.0).get_focused().shape)
    # (2, 88200)

    # Using focus to get part data starting 5 sec with 2 sec duration, mixdown of two stereo channels
    print(audio_container.set_focus(start_seconds=5, duration_seconds=2.0, channel='mixdown').get_focused().shape)
    # (88200,)

    # Using focus to get part data starting 5 sec with 2 sec duration, left of two stereo channels
    print(audio_container.set_focus(start_seconds=5, duration_seconds=2.0, channel='left').get_focused().shape)
    # (88200,)

    # Using focus to get part data starting 5 sec with 2 sec duration, seconds audio channel (indexing starts from 0)
    print(audio_container.set_focus(start_seconds=5, duration_seconds=2.0, channel=1).get_focused().shape)
    # (88200,)

    # Using focus to get part data between samples 44100 and 88200
    print(audio_container.set_focus(start=44100, stop=88200).get_focused().shape)
    # (2, 44100)

    # Resetting focus and accessing full data matrix::
    audio_container.reset_focus()
    print(audio_container.get_focused().shape)
    # (2, 441001)

    # Using focus to get part data starting 5 sec with 2 sec duration, and freeze this segment ::
    audio_container.set_focus(start_seconds=5, duration_seconds=2.0).freeze()
    print(audio_container.shape)
    # (2, 88200)

Processing examples:

.. code-block:: python
    :linenos:

    # Normalizing audio
    audio_container.normalize()

    # Resampling audio to target sampling rate
    audio_container.resample(target_fs=16000)

Visualizations examples:

.. code-block:: python
    :linenos:

    # Plotting waveform
    audio_container.plot_wave()

    # Plotting spectrogram
    audio_container.plot_spec()

.. plot::

    import dcase_util
    audio_container = dcase_util.containers.AudioContainer().load(
      filename=dcase_util.utils.Example.audio_filename()
    )
    audio_container.filename = None
    audio_container.plot_wave()

.. plot::

    import dcase_util
    audio_container = dcase_util.containers.AudioContainer().load(
      filename=dcase_util.utils.Example.audio_filename()
    )
    audio_container.filename = None
    audio_container.plot_spec()

.. autosummary::
    :toctree: generated/

    AudioContainer
    AudioContainer.load
    AudioContainer.load_from_youtube
    AudioContainer.save
    AudioContainer.show
    AudioContainer.log
    AudioContainer.data
    AudioContainer.focus_start_samples
    AudioContainer.focus_start_seconds
    AudioContainer.focus_stop_samples
    AudioContainer.focus_stop_seconds
    AudioContainer.focus_channel
    AudioContainer.loaded
    AudioContainer.shape
    AudioContainer.length
    AudioContainer.duration_samples
    AudioContainer.duration_ms
    AudioContainer.duration_sec
    AudioContainer.streams
    AudioContainer.empty
    AudioContainer.reset_focus
    AudioContainer.set_focus
    AudioContainer.get_focused
    AudioContainer.freeze
    AudioContainer.frames
    AudioContainer.normalize
    AudioContainer.resample
    AudioContainer.mixdown
    AudioContainer.plot
    AudioContainer.plot_wave
    AudioContainer.plot_spec


Feature containers
::::::::::::::::::

FeatureContainer
----------------

*dcase_util.containers.FeatureContainer*

.. autosummary::
    :toctree: generated/

    FeatureContainer

FeatureRepository
-----------------

*dcase_util.containers.FeatureRepository*

.. autosummary::
    :toctree: generated/

    FeatureRepository

Mapping containers
::::::::::::::::::

OneToOneMappingContainer
------------------------

*dcase_util.containers.OneToOneMappingContainer*

.. autosummary::
    :toctree: generated/

    OneToOneMappingContainer
    OneToOneMappingContainer.load
    OneToOneMappingContainer.save
    OneToOneMappingContainer.show
    OneToOneMappingContainer.log
    OneToOneMappingContainer.map
    OneToOneMappingContainer.flipped

Metadata containers
:::::::::::::::::::

MetaDataItem
------------

*dcase_util.containers.MetaDataItem*

.. autosummary::
    :toctree: generated/

    MetaDataItem
    MetaDataItem.show
    MetaDataItem.log
    MetaDataItem.id
    MetaDataItem.get_list
    MetaDataItem.filename
    MetaDataItem.filename_original
    MetaDataItem.scene_label
    MetaDataItem.event_label
    MetaDataItem.onset
    MetaDataItem.offset
    MetaDataItem.identifier
    MetaDataItem.source_label
    MetaDataItem.set_label
    MetaDataItem.tags
    MetaDataItem.active_within_segment

MetaDataContainer
-----------------

*dcase_util.containers.MetaDataContainer*

.. autosummary::
    :toctree: generated/

    MetaDataContainer
    MetaDataContainer.log
    MetaDataContainer.log_all
    MetaDataContainer.show
    MetaDataContainer.show_all
    MetaDataContainer.load
    MetaDataContainer.save
    MetaDataContainer.append
    MetaDataContainer.file_count
    MetaDataContainer.event_count
    MetaDataContainer.scene_label_count
    MetaDataContainer.event_label_count
    MetaDataContainer.identifier_count
    MetaDataContainer.tag_count
    MetaDataContainer.unique_files
    MetaDataContainer.unique_event_labels
    MetaDataContainer.unique_scene_labels
    MetaDataContainer.unique_tags
    MetaDataContainer.unique_identifiers
    MetaDataContainer.unique_source_labels
    MetaDataContainer.max_offset
    MetaDataContainer.to_string
    MetaDataContainer.filter
    MetaDataContainer.filter_time_segment
    MetaDataContainer.process_events
    MetaDataContainer.map_events
    MetaDataContainer.event_inactivity
    MetaDataContainer.add_time
    MetaDataContainer.stats
    MetaDataContainer.scene_stat_counts
    MetaDataContainer.event_stat_counts
    MetaDataContainer.tag_stat_counts
    MetaDataContainer.to_event_roll
    MetaDataContainer.intersection
    MetaDataContainer.intersection_report
    MetaDataContainer.difference

Parameter containers
::::::::::::::::::::

ParameterContainer
------------------

*dcase_util.containers.ParameterContainer*

.. autosummary::
    :toctree: generated/

    ParameterContainer

AppParameterContainer
---------------------

*dcase_util.containers.AppParameterContainer*

.. autosummary::
    :toctree: generated/

    AppParameterContainer
    AppParameterContainer.reset
    AppParameterContainer.process
    AppParameterContainer.process_set
    AppParameterContainer.override
    AppParameterContainer.get_path_translated
    AppParameterContainer.set_path_translated
    AppParameterContainer.update_parameter_set
    AppParameterContainer.set_ids
    AppParameterContainer.set_id_exists
    AppParameterContainer.active_set
    AppParameterContainer.get_set


DCASEAppParameterContainer
--------------------------

*dcase_util.containers.DCASEAppParameterContainer*

.. autosummary::
    :toctree: generated/

    DCASEAppParameterContainer

ParameterListContainer
----------------------

*dcase_util.containers.ParameterListContainer*

.. autosummary::
    :toctree: generated/

    ParameterListContainer

Probability containers
::::::::::::::::::::::

ProbabilityItem
---------------

*dcase_util.containers.ProbabilityItem*

.. autosummary::
    :toctree: generated/

    ProbabilityItem
    ProbabilityItem.show
    ProbabilityItem.log
    ProbabilityItem.filename
    ProbabilityItem.label
    ProbabilityItem.probability
    ProbabilityItem.id
    ProbabilityItem.get_list

ProbabilityContainer
--------------------

*dcase_util.containers.ProbabilityContainer*

.. autosummary::
    :toctree: generated/

    ProbabilityContainer
    ProbabilityContainer.show
    ProbabilityContainer.log
    ProbabilityContainer.load
    ProbabilityContainer.save
    ProbabilityContainer.append
    ProbabilityContainer.unique_files
    ProbabilityContainer.unique_labels
    ProbabilityContainer.unique_indices
    ProbabilityContainer.filter
    ProbabilityContainer.as_matrix

Mixins
::::::

ContainerMixin
--------------

*dcase_util.containers.ContainerMixin*

.. autosummary::
    :toctree: generated/

    ContainerMixin
    ContainerMixin.show
    ContainerMixin.log

FileMixin
---------

*dcase_util.containers.FileMixin*

.. autosummary::
    :toctree: generated/

    FileMixin
    FileMixin.get_file_information
    FileMixin.detect_file_format
    FileMixin.validate_format
    FileMixin.exists
    FileMixin.empty
    FileMixin.delimiter
    FileMixin.is_package


PackageMixin
------------

*dcase_util.containers.PackageMixin*

.. autosummary::
    :toctree: generated/

    PackageMixin
    PackageMixin.package_password
    PackageMixin.extract

"""

from .mixins import *
from .containers import *
from .audio import *
from .mapping import *
from .metadata import *
from .probability import *
from .parameters import *
from .data import *
from .features import *


__all__ = [_ for _ in dir() if not _.startswith('_')]
