# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import six
import string
import collections
import logging
from dcase_util.utils import setup_logging


class BibtexProcessor(object):
    """Simple Bibtex field processing class to prepare bibtex entries for the challenge and workshop submissions."""
    def __init__(self, year=None):
        """Constructor

        Parameters
        ----------
        year : int
            Year
        """

        self.year = year
        self.keys = {}
        self.num2alpha = dict(zip(range(1, 27), string.ascii_lowercase))
        self.num2alpha[0] = ''

    def key(self, authors, title=None, year=None):
        """Bibtex key generation. Keeps track internally seen keys to avoid identical keys.

        Parameters
        ----------
        authors : list of dict
            List of author dicts

        title : str
            Publication title

        year : int
            Publication year

        Returns
        -------
        str
            Bibtex key

        """

        if year is None:
            year = self.year

        key = authors[0]['lastname'].replace(' ', '_')+str(year)

        # Handle special characters
        key = key.replace(u'ö', 'oe')
        key = key.replace(u'ä', 'ae')

        if key not in self.keys:
            self.keys[key] = []

        if title not in self.keys[key]:
            self.keys[key].append(title)

        key += self.num2alpha[self.keys[key].index(title)]

        if six.PY2:
            return str(key.encode('ascii', 'ignore'))

        else:
            return str(key.encode('ascii', 'ignore'), 'utf-8')

    @staticmethod
    def authors(authors):
        """Author list in format [lastname1], [firstname1] and [lastname2], [firstname2].

        Parameters
        ----------
        authors : list of dict
            List of author dicts

        Returns
        -------
        str
            Authors string

        """

        bibtex_authors = []
        for author in authors:
            bibtex_authors.append(author['lastname']+', '+author['firstname'])

        return ' and '.join(bibtex_authors)

    def authors_fancy(self, authors, affiliation_list=None):
        """Author list with affiliation indexes.

        Parameters
        ----------
        authors : list of dict
            List of author dicts

        affiliation_list : list of affiliations, optional
            List of affiliation dicts

        Returns
        -------
        str
            Authors string

        """

        if affiliation_list is None:
            affiliation_list = self.affiliation_list(authors=authors)

        bibtex_authors_fancy = []
        for author in authors:
            name = author['firstname'] + ' ' + author['lastname']
            if len(affiliation_list) > 1:
                sup_text = {}

                if not isinstance(author['affiliation'], list):
                    aff_list = [author['affiliation']]
                else:
                    aff_list = author['affiliation']

                for aff in aff_list:
                    aff_label = self.affiliation_str(aff)
                    if aff_label in affiliation_list:
                        aff_index = affiliation_list.index(aff_label)+1

                    sup_text[aff_index] = str(aff_index)

                sup_text = '<sup>'+','.join(list(collections.OrderedDict(sorted(sup_text.items())).values()))+'</sup>'
                bibtex_authors_fancy.append(name+sup_text)
            else:
                bibtex_authors_fancy.append(name)

        if len(bibtex_authors_fancy) > 2:
            return ', '.join(bibtex_authors_fancy[0:-1]) + ' and ' + bibtex_authors_fancy[-1]
        elif len(bibtex_authors_fancy) == 2:
            return bibtex_authors_fancy[0] + ' and ' + bibtex_authors_fancy[1]
        else:
            return bibtex_authors_fancy[0]

    def affiliation_str(self, data):
        """Affiliation string.

        Parameters
        ----------
        data : list or dict
            Affiliation information dictionary

        Returns
        -------
        str
            Affiliation string

        """

        if isinstance(data, list):
            part_list = []
            for a in data:
                part_list.append(self.affiliation_str(a))
            return '; '.join(part_list)

        elif isinstance(data, dict):
            part_list = []
            if 'department' in data and data['department']:
                part_list.append(data['department'].strip())
            if 'institute' in data and data['institute']:
                part_list.append(data['institute'].strip())
            if 'location' in data and data['location']:
                part_list.append(data['location'].strip())
            return ', '.join(part_list)

    def affiliation_list(self, authors):
        """Collect all unique affiliations

        Parameters
        ----------
        authors : list of dict
            List of author dicts

        Returns
        -------
        list
            List of affiliation information dictionaries

        """

        affiliation_list = []
        for author in authors:
            if isinstance(author['affiliation'], list):
                for a in author['affiliation']:
                    label = self.affiliation_str(a)
                    if label not in affiliation_list:
                        affiliation_list.append(label)
            else:
                label = self.affiliation_str(author['affiliation'])
                if label not in affiliation_list:
                    affiliation_list.append(label)

        return affiliation_list

    def affiliation_list_fancy(self, authors, affiliation_list=None):
        """Affiliation string with indexes.

        Parameters
        ----------
        authors : list of dict
            List of author dicts

        affiliation_list : list, optional
            List of affiliation dicts

        Returns
        -------
        str
            String of affiliations with indexes.

        """

        if affiliation_list is None:
            affiliation_list = self.affiliation_list(authors=authors)

        if len(affiliation_list) > 1:
            bibtex_affiliations_fancy = []
            for index, aff in enumerate(affiliation_list):
                bibtex_affiliations_fancy.append('<sup>'+str(index+1)+'</sup>'+aff)
            return ', '.join(bibtex_affiliations_fancy)
        else:
            return affiliation_list[0]

    @staticmethod
    def submissions_fancy(submissions, css_class='label label-primary'):
        """HTML string with submission labels

        Parameters
        ----------
        submissions : list of str
            List of submission labels

        css_class : str
            CSS class for spans to wrap the submission labels
            Default value "label label-primary"

        Returns
        -------
        str
            String of submission labels

        """

        output = ''
        for sub in submissions:
            if css_class:
                output += '<span class="'+css_class+'">'+sub+'</span> '
            else:
                output += sub+', '
        return output

    def title(self, title):
        """Process publication title.

        Parameters
        ----------
        title : str
            Publication title

        Returns
        -------
        str
            Processed title

        """

        try:
            from titlecase import titlecase

        except ImportError:
            message = '{name}: Unable to import titlecase module. You can install it with `pip install titlecase`.'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise ImportError(message)

        def abbreviations(word, **kwargs):

            word_prefix = ''
            word_postfix = ''

            if word.startswith('('):
                word_prefix = word[0]
                word = word[1:]

            if word.endswith(':') or word.endswith(')'):
                word_postfix = word[-1]
                word = word[:-1]

            abbr_list = []
            abbr_list += ['GMM', 'DNN', 'CNN', 'RNN', 'CRNN', 'HMM', 'LSTM', 'MP', 'MLP', 'NMF']
            abbr_list += ['VGG', 'SVM', 'LTE', 'CQT', 'MFCC', 'GRU', 'I', 'AA']
            abbr_list += ['1D', '2D', '3D']
            abbr_list += ['DCASE', 'DCASE2017', 'DCASE2016', 'TUT', 'USTC', 'CP-JKU', 'IIT', 'SEIE-SCUT']
            abbr_list += ['B2C', 'IEEE', 'AASP', 'ADSC', 'BUET', 'CVSSP', 'CMU', 'COCAI', 'MTG', 'UPM',
                          'NCU', 'SINICA', 'CERTH', 'B2C', 'R-FCN']
            abbr_list += ['ASC', 'SED']

            if word.upper() in abbr_list:
                return word_prefix + '{'+word.upper()+'}' + word_postfix

            if word.upper().endswith('S'):
                if word[:-1].upper() in abbr_list:
                    return word_prefix + '{' + word[:-1].upper() + 's}' + word_postfix

            if '-' in word:
                word_list = []
                for w in word.split('-'):
                    if w.upper() in abbr_list:
                        word_list.append('{' + w.upper() + '}')
                    else:
                        word_list.append(titlecase(w))

                return '-'.join(word_list) + word_postfix

            mixed_list = ['FrameCNN', 'LightGBM']
            mixed_list_upper = []
            for i in mixed_list:
                mixed_list_upper.append(i.upper())
            if word.upper() in mixed_list_upper:
                return word_prefix + '{' + mixed_list[mixed_list_upper.index(word.upper())] + '}' + word_postfix

            # titlecase library implements AP-style (where all shorter than 4 letter words are not capitalized)
            # let's make exception for "with"
            lower_exceptions = ['with', 'WITH']
            if word in lower_exceptions:
                return word_prefix + word.lower() + word_postfix

        title = titlecase(title.lower(), callback=abbreviations)
        return title

    @staticmethod
    def abstract(abstract):
        """Process publication abstract.

        Parameters
        ----------
        abstract : str
            Publication abstract

        Returns
        -------
        str
            Processed abstract

        """

        pairs = [
            [u'\xe2\x80\x93', u'-'],
            [u'\xe2\x80\x94', u'-'],
            [u'\xe2\x80\x99', u"'"],
            [u'\xef\xac\x81', u'fi'],
            [u'\xe2\x80\x9d', u'"'],
            [u'\n', u''],
            [u'\%', u'%'],
            [u'$', u''],
        ]

        if six.PY2:
            abstract = abstract.decode('utf-8')

        for pair in pairs:
            abstract = abstract.replace(pair[0], pair[1])

        return abstract

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            setup_logging()

        return logger
