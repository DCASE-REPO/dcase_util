""" Unit tests for Challenge tools """

import nose.tools
import dcase_util


def test_key():
    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
        },
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
        },
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
        },
    ]

    bib = dcase_util.tools.BibtexProcessor(year=2017)
    key1 = bib.key(authors=authors, title='Test title 1', year=2017)
    key2 = bib.key(authors=authors, title='Test title 2', year=2017)

    nose.tools.eq_(key1, 'Lastname2017')
    nose.tools.eq_(key2, 'Lastname2017a')

    key3 = bib.key(authors=authors, title='Test title 1')
    key4 = bib.key(authors=authors, title='Test title 2')

    nose.tools.eq_(key3, 'Lastname2017')
    nose.tools.eq_(key4, 'Lastname2017a')

    key5 = bib.key(authors=authors)
    nose.tools.eq_(key5, 'Lastname2017b')


def test_authors():
    authors1 = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
        }
    ]
    authors2 = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
        },
        {
            'lastname': 'Lastname2',
            'firstname': 'Firstname2',
        },
        {
            'lastname': 'Lastname3',
            'firstname': 'Firstname3',
        },
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(bib.authors(authors=authors1),
                   'Lastname, Firstname')
    nose.tools.eq_(bib.authors(authors=authors2),
                   'Lastname, Firstname and Lastname2, Firstname2 and Lastname3, Firstname3')


def test_authors_fancy():
    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
        {
            'lastname': 'Lastname2',
            'firstname': 'Firstname2',
            'affiliation': {
                'institute': 'Universitat Pompeu Fabra',
                'department': 'Music Technology Group',
                'location': 'Barcelona, Spain',
            }
        },
        {
            'lastname': 'Lastname3',
            'firstname': 'Firstname3',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.authors_fancy(authors=authors),
        'Firstname Lastname<sup>1</sup>, Firstname2 Lastname2<sup>2</sup> and Firstname3 Lastname3<sup>1</sup>'
    )

    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
        {
            'lastname': 'Lastname2',
            'firstname': 'Firstname2',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.authors_fancy(authors=authors),
        'Firstname Lastname and Firstname2 Lastname2'
    )

    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        }
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.authors_fancy(authors=authors),
        'Firstname Lastname'
    )

    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
            'affiliation': [
                {
                    'institute': 'Tampere University of Technology',
                    'department': 'Laboratory of Signal Processing',
                    'location': 'Tampere, Finland',
                },
                {
                    'institute': 'Universitat Pompeu Fabra',
                    'department': 'Music Technology Group',
                    'location': 'Barcelona, Spain',
                }
            ]

        },
        {
            'lastname': 'Lastname2',
            'firstname': 'Firstname2',
            'affiliation': {
                'institute': 'Universitat Pompeu Fabra',
                'department': 'Music Technology Group',
                'location': 'Barcelona, Spain',
            }
        },
        {
            'lastname': 'Lastname3',
            'firstname': 'Firstname3',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.authors_fancy(authors=authors),
        'Firstname Lastname<sup>1,2</sup>, Firstname2 Lastname2<sup>2</sup> and Firstname3 Lastname3<sup>1</sup>'
    )


def test_affiliation_str():
    affiliation = {
        'institute': 'Tampere University of Technology',
        'department': 'Laboratory of Signal Processing',
        'location': 'Tampere, Finland',
    }
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.affiliation_str(data=affiliation),
        'Laboratory of Signal Processing, Tampere University of Technology, Tampere, Finland'
    )

    affiliation = [
        {
            'institute': 'Tampere University of Technology',
            'department': 'Laboratory of Signal Processing',
            'location': 'Tampere, Finland',
        },
        {
            'institute': 'Universitat Pompeu Fabra',
            'department': 'Music Technology Group',
            'location': 'Barcelona, Spain',
        }
    ]

    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.affiliation_str(data=affiliation),
        'Laboratory of Signal Processing, Tampere University of Technology, Tampere, Finland; Music Technology Group, Universitat Pompeu Fabra, Barcelona, Spain'
    )


def test_affiliation_list():
    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
        {
            'lastname': 'Lastname2',
            'firstname': 'Firstname2',
            'affiliation': {
                'institute': 'Universitat Pompeu Fabra',
                'department': 'Music Technology Group',
                'location': 'Barcelona, Spain',
            }
        },
        {
            'lastname': 'Lastname3',
            'firstname': 'Firstname3',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.affiliation_list(authors=authors),
        ['Laboratory of Signal Processing, Tampere University of Technology, Tampere, Finland',
         'Music Technology Group, Universitat Pompeu Fabra, Barcelona, Spain']
    )


def test_affiliation_list_fancy():
    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
        {
            'lastname': 'Lastname2',
            'firstname': 'Firstname2',
            'affiliation': {
                'institute': 'Universitat Pompeu Fabra',
                'department': 'Music Technology Group',
                'location': 'Barcelona, Spain',
            }
        },
        {
            'lastname': 'Lastname3',
            'firstname': 'Firstname3',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.affiliation_list_fancy(authors=authors),
        '<sup>1</sup>Laboratory of Signal Processing, Tampere University of Technology, Tampere, Finland, <sup>2</sup>Music Technology Group, Universitat Pompeu Fabra, Barcelona, Spain'
    )

    authors = [
        {
            'lastname': 'Lastname',
            'firstname': 'Firstname',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
        {
            'lastname': 'Lastname2',
            'firstname': 'Firstname2',
            'affiliation': {
                'institute': 'Tampere University of Technology',
                'department': 'Laboratory of Signal Processing',
                'location': 'Tampere, Finland',
            }
        },
    ]
    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.affiliation_list_fancy(authors=authors),
        'Laboratory of Signal Processing, Tampere University of Technology, Tampere, Finland'
    )


def test_title():
    data = [
        {
            'input': 'Test and title',
            'target': 'Test and Title'
        },
        {
            'input': 'TeST aNd tItlE research',
            'target': 'Test and Title Research'
        },
        {
            'input': 'using gmm-based classifier',
            'target': 'Using {GMM}-Based Classifier'
        },
        {
            'input': 'Testing GMMs for classification',
            'target': 'Testing {GMMs} for Classification'
        },
        {
            'input': 'GMM: basic classifier',
            'target': '{GMM}: Basic Classifier'
        },
        {
           'input': 'Test case: a new study',
           'target': 'Test Case: A New Study'
        },
        {
            'input': 'new and brave approach to classification',
            'target': 'New and Brave Approach to Classification'
        },
        {
            'input': 'new and brave approach to classification with exception',
            'target': 'New and Brave Approach to Classification with Exception'
        },
    ]

    bib = dcase_util.tools.BibtexProcessor()

    for title in data:
        nose.tools.eq_(bib.title(title['input']), title['target'])


def test_abstract():
    abstract = 'This is test abstract.'

    bib = dcase_util.tools.BibtexProcessor()
    nose.tools.eq_(
        bib.abstract(abstract=abstract),
        u'This is test abstract.'
    )
