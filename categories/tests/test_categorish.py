import unittest
from couchish import jsonutil

import categories


def create(item):
    """
    Dummy category creator.
    """
    return '10'


old_facet_dict = {
"category":[ 
  { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
  { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
  { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
  ]
}



class Test(unittest.TestCase):



    def test_find_deleted(self):

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"5", "path": "a.y", "data": { "_ref":"10", "label":"Y" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        expected = [ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          ]

        data = { "category":[] }
        root_path = 'a'
        actual = list(categories.find_deleted(before['category'], data['category'], root_path))
        assert actual == expected


    def test_find_additions(self):

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        
        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"10", "label":"Z" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        data = { "category":[ { "id":"3", "path":"x", "data": None, "new_category": {"is_new": True, "label": "Z"} }, ] }

        categories.create_added_reference(before['category'], 'f.a', data['category'], create)
        assert before == expected

    def test_pathchange(self):

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        
        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.N", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.N.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        categories.rename_path_segment(before['category'], 'a.x', 'a.N', [])
        assert before == expected

    def test_find_and_replace_pathchanges(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        
        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.N", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.N.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        data = { "category":[ { "id":"3", "path":"N", "data": {"_ref":"8", "label":"X"}, "new_category": {"is_new": False, "label": ""} }, ] }

        categories.find_and_replace_changed_paths(before['category'], data['category'], category)
        assert before == expected

    def test_applychanges(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        
        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.N", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.N.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        data = { "category":[ { "id":"3", "path":"N", "data": {"_ref":"8", "label":"X"}, "new_category": {"is_new": False, "label": ""} }, ] }


        categories.apply_changes(before['category'], data['category'], category, create)
        assert before == expected

    def test_lenient_ordering(self):
        # Do the right thing even if the children don't *immediately* follow
        # the parent.
        cats = [
            {'id': 1, 'path': 'a', 'data': {'_ref': 10}},
            {'id': 2, 'path': 'b', 'data': {'_ref': 11}},
            {'id': 3, 'path': 'b.a', 'data': {'_ref': 12}},
            {'id': 4, 'path': 'a.b', 'data': {'_ref': 13}},
        ]
        form_data = [
            {'id': 3, 'path': 'a', 'data': {'_ref': 12}, 'new_category': {'is_new': False}},
        ]
        after, changelog = categories.apply_changes(cats, form_data, 'b', None)
        print "*", cats
        print "*", after
        assert cats == after

    def test_apply_no_changes_to_root(self):
        cats = [
            {'id': 1, 'path': 'a', 'data': {'_ref': 10}},
            {'id': 2, 'path': 'b', 'data': {'_ref': 11}},
            {'id': 3, 'path': 'c', 'data': {'_ref': 12}},
        ]
        form_data = [
            {'id': 1, 'path': 'a', 'data': {'_ref': 10}, 'new_category': {'is_new': False}},
            {'id': 2, 'path': 'b', 'data': {'_ref': 11}, 'new_category': {'is_new': False}},
            {'id': 3, 'path': 'c', 'data': {'_ref': 12}, 'new_category': {'is_new': False}},
        ]
        after, changelog = categories.apply_changes(cats, form_data, '', None)
        print "*", cats
        print "*", after
        assert cats == after


class TestChanges(unittest.TestCase):


    def test_addition(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        
        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.N", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.N.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        data = { "category":[ { "id":"3", "path":"N", "data":  {"_ref":"8", "label":"X"}, "new_category": {"is_new": False, "label": ""} }, ] }


        categories.apply_changes(before['category'], data['category'], category, create)
        assert before == expected


    def test_deletion(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        
        expected = {'category': [ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          ]}

        data = { "category":[] }

        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']


    def test_pathchange(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.N", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.N.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        

        data = { "category":[{ "id":"3", "path":"N", "data":  {"_ref":"8", "label":"X"}, "new_category": {"is_new": False, "label": ""} },] }


        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_pathchange_rootcategory(self):

        category = None

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        expected = {
        "category":[ 
          { "id":"2", "path":"N", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "N.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"N.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        

        data = { "category":[{ "id":"2", "path":"N", "data": { "_ref":"7", "label":"A" }, "new_category": {"is_new": False, "label": ""} },] }


        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']
        
    def test_new_ref(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"10", "label":"FooBar" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        

        data = { "category":[{ "id":"3", "path":"x", "data": None, "new_category": {"is_new": True, "label": "FooBar"} },] }


        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']
        
    def test_new_ref2(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.N", "data": { "_ref":"10", "label":"FooBar" } },
          { "id":"4", "path":"a.N.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        

        data = { "category":[{ "id":"3", "path":"N", "data": None, "new_category": {"is_new": True, "label": "FooBar"} },] }


        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_reorder(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path": "a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"5", "path": "a.y", "data": { "_ref":"10", "label":"Y" } },
          { "id":"4", "path": "a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"5", "path": "a.N", "data": { "_ref":"10", "label":"Y" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path": "a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        

        data = { "category":[{ "id":"5", "path":"N", "data": { "_ref":"10", "label":"Y" }, "new_category": {"is_new": False, "label": None} },{ "id":"3", "path":"x", "data":  { "_ref":"8", "label":"X" }, "new_category": {"is_new": False, "label": None} }] }


        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_addnew(self):

        category = None

        before = {'category': [{'path': 'uk', 'data': {'_ref': '0bf538d1c8b272fddde23068b52f2463', 'label': 'UK'}, 'id': '0bf538d1c8b272fddde23068b52f2463'}, {'path': 'uk.england', 'data': {'_ref': '59a6432dd70cbbd967f410f3f0e0c649', 'label': 'England'}, 'id': '59a6432dd70cbbd967f410f3f0e0c649'}, {'path': 'uk.england.lakedistrict', 'data': {'_ref': '383a3106a48a5ff1cf8aeb5aa2a57444', 'label': 'Lake District'}, 'id': '383a3106a48a5ff1cf8aeb5aa2a57444'}] }

        expected = {
             'category': [
                 {'path': 'uk', 'data': {'_ref': '0bf538d1c8b272fddde23068b52f2463', 'label': 'UK'}, 'id': '0bf538d1c8b272fddde23068b52f2463'}, 
                 {'path': 'france', 'data': {'_ref': '10', 'label': 'France'}, 'id': '10'}, 
                 {'path': 'uk.england', 'data': {'_ref': '59a6432dd70cbbd967f410f3f0e0c649', 'label': 'England'}, 'id': '59a6432dd70cbbd967f410f3f0e0c649'}, 
                 {'path': 'uk.england.lakedistrict', 'data': {'_ref': '383a3106a48a5ff1cf8aeb5aa2a57444', 'label': 'Lake District'}, 'id': '383a3106a48a5ff1cf8aeb5aa2a57444'}
              ] }

        data = {'category':
        [{'data': {'_ref': u'0bf538d1c8b272fddde23068b52f2463', 'label': 'UK'},
          'id': u'0bf538d1c8b272fddde23068b52f2463',
          'new_category': {'is_new': False, 'label': None},
          'path': u'uk'},
         {'data': None,
          'id': None,
          'new_category': {'is_new': True, 'label': u'France'},
          'path': u'france'}]}

       
        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        expected['category'][1]['id'] = actual[1]['id']
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_addnew_nonroot(self):

        category = 'uk'

        before = {'category': [
            {'path': 'uk', 'data': {'_ref': '0bf538d1c8b272fddde23068b52f2463', 'label': 'UK'}, 'id': '0bf538d1c8b272fddde23068b52f2463'}, 
            {'path': 'uk.england', 'data': {'_ref': '59a6432dd70cbbd967f410f3f0e0c649', 'label': 'England'}, 'id': '59a6432dd70cbbd967f410f3f0e0c649'}, 
            {'path': 'uk.england.lakedistrict', 'data': {'_ref': '383a3106a48a5ff1cf8aeb5aa2a57444', 'label': 'Lake District'}, 'id': '383a3106a48a5ff1cf8aeb5aa2a57444'}] }

        expected = {
             'category': [
                 {'path': 'uk', 'data': {'_ref': '0bf538d1c8b272fddde23068b52f2463', 'label': 'UK'}, 'id': '0bf538d1c8b272fddde23068b52f2463'}, 
                 {'path': 'uk.england', 'data': {'_ref': '59a6432dd70cbbd967f410f3f0e0c649', 'label': 'England'}, 'id': '59a6432dd70cbbd967f410f3f0e0c649'}, 
                 {'path': 'uk.ireland', 'data': {'_ref': '10', 'label': 'Ireland'}, 'id': '10'}, 
                 {'path': 'uk.england.lakedistrict', 'data': {'_ref': '383a3106a48a5ff1cf8aeb5aa2a57444', 'label': 'Lake District'}, 'id': '383a3106a48a5ff1cf8aeb5aa2a57444'}
              ] }

        data = {'category':
        [{'data': {'_ref': u'59a6432dd70cbbd967f410f3f0e0c649', 'label': 'England'},
          'id': u'59a6432dd70cbbd967f410f3f0e0c649',
          'new_category': {'is_new': False, 'label': None},
          'path': u'england'},
         {'data': None,
          'id': None,
          'new_category': {'is_new': True, 'label': u'Ireland'},
          'path': u'ireland'}]}

       
        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        expected['category'][2]['id'] = actual[2]['id']
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_new_ref(self):

        category = 'a'

        before = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"8", "label":"X" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }

        expected = {
        "category":[ 
          { "id":"2", "path":"a", "data": { "_ref":"7", "label":"A" } },
          { "id":"3", "path": "a.x", "data": { "_ref":"9", "label":"P" } },
          { "id":"4", "path":"a.x.p", "data": { "_ref":"9", "label":"P" } },
          ]
        }
        

        data = { "category":[{ "id":"3", "path":"x", "data": { "_ref":"9", "label":"P" }, "new_category": {"is_new": False, "label": None} },] }


        actual, c = list(categories.apply_changes(before['category'], data['category'], category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']
