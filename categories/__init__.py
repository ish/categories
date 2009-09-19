import uuid


def sort_categories(facet_data):
    # XXX is this useful? how often would someone want to sort on path?
    # We could use sorted with a key arg, but that would mean splitting the
    # path on every comparison, so use the DSU pattern here.
    categories = [(i['path'].split('.'), i) for i in facet_data['category']]
    categories.sort()
    categories = [i[1] for i in categories]
    return categories


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
        if _is_descendent(old_path, c['path']):
            old = c['path']
            # XXX this is wrong.
            c['path'] = c['path'].replace(old_path, new_path, 1)
            changelog.append( (old, c['path']) )


def _is_descendent(root_path, path):
    root_path = _path(root_path)
    path = _path(path)
    return path[:len(root_path)] == root_path


def is_direct_child(root_path, path):
    root_path = _path(root_path)
    path = _path(path)
    return len(path) == len(root_path)+1 and \
            path[:len(root_path)] == root_path


def find_and_replace_changed_paths(old_facet_dict, data, root_path):
    # Map to id for fast lookup.
    oc_by_id = dict((i['id'], i) for i in old_facet_dict)
    changelog = []
    for d in data:
        if d['id'] in oc_by_id:
            old_path = oc_by_id[d['id']]['path']
            if root_path:
                new_path = '%s.%s'%('.'.join(root_path), d['path'])
            else:
                new_path = d['path']
            if new_path != old_path:
                rename_path_segment(old_facet_dict, old_path, new_path, changelog)
    return changelog


def find_deleted(old_facet_dict, data, root_path):
    root_path = _path(root_path)
    # Map to id for fast lookup.
    nc_by_id = dict((i['id'], i) for i in data)
    # List the deleted paths.
    deleted = [c['path'] for c in old_facet_dict
               if is_direct_child(root_path, c['path']) and c['id'] not in nc_by_id]
    deleted_ids = []
    # List the deleted ids (anything that is below a deleted path).
    for cat in old_facet_dict:
        for d in deleted:
            if _is_descendent(d, cat['path']):
                deleted_ids.append(cat['id'])
    # XXX can't this be part of the above loop?
    for cat in old_facet_dict:
        if cat['id'] not in deleted_ids:
            yield cat


def _path(path):
    """
    Split a path (whatever it is) into a list of segments.
    """
    if isinstance(path, list):
        return path
    if not path:
        return []
    return path.split('.')


def reorder_from_data(old_facet_dict, data, root_path):
    # Map to id for fast lookup.
    data_by_id = dict((i['id'], i) for i in old_facet_dict)
    cats = (cat for cat in old_facet_dict if not is_direct_child(root_path, cat['path']))
    # Yield any categories up to the parent of the new data.
    if root_path:
        for cat in cats:
            yield cat
            if _path(cat['path']) == root_path:
                break
    # Yield new category data.
    for d in data:
        if d['id'] in data_by_id:
            fd = data_by_id[d['id']]
            if fd['data']['_ref'] != d['data']:
                fd['data']=d['data']
            yield data_by_id[d['id']]
        else:
            if not root_path:
                path = d['path']
            else:
                path = '.'.join(root_path+d['path'].split('.'))
            yield {'id': uuid.uuid4().hex, 'data': d['data'], 'path': path}
    # Yield remaining categories.
    for cat in cats:
        yield cat
    return

        
def apply_changes(old_facet_dict, data, base_category, create_category):
    # XXX The 'data' structure seems to be very form-oriented. Shouldn't it be
    # in adminish really?
    if base_category:
        root_path = base_category.split('.')
    else:
        root_path = []
    create_added_reference(old_facet_dict, root_path , data, create_category)
    changelog = find_and_replace_changed_paths(old_facet_dict, data, root_path)
    categories = list(find_deleted(old_facet_dict, data, root_path))
    categories = list(reorder_from_data(categories, data, root_path))
    return categories, changelog

