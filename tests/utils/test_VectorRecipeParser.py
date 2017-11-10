""" Unit tests for VectorRecipeParser """

import nose.tools
from dcase_util.utils import VectorRecipeParser


def test_parse():
    parser = VectorRecipeParser()

    # Test #1
    test_recipe = 'mel'

    parsed_recipe = parser.parse(recipe=test_recipe)

    # correct amount of items
    nose.tools.eq_(len(parsed_recipe), 1)

    # method is correct
    nose.tools.eq_(parsed_recipe[0]['label'], 'mel')

    # Test #2
    test_recipe = 'mel=0;mfcc=1'
    parsed_recipe = parser.parse(recipe=test_recipe)

    # correct amount of items
    nose.tools.eq_(len(parsed_recipe), 2)

    # methods are correct
    nose.tools.eq_(parsed_recipe[0]['label'], 'mel')
    nose.tools.eq_(parsed_recipe[1]['label'], 'mfcc')

    # vector-index is correct / channel
    nose.tools.eq_(parsed_recipe[0]['vector-index']['stream'], 0)
    nose.tools.eq_(parsed_recipe[1]['vector-index']['stream'], 1)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['full'], True)
    nose.tools.eq_(parsed_recipe[1]['vector-index']['full'], True)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['selection'], False)
    nose.tools.eq_(parsed_recipe[1]['vector-index']['selection'], False)

    # Test #3
    test_recipe = 'mel=1-20'
    parsed_recipe = parser.parse(recipe=test_recipe)

    # correct amount of items
    nose.tools.eq_(len(parsed_recipe), 1)

    # method is correct
    nose.tools.eq_(parsed_recipe[0]['label'], 'mel')

    # vector-index is correct / channel
    nose.tools.eq_(parsed_recipe[0]['vector-index']['stream'], 0)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['full'], False)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['selection'], False)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['start'], 1)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['stop'], 21)

    # Test #4
    test_recipe = 'mel=1,2,4,5'
    parsed_recipe = parser.parse(recipe=test_recipe)

    # correct amount of items
    nose.tools.eq_(len(parsed_recipe), 1)

    # extractor is correct
    nose.tools.eq_(parsed_recipe[0]['label'], 'mel')

    # vector-index is correct / channel
    nose.tools.eq_(parsed_recipe[0]['vector-index']['stream'], 0)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['full'], False)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['selection'], True)
    nose.tools.assert_list_equal(parsed_recipe[0]['vector-index']['vector'], [1, 2, 4, 5])

    # Test #5
    test_recipe = 'mel=1:1-20'
    parsed_recipe = parser.parse(recipe=test_recipe)

    # correct amount of items
    nose.tools.eq_(len(parsed_recipe), 1)

    # method is correct
    nose.tools.eq_(parsed_recipe[0]['label'], 'mel')

    # vector-index is correct / channel
    nose.tools.eq_(parsed_recipe[0]['vector-index']['stream'], 1)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['full'], False)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['selection'], False)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['start'], 1)
    nose.tools.eq_(parsed_recipe[0]['vector-index']['stop'], 21)
