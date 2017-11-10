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
        label_list : list or str
            Label list

        """

        super(ProbabilityEncoder, self).__init__(**kwargs)

        self.label_list = label_list

    def collapse_probabilities(self, probabilities, operator='sum', frame_axis=0):
        """Collapse probabilities

        Parameters
        ----------
        probabilities : numpy.ndarray
            Probabilities to be accumulated

        operator : str ('sum', 'prod', 'mean')
            Operator to be used

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

        accumulated = numpy.ones(probabilities.shape[frame_axis]) * -numpy.inf
        for row_id in range(0, probabilities.shape[frame_axis]):
            if operator == 'sum':
                accumulated[row_id] = numpy.sum(probabilities[row_id, :])
            elif operator == 'prod':
                accumulated[row_id] = numpy.prod(probabilities[row_id, :])
            elif operator == 'mean':
                accumulated[row_id] = numpy.mean(probabilities[row_id, :])

        return accumulated

    def collapse_probabilities_windowed(self, probabilities, window_length, operator='sliding_sum'):
        """Collapse probabilities in windows

        Parameters
        ----------
        probabilities : numpy.ndarray
            Probabilities to be accumulated

        window_length : int
            Window length in analysis frame amount

        operator : str ('sliding_sum', 'sliding_mean', 'sliding_median')
            Operator to be used

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

        # Lets keep the system causal and use look-back while smoothing (accumulating) likelihoods
        output_probabilities = copy.deepcopy(probabilities)
        for stop_id in range(0, probabilities.shape[0]):
            start_id = stop_id - window_length

            if start_id < 0:
                start_id = 0

            if start_id != stop_id:
                if operator == 'sliding_sum':
                    output_probabilities[start_id] = numpy.sum(probabilities[start_id:stop_id])

                elif operator == 'sliding_mean':
                    output_probabilities[start_id] = numpy.mean(probabilities[start_id:stop_id])

                elif operator == 'sliding_median':
                    output_probabilities[start_id] = numpy.median(probabilities[start_id:stop_id])

            else:
                output_probabilities[start_id] = probabilities[start_id]

        return output_probabilities

    def binarization(self, probabilities, binarization_type='global_threshold', threshold=0.5, frame_axis=0):
        """Binarization

        Parameters
        ----------
        probabilities : numpy.ndarray
            Probabilities to be binarized

        binarization_type : str ('global_threshold', 'class_threshold', 'frame_max')

        threshold : float
            Binarization threshold, value of the threshold are replaced with 1 and under with 0.

        frame_axis : int
            Axis index for the frames

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

        if binarization_type == 'global_threshold':
            return numpy.array(probabilities >= threshold, dtype=int)

        elif binarization_type == 'class_threshold' and isinstance(threshold, list):
            data = []
            for class_id, class_threshold in enumerate(threshold):
                if frame_axis == 0:
                    data.append(numpy.array(probabilities[class_id, :] >= class_threshold, dtype=int))
                elif frame_axis == 1:
                    data.append(numpy.array(probabilities[:, class_id] >= class_threshold, dtype=int))

            if frame_axis == 0:
                return numpy.vstack(data)
            elif frame_axis == 1:
                return numpy.vstack(data).T

        elif binarization_type == 'frame_max':
            if frame_axis == 0:
                return numpy.array((probabilities / numpy.max(probabilities, axis=0)) == 1, dtype=int)

            elif frame_axis == 1:
                return numpy.array((probabilities.T / numpy.max(probabilities, axis=1)).T == 1, dtype=int)

    def max_selection(self, probabilities):
        class_id = numpy.argmax(probabilities)
        if class_id < len(self.label_list):
            return self.label_list[class_id]
        else:
            return None