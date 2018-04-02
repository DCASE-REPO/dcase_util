.. _tutorial_metadata:

Metadata
--------

Library provides container `dcase_util.containers.MetaDataContainer` for handling meta data from most of the DCASE related
application areas: acoustic scene classification, event detection, and audio tagging.

In principal, meta data is a list containing meta item dictionaries, and it can be used like normal list.

Creating container
==================

Initialize meta data container with acoustic scene list::

    meta_container_scenes = dcase_util.containers.MetaDataContainer(
        [
            {
                'filename': 'file1.wav',
                'scene_label': 'office'
            },
            {
                'filename': 'file2.wav',
                'scene_label': 'street'
            },
            {
                'filename': 'file3.wav',
                'scene_label': 'home'
            }
        ]
    )

Initialize meta data container with sound event list::

    meta_container_events = dcase_util.containers.MetaDataContainer(
        [
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 10.0,
                'offset': 15.0,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'footsteps',
                'onset': 23.0,
                'offset': 26.0,
            },
            {
                'filename': 'file2.wav',
                'event_label': 'speech',
                'onset': 2.0,
                'offset': 5.0,
            }
        ]
    )

Initialize meta data container with tags::

    meta_container_tags = dcase_util.containers.MetaDataContainer(
        [
            {
                'filename': 'file1.wav',
                'tags': ['cat','dog']
            },
            {
                'filename': 'file2.wav',
             'tags': ['dog']
            },
            {
                'filename': 'file3.wav',
                'tags': ['dog','horse']
            }
        ]
    )

Show content::

    meta_container_scenes.show()
    # MetaDataContainer :: Class
    #   Items                             : 3
    #   Unique
    #     Files                           : 3
    #     Scene labels                    : 3
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         home                        1
    #         office                      1
    #         street                      1

    meta_container_events.show()
    # MetaDataContainer :: Class
    #   Items                             : 3
    #   Unique
    #     Files                           : 2
    #     Scene labels                    : 0
    #     Event labels                    : 2
    #     Tags                            : 0
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #         footsteps                   1          3.00          3.00
    #         speech                      2          8.00          4.00

    meta_container_tags.show()
    # MetaDataContainer :: Class
    #   Items                             : 3
    #   Unique
    #     Files                           : 3
    #     Scene labels                    : 0
    #     Event labels                    : 0
    #     Tags                            : 3
    #
    #   Tag statistics
    #         Tag                     Count
    #         --------------------   ------
    #         cat                         1
    #         dog                         3
    #         horse                       1

Show content and each meta data item::

    meta_container_scenes.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 3
    #   Unique
    #     Files                           : 3
    #     Scene labels                    : 3
    #     Event labels                    : 0
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav                   -        -   office            -                 -                 -
    #         file2.wav                   -        -   street            -                 -                 -
    #         file3.wav                   -        -   home              -                 -                 -
    #
    #   Scene statistics
    #         Scene label             Count
    #         --------------------   ------
    #         home                        1
    #         office                      1
    #         street                      1

    meta_container_events.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 3
    #   Unique
    #     Files                           : 2
    #     Scene labels                    : 0
    #     Event labels                    : 2
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav               10.00    15.00   -                 speech            -                 -
    #         file1.wav               23.00    26.00   -                 footsteps         -                 -
    #         file2.wav                2.00     5.00   -                 speech            -                 -
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #         footsteps                   1          3.00          3.00
    #         speech                      2          8.00          4.00

Loading and saving
==================

Save meta data to file::

    meta_container_events.save(filename='events.txt')

Load meta data from annotation file::

    meta_container_events = dcase_util.containers.MetaDataContainer().load(
        filename='events.txt'
    )

Accessing data
==============

Getting audio files mentioned in the meta data and their count::

    print(meta_container_events.unique_files)
    # ['file1.wav', 'file2.wav']

    print(meta_container_events.file_count)
    # 2

Getting unique scene labels and their count::

    print(meta_container_scenes.unique_scene_labels)
    # ['home', 'office', 'street']

    print(meta_container_scenes.scene_label_count)
    # 3

Getting unique event labels used in the meta data and their count::

    print(meta_container_events.unique_event_labels)
    # ['footsteps', 'speech']

    print(meta_container_scenes.event_label_count)
    # 2

Getting unique tags used in the meta data and their count::

    print(meta_container_tags.unique_tags)
    # ['cat', 'dog', 'horse']

    print(meta_container_tags.tag_count)
    # 3

Filtering
=========

Filtering meta data based on filename::

    filtered = meta_container_events.filter(filename='file1.wav')
    filtered.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 2
    #   Unique
    #     Files                           : 1
    #     Scene labels                    : 0
    #     Event labels                    : 2
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav               10.00    15.00   -                 speech            -                 -
    #         file1.wav               23.00    26.00   -                 footsteps         -                 -
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #         footsteps                   1          3.00          3.00
    #         speech                      1          5.00          5.00

Filtering meta data based on event label::

    filtered = meta_container_events.filter(event_label='speech')
    filtered.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 2
    #   Unique
    #     Files                           : 2
    #     Scene labels                    : 0
    #     Event labels                    : 1
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav               10.00    15.00   -                 speech            -                 -
    #         file2.wav                2.00     5.00   -                 speech            -                 -
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #         speech                      2          8.00          4.00

Filtering meta data based on file and event label::

    filtered = meta_container_events.filter(filename='file1.wav', event_label='speech')
    filtered.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 1
    #   Unique
    #     Files                           : 1
    #     Scene labels                    : 0
    #     Event labels                    : 1
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav               10.00    15.00   -                 speech            -                 -
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #         speech                      1          5.00          5.00

Filtering based on time segment, and make segment start new zero time::

    filtered = meta_container_events.filter_time_segment(filename='file1.wav', start=12, stop=24)
    filtered.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 2
    #   Unique
    #     Files                           : 1
    #     Scene labels                    : 0
    #     Event labels                    : 2
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav                0.00     3.00   -                 speech            -                 -
    #         file1.wav               11.00    12.00   -                 footsteps         -                 -
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #         footsteps                   1          1.00          1.00
    #         speech                      1          3.00          3.00

Processing
==========

Add time offset to the onset and offset set in the meta data items::

    meta_container_events.add_time(time=10)
    meta_container_events.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 3
    #   Unique
    #     Files                           : 2
    #     Scene labels                    : 0
    #     Event labels                    : 2
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav               20.00    25.00   -                 speech            -                 -
    #         file1.wav               33.00    36.00   -                 footsteps         -                 -
    #         file2.wav               12.00    15.00   -                 speech            -                 -
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #         footsteps                   1          3.00          3.00
    #         speech                      2          8.00          4.00

Remove very short events and merge events with small gap between them (same event label)::

    meta_container_events = dcase_util.containers.MetaDataContainer(
        [
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 1.0,
                'offset': 2.0,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 2.05,
                'offset': 2.5,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 5.1,
                'offset': 5.15,
            },
        ]
    )
    processed = meta_container_events.process_events(minimum_event_length=0.2, minimum_event_gap=0.1)
    processed.show_all()
    # MetaDataContainer :: Class
    #   Items                             : 1
    #   Unique
    #     Files                           : 1
    #     Scene labels                    : 0
    #     Event labels                    : 1
    #     Tags                            : 0
    #
    #   Meta data
    #         Source                  Onset   Offset   Scene             Event             Tags              Identifier
    #         --------------------   ------   ------   ---------------   ---------------   ---------------   -----
    #         file1.wav                1.00     2.50   -                 speech            -                 -
    #
    #   Event statistics
    #         Event label             Count   Tot. Length   Avg. Length
    #         --------------------   ------   -----------   -----------
    #        speech                      1          1.50          1.50


Event roll
==========

Converting event list to event roll (binary matrix with event activity)::

    meta_container_events = dcase_util.containers.MetaDataContainer(
        [
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 1.0,
                'offset': 2.0,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 2.05,
                'offset': 2.5,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 5.1,
                'offset': 5.15,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'footsteps',
                'onset': 3.1,
                'offset': 4.15,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'dog',
                'onset': 2.6,
                'offset': 3.6,
            },
        ]
    )
    event_roll = meta_container_events.to_event_roll()

    # Plot
    event_roll.plot()

.. plot::

    import dcase_util
    meta_container_events = dcase_util.containers.MetaDataContainer(
        [
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 1.0,
                'offset': 2.0,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 2.05,
                'offset': 2.5,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'speech',
                'onset': 5.1,
                'offset': 5.15,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'footsteps',
                'onset': 3.1,
                'offset': 4.15,
            },
            {
                'filename': 'file1.wav',
                'event_label': 'dog',
                'onset': 2.6,
                'offset': 3.6,
            },
        ]
    )
    event_roll = meta_container_events.to_event_roll()

    # Plot
    event_roll.plot()