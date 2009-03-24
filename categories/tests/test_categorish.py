import unittest
from couchish import jsonutil

import categories

create = categories._create_category


facet_path = 'f'
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
        root_path = 'f.a'
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

        categories.rename_path_segment(before['category'], 'a.x', 'a.N')
        assert before == expected

    def test_find_and_replace_pathchanges(self):

        facet = 'f'
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

        data = { "category":[ { "id":"3", "path":"N", "data": "8", "new_category": {"is_new": False, "label": ""} }, ] }

        categories.find_and_replace_changed_paths(before['category'], data['category'], category)
        assert before == expected

    def test_applychanges(self):

        facet = 'f'
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

        data = { "category":[ { "id":"3", "path":"N", "data": "8", "new_category": {"is_new": False, "label": ""} }, ] }


        categories.apply_changes(before['category'], data['category'], facet, category, create)
        assert before == expected


class TestChanges(unittest.TestCase):


    def test_addition(self):

        facet = 'f'
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

        data = { "category":[ { "id":"3", "path":"N", "data": "8", "new_category": {"is_new": False, "label": ""} }, ] }


        categories.apply_changes(before['category'], data['category'], facet, category, create)
        assert before == expected


    def test_deletion(self):

        facet = 'f'
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

        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']


    def test_pathchange(self):

        facet = 'f'
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
        

        data = { "category":[{ "id":"3", "path":"N", "data": "8", "new_category": {"is_new": False, "label": ""} },] }


        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_pathchange_rootcategory(self):

        facet = 'f'
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
        

        data = { "category":[{ "id":"2", "path":"N", "data": "7", "new_category": {"is_new": False, "label": ""} },] }


        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']
        
    def test_new_ref(self):

        facet = 'f'
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


        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']
        
    def test_new_ref2(self):

        facet = 'f'
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


        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_reorder(self):

        facet = 'f'
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
        

        data = { "category":[{ "id":"5", "path":"N", "data": "10", "new_category": {"is_new": False, "label": None} },{ "id":"3", "path":"x", "data": "8", "new_category": {"is_new": False, "label": None} }] }


        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_addnew(self):

        facet = 'f'
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

       
        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        expected['category'][1]['id'] = actual[1]['id']
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']

    def test_new_ref(self):

        facet = 'f'
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
        

        data = { "category":[{ "id":"3", "path":"x", "data": "9", "new_category": {"is_new": False, "label": None} },] }


        actual = list(categories.apply_changes(before['category'], data['category'], facet, category, create))
        print 'ACTUAL'
        print actual
        print 'EXPECTED'
        print expected['category']
        assert actual == expected['category']
