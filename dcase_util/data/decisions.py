#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import numpy
import copy
import scipy

from dcase_util.containers import ObjectContainer


class DecisionEncoder(ObjectContainer):
    def __init__(self, label_list=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list or str
            Label list
            Default value None

        """
        super(DecisionEncoder, self).__init__(**kwargs)

        self.label_list = label_list

    def majority_vote(self, frame_decisions, time_axis=1):
        """Majority vote.

        Parameters
        ----------
        frame_decisions : numpy.ndarray [shape=(d,t) or (t,d)]
            Frame decisions

        time_axis : int
            Axis index for time in the matrix
            Default value 1

        Returns
        -------
        str
            Class label

        """

        # Get data_axis
        if time_axis == 0:
            class_axis = 1
        else:
            class_axis = 0

        if numpy.issubdtype(frame_decisions.dtype, numpy.signedinteger) or numpy.issubdtype(frame_decisions.dtype, numpy.bool_):
            if len(frame_decisions.shape) == 1:
                # We have array, most likely single frame
                return self.label_list[numpy.argmax(frame_decisions)]

            else:
                if isinstance(frame_decisions, numpy.ndarray) and len(frame_decisions.shape) == 2:
                    # We have matrix
                    frame_decisions = numpy.argmax(frame_decisions, axis=class_axis)

                counts = numpy.bincount(frame_decisions)

                return self.label_list[numpy.argmax(counts)]

        else:
            # We have matrix with strings
            if len(frame_decisions.shape) == 1:
                labels, counts = numpy.unique(frame_decisions, return_counts=True)

                majority_voted_label = labels[numpy.argmax(counts)]

                if majority_voted_label in self.label_list:
                    return majority_voted_label
                else:
                    message = '{name}: Label [{label}] not in label_list parameter given to class initializer.'.format(
                        name=self.__class__.__name__,
                        label=majority_voted_label
                    )

                    self.logger.exception(message)
                    raise ValueError(message)
            else:
                message = '{name}: Majority voting not implemented for label matrix.'.format(
                    name=self.__class__.__name__
                )

                self.logger.exception(message)
                raise NotImplementedError(message)

    def many_hot(self, frame_decisions, label_list=None, time_axis=1):
        """Many hot

        Parameters
        ----------
        frame_decisions : numpy.ndarray [shape=(d,t) or (t,d)]
            Frame decisions

        label_list : list or str
            Label list, if None given one for class initializer is used.
            Default value None

        time_axis : int
            Axis index for frames in the matrix
            Default value 1

        Raises
        ------
        ValueError
            No label list given as method parameter or class initializer parameter

        Returns
        -------
        list

        """

        if label_list is None:
            label_list = self.label_list

        if label_list is None:
            message = '{name}: No label_list parameter given to method or class initializer.'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise ValueError(message)

        # Get data_axis
        if time_axis == 0:
            class_axis = 1
        else:
            class_axis = 0

        encoded = []
        for frame_id in range(0, frame_decisions.shape[time_axis]):
            # Get decisions for current frame
            if class_axis == 0:
                current_frame = frame_decisions[:, frame_id].T

            elif class_axis == 1:
                current_frame = frame_decisions[frame_id, :]

            # Encode current frame decisions
            current_frame_encoded = []
            for label_id in numpy.where(current_frame == 1)[0]:
                current_frame_encoded.append(label_list[label_id])

            # Store
            encoded.append(current_frame_encoded)

        return encoded

    def find_contiguous_regions(self, activity_array):
        """Find contiguous regions from bool valued numpy.array.
        Transforms boolean values for each frame into pairs of onsets and offsets.

        Parameters
        ----------
        activity_array : numpy.array [shape=(t)]
            Event activity array, bool values

        Returns
        -------
        numpy.ndarray [shape=(2, number of found changes)]
            Onset and offset indices pairs in matrix

        """

        # Find the changes in the activity_array
        change_indices = numpy.logical_xor(activity_array[1:], activity_array[:-1]).nonzero()[0]

        # Shift change_index with one, focus on frame after the change.
        change_indices += 1

        if activity_array[0]:
            # If the first element of activity_array is True add 0 at the beginning
            change_indices = numpy.r_[0, change_indices]

        if activity_array[-1]:
            # If the last element of activity_array is True, add the length of the array
            change_indices = numpy.r_[change_indices, activity_array.size]

        # Reshape the result into two columns
        return change_indices.reshape((-1, 2))

    def process_activity(self, activity_matrix, window_length, operator="median_filtering", time_axis=1):
        """Process activity array (binary)

        Parameters
        ----------
        activity_matrix : numpy.ndarray
            Activity matrix

        window_length : int
            Window length in analysis frame amount

        operator : str
            Operator to be used ['median_filtering']
            Default value 'median_filtering'

        time_axis : int
            Time axis
            Default value 1

        Raises
        ------
        AssertionError
            Unknown operator.

        Returns
        -------
        numpy.ndarray
            Processed activity

        """

        if operator not in ['median_filtering']:
            message = '{name}: Unknown operator [{operator}].'.format(
                name=self.__class__.__name__,
                operator=operator
            )

            self.logger.exception(message)
            raise ValueError(message)

        if time_axis > 1:
            message = '{name}: Unknown time_axis [{time_axis}].'.format(
                name=self.__class__.__name__,
                time_axis=time_axis
            )

            self.logger.exception(message)
            raise ValueError(message)

        # Get class axis
        if time_axis == 0:
            class_axis = 1

        else:
            class_axis = 0

        # Get a copy of the activity_matrix to prevent data contamination
        activity_matrix = copy.deepcopy(activity_matrix)

        if operator == 'median_filtering':
            for class_id in range(0, activity_matrix.shape[class_axis]):
                # Loop along classes axis, and apply filtering
                if time_axis == 0:
                    activity_matrix[:, class_id] = scipy.signal.medfilt(
                        volume=activity_matrix[:, class_id],
                        kernel_size=window_length
                    )

                elif time_axis == 1:
                    activity_matrix[class_id, :] = scipy.signal.medfilt(
                        volume=activity_matrix[class_id, :],
                        kernel_size=window_length
                    )

        return activity_matrix
