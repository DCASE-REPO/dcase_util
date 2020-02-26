#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import numpy
import copy

from dcase_util.containers import ObjectContainer


class ProbabilityEncoder(ObjectContainer):
    def __init__(self, label_list=None, **kwargs):
        """Constructor

        Parameters
        ----------
        label_list : list of str
            Label list

        """

        super(ProbabilityEncoder, self).__init__(**kwargs)

        self.label_list = label_list

    def collapse_probabilities(self, probabilities, operator='sum', time_axis=1):
        """Collapse probabilities along time_axis

        Parameters
        ----------
        probabilities : numpy.ndarray
            Probabilities to be collapsed

        operator : str ('sum', 'prod', 'mean')
            Operator to be used
            Default value 'sum'

        time_axis : int
            time axis
            Default value 1

        Raises
        ------
        AssertionError
            Unknown operator

        Returns
        -------
        numpy.ndarray
            collapsed probabilities

        """

        if operator not in ['sum', 'prod', 'mean']:
            message = '{name}: Unknown operator [{operator}].'.format(
                name=self.__class__.__name__,
                operator=operator
            )

            self.logger.exception(message)
            raise AssertionError(message)

        # Get data_axis
        if time_axis == 0:
            data_axis = 1
        else:
            data_axis = 0

        # Initialize array to store results
        accumulated = numpy.ones(probabilities.shape[data_axis]) * -numpy.inf

        # Loop along data_axis
        for class_id in range(0, probabilities.shape[data_axis]):
            # Get current array
            if time_axis == 0:
                current_array = probabilities[:, class_id]

            elif time_axis == 1:
                current_array = probabilities[class_id, :]

            # Collapse array with given operator
            if operator == 'sum':
                accumulated[class_id] = numpy.sum(current_array)

            elif operator == 'prod':
                accumulated[class_id] = numpy.prod(current_array)

            elif operator == 'mean':
                accumulated[class_id] = numpy.mean(current_array)

        return accumulated

    def collapse_probabilities_windowed(self, probabilities, window_length, operator='sliding_sum', time_axis=1):
        """Collapse probabilities with a sliding window. Window hop size is one.

        Parameters
        ----------
        probabilities : numpy.ndarray
            Probabilities to be collapsed

        window_length : int
            Window length in analysis frame amount.

        operator : str ('sliding_sum', 'sliding_mean', 'sliding_median')
            Operator to be used
            Default value 'sliding_sum'

        time_axis : int
            time axis
            Default value 1

        Raises
        ------
        AssertionError
            Unknown operator

        Returns
        -------
        numpy.ndarray
            collapsed probabilities

        """

        if operator not in ['sliding_sum', 'sliding_mean', 'sliding_median']:
            message = '{name}: Unknown operator [{operator}].'.format(
                name=self.__class__.__name__,
                operator=operator
            )

            self.logger.exception(message)
            raise AssertionError(message)

        if len(probabilities.shape) == 1:
            # In case of array, convert to matrix
            if time_axis == 0:
                probabilities = probabilities.reshape(-1, 1)
            else:
                probabilities = probabilities.reshape(1, -1)

        # Get data_axis
        if time_axis == 0:
            data_axis = 1
        else:
            data_axis = 0

        # Lets keep the system causal and use look-back while smoothing (accumulating) likelihoods
        output_probabilities = copy.deepcopy(probabilities)

        # Loop along data_axis
        for class_id in range(0, probabilities.shape[data_axis]):

            # Get current array
            if time_axis == 0:
                current_array = probabilities[:, class_id]

            elif time_axis == 1:
                current_array = probabilities[class_id, :]

            # Loop windows
            for stop_id in range(0, probabilities.shape[time_axis]):
                start_id = stop_id - window_length

                if start_id < 0:
                    start_id = 0

                if start_id != stop_id:
                    if operator == 'sliding_sum':
                        current_result = numpy.sum(current_array[start_id:stop_id])

                    elif operator == 'sliding_mean':
                        current_result = numpy.mean(current_array[start_id:stop_id])

                    elif operator == 'sliding_median':
                        current_result = numpy.median(current_array[start_id:stop_id])

                else:
                    current_result = current_array[start_id]

                if time_axis == 0:
                    output_probabilities[start_id, class_id] = current_result

                elif time_axis == 1:
                    output_probabilities[class_id, start_id] = current_result

        return output_probabilities

    def binarization(self, probabilities, binarization_type='global_threshold', threshold=0.5, time_axis=1):
        """Binarization

        Parameters
        ----------
        probabilities : numpy.ndarray
            Probabilities to be binarized

        binarization_type : str ('global_threshold', 'class_threshold', 'frame_max')

        threshold : float
            Binarization threshold, value of the threshold are replaced with 1 and under with 0.
            Default value 0.5

        time_axis : int
            Axis index for the frames
            Default value 1

        Raises
        ------
        AssertionError:
            Unknown binarization_type

        Returns
        -------
        numpy.ndarray
            Binarized data

        """

        if binarization_type not in ['global_threshold', 'class_threshold', 'frame_max']:
            message = '{name}: Unknown frame_binarization type [{type}].'.format(
                name=self.__class__.__name__,
                type=binarization_type
            )

            self.logger.exception(message)
            raise AssertionError(message)

        # Get data_axis
        if time_axis == 0:
            data_axis = 1
        else:
            data_axis = 0

        if binarization_type == 'global_threshold':
            return numpy.array(probabilities >= threshold, dtype=int)

        elif binarization_type == 'class_threshold' and isinstance(threshold, list):
            data = []
            for class_id, class_threshold in enumerate(threshold):
                if data_axis == 0:
                    data.append(numpy.array(probabilities[class_id, :] >= class_threshold, dtype=int))

                elif data_axis == 1:
                    data.append(numpy.array(probabilities[:, class_id] >= class_threshold, dtype=int))

            if data_axis == 0:
                return numpy.vstack(data)

            elif data_axis == 1:
                return numpy.vstack(data).T

        elif binarization_type == 'frame_max':
            if data_axis == 0:
                return numpy.array((probabilities / numpy.max(probabilities, axis=0)) == 1, dtype=int)

            elif data_axis == 1:
                return numpy.array((probabilities.T / numpy.max(probabilities, axis=1)).T == 1, dtype=int)

    def max_selection(self, probabilities, label_list=None):
        """Selection based on maximum probability

        Parameters
        ----------
        probabilities : numpy.ndarray
            Probabilities

        label_list : list of str
            Label list
            Default value None

        Returns
        -------
        numpy.ndarray

        """

        if label_list is None:
            label_list = self.label_list

        class_id = numpy.argmax(probabilities)

        if class_id < len(label_list):
            return label_list[class_id]

        else:
            return None
