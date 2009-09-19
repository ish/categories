import uuid


def sort_categories(facet_data):
    # XXX is this useful? how often would someone want to sort on path?
    # We could use sorted with a key arg, but that would mean splitting the
    # path on every comparison, so use the DSU pattern here.
    categories = [(i['path'].split('.'), i) for i in facet_data['category']]
    categories.sort()
    categories = [i[1] for i in categories]
    return categories


def split_categories(categories, root_path, data):
    # XXX parent comparison is incorrect.
    # Calculate root-related values.
    root_segments = root_path.split('.')
    root_depth = len(root_segments)
    facet_path = root_path.split('.')[0]
    # Setup some buckets to return items in.
    before = []
    after = []
    during = []
    current = before
    for c in categories:
        path = '%s.%s'%(facet_path, c['path'])
        segments = path.split('.')
        depth = len(segments)
        if depth == root_depth+1 and path.startswith(root_path):
            current = during
        if depth > root_depth+1:
            current = after
        current.append(c)
    return before, during, after


def find_added_category(facet_dict, root_path, data):
    return [i for i in data if i['id'] is None]


def create_added_reference(facet_dict, root_path, data, create_category):
    for n,item in enumerate(data):
        if item['new_category']['is_new'] is True:
            del item['new_category']['is_new']
            id = create_category(item['new_category'])
            item['new_category']['_ref'] = id
            I = dict(item['new_category'])
            if '_id' in I:
                del I['_id']
            data[n]['data'] = I
        else:
            I = item['data']
        for d in facet_dict:
            if d['id'] == item['id']:
                d['data'] = I
        

def rename_path_segment(facet_dict, old_path, new_path, changelog):
    for c in facet_dict:
        if c['path'].startswith(old_path):
            old = c['path']
            c['path'] = c['path'].replace(old_path, new_path, 1)
            changelog.append( (old, c['path']) )


def is_direct_child(root_path, c):
    facet_path = root_path.split('.')[0]
    path = '%s.%s'%(facet_path, c['path'])
    segments = path.split('.')
    depth = len(segments)
    root_segments = root_path.split('.')
    root_depth = len(root_segments)
    if depth == root_depth+1 and path.startswith(root_path):
        return True
    return False


def find_and_replace_changed_paths(old_facet_dict, data, base_category):
    # Map to id for fast lookup.
    oc_by_id = dict((i['id'], i) for i in old_facet_dict)
    changelog = []
    for d in data:
        if d['id'] in oc_by_id:
            old_path = oc_by_id[d['id']]['path']
            if base_category is not None:
                new_path = '%s.%s'%(base_category, d['path'])
            else:
                new_path = d['path']
            if new_path != old_path:
                rename_path_segment(old_facet_dict, old_path, new_path, changelog)
    return changelog


def find_deleted(old_facet_dict, data, root_path):
    # XXX parent comparison is incorrect.
    # Map to id for fast lookup.
    nc_by_id = dict((i['id'], i) for i in data)
    # List the deleted paths.
    deleted = [c['path'] for c in old_facet_dict
               if is_direct_child(root_path, c) and c['id'] not in nc_by_id]
    deleted_ids = []
    # List the deleted ids (anything that is below a deleted path).
    for cat in old_facet_dict:
        for d in deleted:
            if cat['path'].startswith(d):
                deleted_ids.append(cat['id'])
    # XXX can't this be part of the above loop?
    for cat in old_facet_dict:
        if cat['id'] not in deleted_ids:
            yield cat


def reorder_from_data(old_facet_dict, data, facet, base_category):
    root_path = _root_path(facet, base_category)
    # Map to id for fast lookup.
    data_by_id = dict((i['id'], i) for i in old_facet_dict)
    before, during, after = split_categories(old_facet_dict, root_path, data)
    for d in before:
        yield d
    for d in data:
        if d['id'] in data_by_id:
            fd = data_by_id[d['id']]
            if fd['data']['_ref'] != d['data']:
                fd['data']=d['data']
            yield data_by_id[d['id']]
        else:
            if base_category is None:
                path = d['path']
            else:
                path = '%s.%s'%(base_category,d['path'])
            yield {'id': uuid.uuid4().hex, 'data': d['data'], 'path': path}
    for d in after:
        yield d

        
def apply_changes(old_facet_dict, data, facet, base_category, create_category):
    root_path = _root_path(facet, base_category)
    create_added_reference(old_facet_dict, root_path , data, create_category)
    changelog = find_and_replace_changed_paths(old_facet_dict, data, base_category)
    categories = list(find_deleted(old_facet_dict, data, root_path))
    categories = list(reorder_from_data(categories, data, facet, base_category))
    return categories, changelog


def _root_path(facet, base_category):
    if base_category is not None:
        return '%s.%s'%(facet, base_category)
    else:
        return facet

