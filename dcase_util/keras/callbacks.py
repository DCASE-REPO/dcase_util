# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
from six import iteritems
import numpy
import os
import collections
import logging
import datetime

from dcase_util.ui import FancyStringifier, FancyHTMLStringifier, FancyLogger, FancyPrinter, FancyHTMLPrinter
from dcase_util.utils import Timer, setup_logging, is_jupyter


class BaseCallback(object):
    """Base class for Callbacks
    """
    def __init__(self, epochs=None, manual_update=False, external_metric_labels=None, **kwargs):
        self.params = None
        self.model = None

        self.manual_update = manual_update

        self.epochs = epochs
        self.epoch = 0

        if external_metric_labels is None:
            external_metric_labels = collections.OrderedDict()

        self.external_metric_labels = external_metric_labels
        self.external_metric = collections.OrderedDict()

        self.keras_metrics = [
            'binary_accuracy',
            'categorical_accuracy',
            'sparse_categorical_accuracy',
            'top_k_categorical_accuracy'
        ]

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()
        return logger

    def set_model(self, model):
        self.model = model

    def set_params(self, params):
        self.params = params

    def on_train_begin(self, logs=None):
        pass

    def on_train_end(self, logs=None):
        pass

    def on_epoch_begin(self, epoch, logs=None):
        pass

    def on_batch_begin(self, batch, logs=None):
        pass

    def on_batch_end(self, batch, logs=None):
        pass

    def on_epoch_end(self, epoch, logs=None):
        pass

    def update(self):
        pass

    def add_external_metric(self, metric_label):
        pass

    def set_external_metric_value(self, metric_label, metric_value):
        pass

    def get_operator(self, metric):
        metric = metric.lower()
        if metric.endswith('error_rate') or metric.endswith('er'):
            return numpy.less

        elif (metric.endswith('f_measure') or metric.endswith('fmeasure') or metric.endswith('fscore') or
              metric.endswith('f-score')):

            return numpy.greater

        elif metric.endswith('accuracy') or metric.endswith('acc'):
            return numpy.greater

        else:
            return numpy.less


class ProgressLoggerCallback(BaseCallback):
    """Keras callback to show metrics in logging interface. Implements Keras Callback API.

    This callback is very similar to standard ``ProgbarLogger`` Keras callback, however it adds support for logging
    interface, and external metrics (metrics calculated outside Keras training process).

    """

    def __init__(self,
                 manual_update=False, epochs=None, external_metric_labels=None,
                 metric=None, loss=None, manual_update_interval=1, output_type='logging', show_timing=True,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        epochs : int
            Total amount of epochs
            Default value None

        metric : str
            Metric name
            Default value None

        manual_update : bool
            Manually update callback, use this to when injecting external metrics
            Default value False

        manual_update_interval : int
            Epoch interval for manual update, used anticipate updates
            Default value 1

        output_type : str
            Output type, either 'logging', 'console', or 'notebook'
            Default value 'logging'

        show_timing : bool
            Show per epoch time and estimated time remaining
            Default value True

        external_metric_labels : dict or OrderedDict
            Dictionary with {'metric_label': 'metric_name'}
            Default value None

        """

        kwargs.update({
            'manual_update': manual_update,
            'epochs': epochs,
            'external_metric_labels': external_metric_labels,
        })

        super(ProgressLoggerCallback, self).__init__(**kwargs)

        if isinstance(metric, str):
            self.metric = metric

        elif callable(metric):
            self.metric = metric.__name__

        self.loss = loss

        self.manual_update_interval = manual_update_interval

        self.output_type = output_type

        self.show_timing = show_timing

        self.timer = Timer()

        self.ui = FancyStringifier()

        if self.output_type == 'logging':
            self.output_target = FancyLogger()

        elif self.output_type == 'console':
            self.output_target = FancyPrinter()

        elif self.output_type == 'notebook':
            self.output_target = FancyHTMLPrinter()
            self.ui = FancyHTMLStringifier()

        self.seen = 0
        self.log_values = []

        self.most_recent_values = collections.OrderedDict()
        self.most_recent_values['l_tra'] = None
        self.most_recent_values['l_val'] = None
        self.most_recent_values['m_tra'] = None
        self.most_recent_values['m_val'] = None

        self.data = {
            'l_tra': numpy.empty((self.epochs,)),
            'l_val': numpy.empty((self.epochs,)),
            'm_tra': numpy.empty((self.epochs,)),
            'm_val': numpy.empty((self.epochs,)),
        }
        self.data['l_tra'][:] = numpy.nan
        self.data['l_val'][:] = numpy.nan
        self.data['m_tra'][:] = numpy.nan
        self.data['m_val'][:] = numpy.nan

        for metric_label in self.external_metric_labels:
            self.data[metric_label] = numpy.empty((self.epochs,))
            self.data[metric_label][:] = numpy.nan

        self.header_shown = False
        self.last_update_epoch = 0

        self.target = None
        self.first_epoch = None
        self.total_time = 0

    def on_train_begin(self, logs=None):
        if self.epochs is None:
            self.epochs = self.params['epochs']

        if not self.header_shown:
            output = ''
            output += self.ui.line('Training') + '\n'

            if self.external_metric_labels:
                output += self.ui.row(
                    '', 'Loss', 'Metric', 'Ext. metrics', '',
                    widths=[10, 26, 26, len(self.external_metric_labels)*15, 17]
                ) + '\n'

                header2 = ['', self.loss, self.metric]
                header3 = ['Epoch', 'Train', 'Val', 'Train', 'Val']
                widths = [10, 13, 13, 13, 13]
                for metric_label, metric_name in iteritems(self.external_metric_labels):
                    header2.append('')
                    header3.append(metric_name)
                    widths.append(15)

                if self.show_timing:
                    header2.append('')
                    header3.append('Step time')
                    widths.append(20)

                    header2.append('')
                    header3.append('Remaining time')
                    widths.append(20)

                output += self.ui.row(*header2) + '\n'
                output += self.ui.row(*header3, widths=widths) + '\n'
                output += self.ui.row_sep()

            else:
                if self.show_timing:
                    output += self.ui.row('', 'Loss', 'Metric', '', '', widths=[10, 36, 36, 16, 15]) + '\n'
                    output += self.ui.row('', self.loss, self.metric, '') + '\n'
                    output += self.ui.row(
                        'Epoch', 'Train', 'Val', 'Train', 'Val', 'Step', 'Remaining',
                        widths=[10, 18, 18, 18, 18, 16, 15]
                    ) + '\n'
                else:
                    output += self.ui.row('', 'Loss', 'Metric', widths=[10, 36, 36]) + '\n'
                    output += self.ui.row('', self.loss, self.metric) + '\n'
                    output += self.ui.row(
                        'Epoch', 'Train', 'Val', 'Train', 'Val',
                        widths=[10, 18, 18, 18, 18]
                    ) + '\n'
                output += self.ui.row_sep()

            self.output_target.line(output)

            # Show header only once
            self.header_shown = True

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch = epoch + 1

        if 'steps' in self.params:
            self.target = self.params['steps']

        elif 'samples' in self.params:
            self.target = self.params['samples']

        self.seen = 0
        self.timer.start()

    def on_batch_begin(self, batch, logs=None):
        if self.target and self.seen < self.target:
            self.log_values = []

    def on_batch_end(self, batch, logs=None):
        logs = logs or {}
        batch_size = logs.get('size', 0)
        self.seen += batch_size

        for k in self.params['metrics']:
            if k in logs:
                self.log_values.append((k, logs[k]))

    def on_epoch_end(self, epoch, logs=None):
        self.timer.stop()
        self.total_time += self.timer.elapsed()
        self.epoch = epoch

        if self.first_epoch is None:
            # Store first epoch number
            self.first_epoch = self.epoch

        logs = logs or {}

        # Reset values
        self.most_recent_values['l_tra'] = None
        self.most_recent_values['l_val'] = None
        self.most_recent_values['m_tra'] = None
        self.most_recent_values['m_val'] = None

        # Collect values
        for k in self.params['metrics']:
            if k in logs:
                self.log_values.append((k, logs[k]))
                if k == 'loss':
                    self.data['l_tra'][self.epoch] = logs[k]
                    self.most_recent_values['l_tra'] = '{:4.3f}'.format(logs[k])

                elif k == 'val_loss':
                    self.data['l_val'][self.epoch] = logs[k]
                    self.most_recent_values['l_val'] = '{:4.3f}'.format(logs[k])

                elif self.metric and k.endswith(self.metric):
                    if k.startswith('val_'):
                        self.data['m_val'][self.epoch] = logs[k]
                        self.most_recent_values['m_val'] = '{:4.3f}'.format(logs[k])

                    else:
                        self.data['m_tra'][self.epoch] = logs[k]
                        self.most_recent_values['m_tra'] = '{:4.3f}'.format(logs[k])

        for metric_label in self.external_metric_labels:
            if metric_label in self.external_metric:
                metric_name = self.external_metric_labels[metric_label]
                value = self.external_metric[metric_label]
                if metric_name.endswith('f_measure') or metric_name.endswith('f_score'):
                    self.most_recent_values[metric_label] = '{:3.1f}'.format(value * 100)
                else:
                    self.most_recent_values[metric_label] = '{:4.3f}'.format(value)

        if (not self.manual_update or
           (self.epoch - self.last_update_epoch > 0 and (self.epoch+1) % self.manual_update_interval)):

            # Update logged progress
            self.update_progress_log()

    def update(self):
        """Update

        """
        self.update_progress_log()
        self.last_update_epoch = self.epoch

    def update_progress_log(self):
        """Update progress to logging interface

        """

        if self.epoch - self.last_update_epoch:
            data = [
                self.epoch,
                self.data['l_tra'][self.epoch],
                self.data['l_val'][self.epoch] if 'l_val' in self.most_recent_values else '-',
                self.data['m_tra'][self.epoch],
                self.data['m_val'][self.epoch] if self.most_recent_values['m_val'] else '-'
            ]
            types = [
                'int', 'float4', 'float4', 'float4', 'float4'
            ]
            for metric_label in self.external_metric_labels:
                if metric_label in self.external_metric:
                    value = self.data[metric_label][self.epoch]

                    if numpy.isnan(value):
                        value = ' ' * 10
                    else:
                        if self.external_metric_labels[metric_label].endswith('f_measure') or self.external_metric_labels[metric_label].endswith('f_score'):
                            value = float(value) * 100
                            types.append('float2')

                        else:
                            value = float(value)
                            types.append('float4')

                    data.append(value)

                else:
                    data.append('')

            if self.show_timing:
                # Add step time
                step_time = datetime.timedelta(seconds=self.timer.elapsed())
                data.append(str(step_time)[:-3])
                types.append('str')

                # Add remaining time
                average_time_per_epoch = self.total_time / float(self.epoch-(self.first_epoch-1))
                remaining_time_seconds = datetime.timedelta(
                    seconds=(self.epochs - 1 - self.epoch) * average_time_per_epoch
                )
                data.append('-'+str(remaining_time_seconds).split('.', 2)[0])
                types.append('str')

            output = self.ui.row(*data, types=types)

            self.output_target.line(output)

    def add_external_metric(self, metric_id):
        """Add external metric to be monitored

        Parameters
        ----------
        metric_id : str
            Metric name

        """

        if metric_id not in self.external_metric_labels:
            self.external_metric_labels[metric_id] = metric_id

        if metric_id not in self.data:
            self.data[metric_id] = numpy.empty((self.epochs,))
            self.data[metric_id][:] = numpy.nan

    def set_external_metric_value(self, metric_label, metric_value):
        """Add external metric value

        Parameters
        ----------
        metric_label : str
            Metric label

        metric_value : numeric
            Metric value

        """

        self.external_metric[metric_label] = metric_value
        self.data[metric_label][self.epoch] = metric_value


class ProgressPlotterCallback(ProgressLoggerCallback):
    """Keras callback to plot progress during the training process and save final progress into figure.
    Implements Keras Callback API.

    """

    def __init__(self,
                 epochs=None, manual_update=False, external_metric_labels=None, metric=None, loss=None,
                 filename=None, plotting_rate=10, interactive=True, save=False, focus_span=10,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        epochs : int
            Total amount of epochs
            Default value None

        metric : str
            Metric name
            Default value None

        manual_update : bool
            Manually update callback, use this to when injecting external metrics
            Default value False

        interactive : bool
            Show plot during the training and update with plotting rate
            Default value True

        plotting_rate : int
            Plot update rate in seconds
            Default value 10

        save : bool
            Save plot on disk, plotting rate applies
            Default value False

        filename : str
            Filename of figure
            Default value None

        focus_span : int
            Epoch amount to highlight, and show separately in the plot.
            Default value 10

        """

        kwargs.update({
            'manual_update': manual_update,
            'epochs': epochs,
            'external_metric_labels': external_metric_labels,
            'metric': metric,
            'loss': loss,
        })

        super(ProgressPlotterCallback, self).__init__(**kwargs)
        self.filename = filename

        if filename is not None:
            # Get file format for the output plot
            file_extension = os.path.splitext(self.filename)[1]
            if file_extension == '.eps':
                self.format = 'eps'

            elif file_extension == '.svg':
                self.format = 'svg'

            elif file_extension == '.pdf':
                self.format = 'pdf'

            elif file_extension == '.png':
                self.format = 'png'

        self.plotting_rate = plotting_rate
        self.interactive = interactive
        self.save = save
        self.focus_span = focus_span

        if self.focus_span > self.epochs:
            self.focus_span = self.epochs

        self.timer.start()
        self.data = {
            'l_tra': numpy.empty((self.epochs,)),
            'l_val': numpy.empty((self.epochs,)),
            'm_tra': numpy.empty((self.epochs,)),
            'm_val': numpy.empty((self.epochs,)),
        }
        self.data['l_tra'][:] = numpy.nan
        self.data['l_val'][:] = numpy.nan
        self.data['m_tra'][:] = numpy.nan
        self.data['m_val'][:] = numpy.nan

        for metric_label in self.external_metric_labels:
            self.data[metric_label] = numpy.empty((self.epochs,))
            self.data[metric_label][:] = numpy.nan

        self.ax1_1 = None
        self.ax1_2 = None

        self.ax2_1 = None
        self.ax2_2 = None

        self.extra_main = {}
        self.extra_highlight = {}

        import matplotlib.pyplot as plt
        import warnings
        import matplotlib.cbook
        warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

        figure_height = 8
        if len(self.external_metric_labels) > 2:
            figure_height = 8 + len(self.external_metric_labels)

        self.figure = plt.figure(num=None, figsize=(18, figure_height), dpi=80, facecolor='w', edgecolor='k')
        self.draw()
        if self.interactive:
            plt.show(block=False)
            plt.pause(0.1)

    def draw(self):
        """Draw plot

        """

        import matplotlib.patches as patches
        import matplotlib.pyplot as plt

        plt.figure(self.figure.number)
        row_count = 2+len(self.external_metric_labels)

        self.ax1_1 = plt.subplot2grid((row_count, 4), (0, 0), rowspan=1, colspan=3)
        self.ax1_2 = plt.subplot2grid((row_count, 4), (0, 3), rowspan=1, colspan=1)

        self.ax2_1 = plt.subplot2grid((row_count, 4), (1, 0), rowspan=1, colspan=3)
        self.ax2_2 = plt.subplot2grid((row_count, 4), (1, 3), rowspan=1, colspan=1)

        self.extra_main = {}
        self.extra_highlight = {}
        row_id = 2
        for metric_label in self.external_metric_labels:
            self.extra_main[metric_label] = plt.subplot2grid((row_count, 4), (row_id, 0), rowspan=1, colspan=3)
            self.extra_highlight[metric_label] = plt.subplot2grid((row_count, 4), (row_id, 3), rowspan=1, colspan=1)
            row_id += 1

        span = [self.epoch - self.focus_span, self.epoch]
        if span[0] < 0:
            span[0] = 0

        # PLOT 1 / Main
        self.ax1_1.cla()
        self.ax1_1.set_title('Loss')
        self.ax1_1.set_ylabel('Model Loss')
        self.ax1_1.plot(
            numpy.arange(self.epochs),
            self.data['l_tra'],
            lw=3,
            color='red',
        )
        self.ax1_1.plot(
            numpy.arange(self.epochs),
            self.data['l_val'],
            lw=3,
            color='green',
        )
        self.ax1_1.add_patch(
            patches.Rectangle(
                (span[0], self.ax1_1.get_ylim()[0]),  # (x,y)
                width=span[1]-span[0],
                height=self.ax1_1.get_ylim()[1],
                facecolor="#000000",
                alpha=0.05
            )
        )
        # Horizontal lines
        if not numpy.all(numpy.isnan(self.data['l_tra'])):
            self.ax1_1.axhline(y=numpy.nanmin(self.data['l_tra']), lw=1, color='red', linestyle='--')
            self.ax1_1.axhline(y=numpy.nanmin(self.data['l_val']), lw=1, color='green', linestyle='--')

        self.ax1_1.legend(['Train', 'Validation'], loc='upper right')
        self.ax1_1.set_xlim([0, self.epochs - 1])
        self.ax1_1.set_xticklabels([])
        self.ax1_1.grid(True)

        # PLOT 1 / Highlighted area
        self.ax1_2.cla()
        self.ax1_2.set_title('Loss / Highlighted area')
        self.ax1_2.set_ylabel('Model Loss')
        self.ax1_2.plot(
            numpy.arange(span[0], span[1]),
            self.data['l_tra'][span[0]:span[1]],
            lw=3,
            color='red',
        )

        self.ax1_2.plot(
            numpy.arange(span[0], span[1]),
            self.data['l_val'][span[0]:span[1]],
            lw=3,
            color='green',
        )

        self.ax1_2.set_xticklabels([])
        self.ax1_2.grid(True)
        self.ax1_2.yaxis.tick_right()
        self.ax1_2.yaxis.set_label_position("right")

        # PLOT 2 / Main
        self.ax2_1.cla()
        self.ax2_1.set_title('Metric')
        self.ax2_1.set_ylabel(self.metric)

        # Plots
        self.ax2_1.plot(
            numpy.arange(self.epochs),
            self.data['m_tra'],
            lw=3,
            color='red',
        )
        self.ax2_1.plot(
            numpy.arange(self.epochs),
            self.data['m_val'],
            lw=3,
            color='green',
        )
        # Horizontal lines
        if not numpy.all(numpy.isnan(self.data['m_tra'])):
            if self.get_operator(metric=self.metric) == numpy.greater:
                h_tra_line_y = numpy.nanmax(self.data['m_tra'])
                h_val_line_y = numpy.nanmax(self.data['m_val'])
            else:
                h_tra_line_y = numpy.nanmin(self.data['m_tra'])
                h_val_line_y = numpy.nanmin(self.data['m_tra'])
            self.ax2_1.axhline(y=h_tra_line_y, lw=1, color='red', linestyle='--')
            self.ax2_1.axhline(y=h_val_line_y, lw=1, color='green', linestyle='--')

        self.ax2_1.add_patch(
            patches.Rectangle(
                (span[0], self.ax2_1.get_ylim()[0]),  # (x,y)
                width=span[1]-span[0],
                height=self.ax2_1.get_ylim()[1],
                facecolor="#000000",
                alpha=0.05
            )
        )

        if self.get_operator(metric=self.metric) == numpy.greater:
            legend_location = 'lower right'
        else:
            legend_location = 'upper right'

        self.ax2_1.legend(['Train', 'Validation'], loc=legend_location)
        self.ax2_1.set_xlim([0, self.epochs - 1])
        if self.external_metric_labels:
            self.ax2_1.set_xticklabels([])
        self.ax2_1.grid(True)

        # PLOT 2 / Highlighted area
        self.ax2_2.cla()
        self.ax2_2.set_title('Metric / Highlighted area')
        self.ax2_2.set_ylabel(self.metric)
        self.ax2_2.plot(
            numpy.arange(span[0], span[1]),
            self.data['m_tra'][span[0]:span[1]],
            lw=3,
            color='red',
        )
        self.ax2_2.plot(
            numpy.arange(span[0], span[1]),
            self.data['m_val'][span[0]:span[1]],
            lw=3,
            color='green',
        )
        self.ax2_2.set_xticklabels([])
        self.ax2_2.grid(True)
        self.ax2_2.yaxis.tick_right()
        self.ax2_2.yaxis.set_label_position("right")

        for mid, metric_label in enumerate(self.external_metric_labels):
            metric_name = self.external_metric_labels[metric_label]

            if metric_name.endswith('f_measure') or metric_name.endswith('f_score'):
                factor = 100
            else:
                factor = 1

            # PLOT 3 / Main
            self.extra_main[metric_label].cla()
            self.extra_main[metric_label].set_title('External metric')
            self.extra_main[metric_label].set_ylabel(str(metric_label))

            mask = numpy.isfinite(self.data[metric_label])
            self.extra_main[metric_label].plot(
                numpy.arange(self.epochs)[mask],
                self.data[metric_label][mask]*factor,
                lw=3,
                color='green',
                marker='o',
            )
            self.extra_main[metric_label].add_patch(
                patches.Rectangle(
                    (span[0], self.extra_main[metric_label].get_ylim()[0]),  # (x,y)
                    width=span[1]-span[0],
                    height=self.extra_main[metric_label].get_ylim()[1],
                    facecolor="#000000",
                    alpha=0.05
                )
            )

            # Horizontal lines
            if not numpy.all(numpy.isnan(self.data[metric_label][mask])):
                if self.get_operator(metric=str(metric_label)) == numpy.greater:
                    h_extra_line_y = numpy.nanmax((self.data[metric_label][mask]*factor))
                else:
                    h_extra_line_y = numpy.nanmin((self.data[metric_label][mask]*factor))
                self.extra_main[metric_label].axhline(y=h_extra_line_y, lw=1, color='blue', linestyle='--')

            if self.get_operator(metric=self.metric) == numpy.greater:
                legend_location = 'lower right'
            else:
                legend_location = 'upper right'

            self.extra_main[metric_label].legend(['Validation'], loc=legend_location)
            self.extra_main[metric_label].set_xlim([0, self.epochs - 1])

            if (mid + 1) < len(self.external_metric_labels):
                self.extra_main[metric_label].set_xticklabels([])
            else:
                self.extra_main[metric_label].set_xlabel('Epochs')

            self.extra_main[metric_label].grid(True)

            # PLOT 3 / Highlighted area
            self.extra_highlight[metric_label].cla()
            self.extra_highlight[metric_label].set_title('External metric / Highlighted area')
            self.extra_highlight[metric_label].set_ylabel(str(metric_label))
            highlight_data = self.data[metric_label][span[0]:span[1]]*factor
            mask = numpy.isfinite(highlight_data)
            self.extra_highlight[metric_label].plot(
                numpy.arange(span[0], span[1])[mask],
                highlight_data[mask],
                lw=3,
                color='green',
                marker='o',
            )

            if (mid + 1) < len(self.external_metric_labels):
                self.extra_highlight[metric_label].set_xticklabels([])
            else:
                self.extra_highlight[metric_label].set_xlabel('Epochs')

            self.extra_highlight[metric_label].yaxis.tick_right()
            self.extra_highlight[metric_label].yaxis.set_label_position("right")
            self.extra_highlight[metric_label].grid(True)

        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1, wspace=0.02, hspace=0.2)

    def on_train_begin(self, logs=None):
        if self.epochs is None:
            self.epochs = self.params['epochs']

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch = epoch + 1
        self.seen = 0

    def on_epoch_end(self, epoch, logs=None):
        self.epoch = epoch

        logs = logs or {}

        # Collect values
        for k in self.params['metrics']:
            if k in logs:
                self.log_values.append((k, logs[k]))
                if k == 'loss':
                    self.data['l_tra'][self.epoch] = logs[k]

                elif k == 'val_loss':
                    self.data['l_val'][self.epoch] = logs[k]

                elif self.metric and k.endswith(self.metric):
                    if k.startswith('val_'):
                        self.data['m_val'][self.epoch] = logs[k]
                    else:
                        self.data['m_tra'][self.epoch] = logs[k]

        if not self.manual_update:
            # Update logged progress
            self.update()

    def update(self):
        """Update

        """

        import matplotlib.pyplot as plt
        if self.timer.elapsed() > self.plotting_rate:
            self.draw()
            self.figure.canvas.flush_events()
            if self.interactive:
                plt.pause(0.01)

            if self.save:
                plt.savefig(self.filename, bbox_inches='tight', format=self.format, dpi=1000)

            self.timer.start()

    def add_external_metric(self, metric_label):
        """Add external metric to be monitored

        Parameters
        ----------
        metric_label : str
            Metric label

        """

        if metric_label not in self.external_metric_labels:
            self.external_metric_labels[metric_label] = metric_label

        if metric_label not in self.data:
            self.data[metric_label] = numpy.empty((self.epochs,))
            self.data[metric_label][:] = numpy.nan

    def set_external_metric_value(self, metric_label, metric_value):
        """Add external metric value

        Parameters
        ----------
        metric_label : str
            Metric label

        metric_value : numeric
            Metric value

        """

        self.external_metric[metric_label] = metric_value
        self.data[metric_label][self.epoch] = metric_value

    def close(self):
        """Manually close progress logging

        """

        import matplotlib.pyplot as plt

        if self.save:
            self.draw()
            plt.savefig(self.filename, bbox_inches='tight', format=self.format, dpi=1000)

        plt.close(self.figure)


class StopperCallback(BaseCallback):
    """Keras callback to stop training when improvement has not seen in specified amount of epochs.
    Implements Keras Callback API.

    Callback is very similar to standard ``EarlyStopping`` Keras callback, however it adds support for external metrics
    (calculated outside Keras training process).

    """

    def __init__(self,
                 epochs=None, manual_update=False,
                 monitor='val_loss', patience=0, min_delta=0, initial_delay=10,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        epochs : int
            Total amount of epochs

        manual_update : bool
            Manually update callback, use this to when injecting external metrics

        monitor : str
            Metric value to be monitored

        patience : int
            Number of epochs with no improvement after which training will be stopped.

        min_delta : float
            Minimum change in the monitored quantity to qualify as an improvement.

        initial_delay : int
            Amount of epochs to wait at the beginning before quantity is monitored.

        """

        kwargs.update({
            'epochs': epochs,
            'manual_update': manual_update,
        })

        super(StopperCallback, self).__init__(**kwargs)

        self.monitor = monitor
        self.patience = patience
        self.min_delta = min_delta
        self.initial_delay = initial_delay

        self.wait = None
        self.stopped_epoch = None
        self.model = None
        self.params = None
        self.last_update_epoch = 0
        self.stopped = False

        self.metric_data = {
            self.monitor: numpy.empty((self.epochs,))
        }
        self.metric_data[self.monitor][:] = numpy.nan

        mode = kwargs.get('mode', 'auto')
        if mode not in ['min', 'max', 'auto']:
            mode = 'auto'

        if mode == 'min':
            self.monitor_op = numpy.less
        elif mode == 'max':
            self.monitor_op = numpy.greater
        else:
            self.monitor_op = self.get_operator(metric=self.monitor)

        self.best = numpy.Inf if self.monitor_op == numpy.less else -numpy.Inf

        if self.monitor_op == numpy.greater:
            self.min_delta *= 1
        else:
            self.min_delta *= -1

    def on_train_begin(self, logs=None):
        if self.epochs is None:
            self.epochs = self.params['epochs']

        if self.wait is None:
            self.wait = 0

        if self.stopped_epoch is None:
            self.stopped_epoch = 0

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch = epoch + 1

    def on_epoch_end(self, epoch, logs=None):
        self.epoch = epoch
        if self.monitor in logs:
            self.metric_data[self.monitor][self.epoch] = logs.get(self.monitor)

        if not self.manual_update:
            self.update()

    def set_external_metric_value(self, metric_label, metric_value):
        """Add external metric value

        Parameters
        ----------
        metric_label : str
            Metric label

        metric_value : numeric
            Metric value

        """

        if metric_label not in self.metric_data:
            self.metric_data[metric_label] = numpy.empty((self.epochs,))
            self.metric_data[metric_label][:] = numpy.nan

        self.metric_data[metric_label][self.epoch] = metric_value

    def stop(self):
        return self.stopped

    def update(self):
        if self.epoch > self.initial_delay:
            # get current metric value
            current = self.metric_data[self.monitor][self.epoch]
            if numpy.isnan(current):
                message = '{name}: Metric to monitor is Nan, metric:[{metric}]'.format(
                    name=self.__class__.__name__,
                    metric=self.monitor
                )
                self.logger.exception(message)
                raise ValueError(message)

            if self.monitor_op(current - self.min_delta, self.best):
                # New best value found
                self.best = current
                self.wait = 0

            else:
                if self.wait >= self.patience:
                    # Stopping criteria met => return false
                    self.stopped_epoch = self.epoch
                    self.model.stop_training = True
                    self.logger.info('  Stopping criteria met at epoch[{epoch:d}]'.format(
                        epoch=self.epoch,
                    ))
                    self.logger.info('    metric[{metric}], patience[{patience:d}]'.format(
                        metric=self.monitor,
                        current='{:4.4f}'.format(current),
                        patience=self.patience
                    ))
                    self.logger.info('  ')
                    self.stopped = True
                    return self.stopped

                # Increase waiting counter
                self.wait += self.epoch - self.last_update_epoch

        self.last_update_epoch = self.epoch
        return self.stopped


class StasherCallback(BaseCallback):
    """Keras callback to monitor training process and store best model. Implements Keras Callback API.

    This callback is very similar to standard ``ModelCheckpoint`` Keras callback, however it adds support for external
    metrics (metrics calculated outside Keras training process).

    """

    def __init__(self,
                 epochs=None, manual_update=False,
                 monitor='val_loss', mode='auto', period=1, initial_delay=10, save_weights=False, file_path=None,
                 **kwargs):
        """Constructor

        Parameters
        ----------
        epochs : int
            Total amount of epochs
            Default value None

        manual_update : bool
            Manually update callback, use this to when injecting external metrics
            Default value False

        monitor : str
            Metric to monitor
            Default value 'val_loss'

        mode : str
            Which way metric is interpreted, values {auto, min, max}
            Default value 'auto'

        period : int
            Save only after every Nth epoch
            Default value 1

        initial_delay : int
            Amount of epochs to wait at the beginning before quantity is monitored.
            Default value 10

        save_weights : bool
            Save weight to the disk
            Default value False

        file_path : str
            File name for model weight
            Default value None

        """

        kwargs.update({
            'epochs': epochs,
            'manual_update': manual_update,
        })

        super(StasherCallback, self).__init__(**kwargs)

        self.monitor = monitor
        self.period = period
        self.initial_delay = initial_delay

        self.save_weights = save_weights
        self.file_path = file_path

        self.epochs_since_last_save = 0

        if mode not in ['auto', 'min', 'max']:
            mode = 'auto'

        if mode == 'min':
            self.monitor_op = numpy.less

        elif mode == 'max':
            self.monitor_op = numpy.greater

        else:
            self.monitor_op = self.get_operator(metric=self.monitor)

        self.best = numpy.Inf if self.monitor_op == numpy.less else -numpy.Inf

        self.metric_data = {
            self.monitor: numpy.empty((self.epochs,))
        }
        self.metric_data[self.monitor][:] = numpy.nan
        self.best_model_weights = None
        self.best_model_epoch = 0
        self.last_logs = None

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch = epoch + 1

    def on_epoch_end(self, epoch, logs=None):
        self.epoch = epoch
        if self.monitor in logs:
            self.metric_data[self.monitor][self.epoch] = logs.get(self.monitor)

        self.last_logs = logs

        if not self.manual_update:
            self.update()

    def update(self):
        if self.epoch > self.initial_delay:
            self.epochs_since_last_save += 1
            if self.epochs_since_last_save >= self.period:
                self.epochs_since_last_save = 0

                current = self.metric_data[self.monitor][self.epoch]
                if numpy.isnan(current):
                    message = '{name}: Metric to monitor is Nan, metric:[{metric}]'.format(
                        name=self.__class__.__name__,
                        metric=self.monitor
                    )
                    self.logger.exception(message)
                    raise ValueError(message)

                else:
                    if self.monitor_op(current, self.best):

                        # Store the best
                        self.best = current
                        self.best_model_weights = self.model.get_weights()
                        self.best_model_epoch = self.epoch

                        if self.save_weights and self.file_path:
                            # Save weight on disk
                            logs = self.last_logs
                            if self.monitor not in logs:
                                logs[self.monitor] = current

                            file_path = self.file_path.format(epoch=self.epoch, **self.last_logs)
                            self.model.save_weights(file_path, overwrite=True)

    def set_external_metric_value(self, metric_label, metric_value):
        """Add external metric value

        Parameters
        ----------
        metric_label : str
            Metric label

        metric_value : numeric
            Metric value

        """

        if metric_label not in self.metric_data:
            self.metric_data[metric_label] = numpy.empty((self.epochs,))
            self.metric_data[metric_label][:] = numpy.nan
        self.metric_data[metric_label][self.epoch] = metric_value

    def get_best(self):
        """Return best model seen

        Returns
        -------
        dict
            Dictionary with keys 'weights', 'epoch', 'metric_value'
        """

        return {
            'epoch': self.best_model_epoch,
            'weights': self.best_model_weights,
            'metric_value': self.best,
        }

    def to_string(self, ui=None, indent=0):
        """Get information in a string

        Parameters
        ----------
        ui : FancyStringifier or FancyHTMLStringifier
            Stringifier class
            Default value FancyStringifier

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        if ui is None:
            ui = FancyStringifier()

        output = ''
        output += ui.class_name(self.__class__.__name__, indent=indent) + '\n'
        output += ui.data(field='Best model weights at epoch', value=self.best_model_epoch, indent=indent) + '\n'
        output += ui.data(field='Metric type', value=self.monitor, indent=indent+2) + '\n'
        output += ui.data(field='Metric value', value=self.best, indent=indent+2) + '\n'
        output += ui.line()

        return output

    def to_html(self, indent=0):
        """Get information in a HTML formatted string

        Parameters
        ----------
        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        str

        """

        return self.to_string(ui=FancyHTMLStringifier(), indent=indent)

    def log(self):
        """Print information about the best model into logging interface
        """

        lines = self.to_string(indent=2).split('\n')
        for line in lines:
            self.logger.info(line)

        self.logger.info('  ')

    def show(self, mode='auto', indent=0):
        """Print information about the best model

        If called inside Jupyter notebook HTML formatted version is shown.

        Parameters
        ----------
        mode : str
            Output type, possible values ['auto', 'print', 'html']. 'html' will work only in Jupyter notebook
            Default value 'auto'

        indent : int
            Amount of indent
            Default value 0

        Returns
        -------
        Nothing

        """

        if mode == 'auto':
            if is_jupyter():
                mode = 'html'
            else:
                mode = 'print'

        if mode not in ['html', 'print']:
            # Unknown mode given
            message = '{name}: Unknown mode [{mode}]'.format(name=self.__class__.__name__, mode=mode)
            self.logger.exception(message)
            raise ValueError(message)

        if mode == 'html':
            from IPython.core.display import display, HTML
            display(
                HTML(
                    self.to_html(indent=indent)
                )
            )

        elif mode == 'print':
            print(self.to_string(indent=indent))
