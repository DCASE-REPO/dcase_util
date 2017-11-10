#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import numpy
import math
import logging
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
            Default value "None"

        """
        super(DecisionEncoder, self).__init__(**kwargs)

        self.label_list = label_list

    def majority_vote(self, frame_decisions, frame_axis=0):
        """Majority vote.

        Parameters
        ----------
        frame_decisions : numpy.ndarray [shape=(d,t) or (t,d)]
            Frame decisions

        frame_axis : int
            Axis index for frames in the matrix

        Returns
        -------
        str
            Class label

        """

        if isinstance(frame_decisions, numpy.ndarray) and len(frame_decisions.shape) == 2:
            # We have matrix
            frame_decisions = numpy.argmax(frame_decisions, axis=frame_axis)

        counts = numpy.bincount(frame_decisions)
        return self.label_list[numpy.argmax(counts)]

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

    def process_activity(self, activity_matrix, window_length, operator="median_filtering"):
        """Process activity array (binary)

        Parameters
        ----------
        activity_matrix : numpy.ndarray
            Activity matrix

        window_length : int
            Window length in analysis frame amount

        operator : str ('median_filtering')
            Operator to be used
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
            raise AssertionError(message)

        if operator == 'median_filtering':
            for row_id in range(0,activity_matrix.shape[0]):
                activity_matrix[row_id, :] = scipy.signal.medfilt(
                    volume=activity_matrix[row_id, :],
                    kernel_size=window_length
                )

        return activity_matrix
