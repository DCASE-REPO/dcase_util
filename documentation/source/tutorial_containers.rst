.. _tutorial_containers:

Containers
----------

The library provides data containers to ease the workflow. These containers are inherited from standard Python
containers (e.g. object, list, and dictionary) to allow them to be used together with other tools and libraries.
The aim of these data containers it to wrap the data with useful set of method to access and to manipulate
the data, as well as load and store it.

Basic usage
:::::::::::

Initialize container, and load content from the file (four ways shown)::

    # 1
    dict_container = dcase_util.containers.DictContainer(filename='test.yaml')
    dict_container.load()

    # 2
    dict_container = dcase_util.containers.DictContainer()
    dict_container.load(filename='test.yaml')

    # 3
    dict_container = dcase_util.containers.DictContainer(filename='test.yaml').load()

    # 4
    dict_container = dcase_util.containers.DictContainer().load(filename='test.yaml')


To save content to file::

    dict_container.save(filename='test.yaml')

To check content of the container and print it to the console use::

    dict_container.show()

To check content of the container and print it to the standard logging system use::

    dict_container.log()

If logging system is not initialized prior to the call, `dcase_util.utils.setup_logging`
with default parameters will used to initialize it.

Dictionaries
::::::::::::

`dcase_util.containers.DictContainer` is designed to be used with nested dictionaries a bit easier
than standard dict data container. It allows accessing fields in the nested
dictionaries through so called dotted path or through list of path parts.

Initialize container with dictionary::

    dict_container = dcase_util.containers.DictContainer(
        {
            'test': {
                'field1': 1,
                'field2': 2,
            },
            'test2': 100,
            'test3': {
                'field1': {
                    'fieldA': 1
                },
                'field2': {
                    'fieldA': 1
                },
                'field3': {
                    'fieldA': 1
                },
            }
        }
    )

Initialize container, and load content from file::

    dict_container = dcase_util.containers.DictContainer().load(filename='test.yaml')

Accessing field through dotted path::

    # Field exists
    value = dict_container.get_path('test.field1')

    # Using wild card
    values = dict_container.get_path('test3.*')

    # Non existing field with default value
    value = dict_container.get_path('test.fieldA', 'default_value')

Accessing field through list of path parts::

    # Field exists
    value = dict_container.get_path(['test', 'field1'])

    # Non existing field with default value
    value = dict_container.get_path(['test', 'fieldA'], 'default_value)

Setting field through dotted path::

    dict_container.set_path('test.field2', 200)

Getting dotted path to all leaf nodes in the nested dictionary::

    dict_container.get_leaf_path_list()

Getting dotted path to all leaf nodes which starts with 'field' in the nested dictionary::

    dict_container.get_leaf_path_list(target_field_startswith='field')

To save the container into YAML-file::

    dict_container.save(filename='test.yaml')

To load the container data from YAML-file::

    dict_container.load(filename='test.yaml')


List of Dictionaries
::::::::::::::::::::

`dcase_util.containers.ListDictContainer` is meant for storing list of `dcase_util.containers.DictContainer`.

Initialize container with list of dictionaries::

    listdict_container = dcase_util.containers.ListDictContainer(
        [
            {'field1': 1, 'field2': 2},
            {'field1': 10, 'field2': 20},
            {'field1': 100, 'field2': 200},
        ]

    )

Access item in the list based on key and value::

    print(listdict_container.search(key='field1', value=10))
    # DictContainer
    #   field1                            : 10
    #   field2                            : 20

Getting values in specific field of the dictionaries::

    print(ld.get_field(field_name='field2'))
    # [2, 20, 200]


Data Containers
:::::::::::::::

Three is a few data container types available:

- `dcase_util.containers.DataArrayContainer`, data container for array data, internally data is stored in numpy.array.
- `dcase_util.containers.DataMatrix2DContainer`, data container for two-dimensional data matrix, internally data is stored in 2-D numpy.ndarray.
- `dcase_util.containers.DataMatrix3DContainer`, data container for three-dimensional data matrix, internally data is stored in 3-D numpy.ndarray.
- `dcase_util.containers.BinaryMatrixContainer`, data container for two-dimensional binary data matrix, internally data is stored in 2-D numpy.ndarray.

Initialize container with random matrix 10x100, and set time resolution to 20ms::

    data_container = dcase_util.containers.DataMatrix2DContainer(
      data=numpy.random.rand(10,100),
      time_resolution=0.02
    )

When storing, e.g., acoustic features, time resolution corresponds to feature
extraction frame hop length.

Access data matrix directly::

    print(data_container.data.shape)
    # (10, 100)

Show container information::

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

Using focus to get part data between 0.5 sec and 1.0 sec::

    print(data_container.set_focus(start_seconds=0.5, stop_seconds=1.0).get_focused().shape)
    # (10, 25)

Using focus to get part data between frame 10 and 50::

    print(data_container.set_focus(start=10, stop=50).get_focused().shape)
    # (10, 40)

Resetting focus and accessing full data matrix::

    data_container.reset_focus()
    print(data_container.get_focused().shape)
    # (10, 100)

Access frames 1, 2, 10, and 30 ::

    data_container.get_frames(frame_ids=[1,2,10,30])

Access frames 1-5, and only first value per column::

    data_container.get_frames(frame_ids=[1,2,3,4,5], vector_ids=[0])

Transpose matrix::

    transposed_data = data_container.T
    print(transposed_data.shape)
    # (100, 10)

Plot data::

    data_container.plot()

.. plot::

    import dcase_util
    import numpy
    data_container = dcase_util.containers.DataMatrix2DContainer(
      data=numpy.random.rand(10,100),
      time_resolution=0.02
    )
    data_container.plot()

`dcase_util.containers.BinaryMatrixContainer` provides same usage than **DataMatrix2DContainer**
but for the binary content.


Repositories
::::::::::::

`dcase_util.containers.DataRepository` and `dcase_util.containers.FeatureRepository` are containers which can be used
to store multiple other data containers. Repository stores data with two level
information: label and stream. The label is higher level key and stream is
second level one.

Repositories can be used, for example, to store multiple different acoustic
features all related to same audio signal. Stream id can be used to store
features extracted from different audio channels. Later features can be access
using extractor label and stream id.

Initialize container with data::

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

Show container information::

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

Accessing data inside repository::

    data_repository.get_container(label='label1',stream_id='stream1')
    # {'data': 200}

Setting data::

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
