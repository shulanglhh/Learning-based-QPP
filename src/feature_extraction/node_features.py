import json

from src.feature_extraction.predicate_features import *
from src.feature_extraction.node_operations import *


def class2json(instance):
    if instance is None:
        return json.dumps({})
    else:
        return json.dumps(todict(instance))


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


def change_alias2table(column, alias2table):
    relation_name = column.split('.')[0]
    column_name = column.split('.')[1]
    if relation_name in alias2table:
        return alias2table[relation_name] + '.' + column_name
    else:
        return column


def extract_info_from_node(node, alias2table):
    relation_name, index_name , plan_rows, plan_width = None, None, None, None
    if 'Relation Name' in node:
        relation_name = node['Relation Name']
    if 'Index Name' in node:
        index_name = node['Index Name']
    if 'Plan Rows' in node:
        plan_rows = node['Plan Rows']
    if 'Plan Width' in node:
        plan_width = node['Plan Width']
    if node['Node Type'] == 'Materialize':
        return Materialize(plan_rows, plan_width), None
    elif node['Node Type'] == 'Hash':
        return Hash(plan_rows, plan_width), None
    elif node['Node Type'] == 'Sort':
        keys = [change_alias2table(key, alias2table) for key in node['Sort Key']]
        return Sort(keys, plan_rows, plan_width), None
    elif node['Node Type'] == 'BitmapAnd':
        return BitmapCombine('BitmapAnd', plan_rows, plan_width), None
    elif node['Node Type'] == 'BitmapOr':
        return BitmapCombine('BitmapOr', plan_rows, plan_width), None
    elif node['Node Type'] == 'Result':
        return Result(plan_rows, plan_width), None
    elif node['Node Type'] == 'Hash Join':
        return Join('Hash Join', pre2seq(node["Hash Cond"], alias2table, relation_name, index_name), plan_rows, plan_width), None
    elif node['Node Type'] == 'Merge Join':
        return Join('Merge Join', pre2seq(node["Merge Cond"], alias2table, relation_name, index_name), plan_rows, plan_width), None
    elif node['Node Type'] == 'Nested Loop':
        if 'Join Filter' in node:
            condition = pre2seq(node['Join Filter'], alias2table, relation_name, index_name)
        else:
            condition = []
        return Join('Nested Loop', condition, plan_rows, plan_width), None
    elif node['Node Type'] == 'Aggregate':
        if 'Group Key' in node:
            keys = [change_alias2table(key, alias2table) for key in node['Group Key']]
        else:
            keys = []
        return Aggregate(node['Strategy'], keys, plan_rows, plan_width), None
    elif node['Node Type'] == 'Seq Scan':
        if 'Filter' in node:
            condition_seq_filter = pre2seq(node['Filter'], alias2table, relation_name, index_name)
        else:
            condition_seq_filter = []
        condition_seq_index, relation_name, index_name = [], node["Relation Name"], None
        return Scan('Seq Scan', condition_seq_filter, condition_seq_index, relation_name, index_name, plan_rows, plan_width), None
    elif node['Node Type'] == 'Bitmap Heap Scan':
        if 'Filter' in node:
            condition_seq_filter = pre2seq(node['Filter'], alias2table, relation_name, index_name)
        else:
            condition_seq_filter = []
        condition_seq_index, relation_name, index_name = [], node["Relation Name"], None
        return Scan('Bitmap Heap Scan', condition_seq_filter, condition_seq_index, relation_name, index_name, plan_rows, plan_width), None
    elif node['Node Type'] == 'Index Scan':
        if 'Filter' in node:
            condition_seq_filter = pre2seq(node['Filter'], alias2table, relation_name, index_name)
        else:
            condition_seq_filter = []
        if 'Index Cond' in node:
            condition_seq_index = pre2seq(node['Index Cond'], alias2table, relation_name, index_name)
        else:
            condition_seq_index = []
        relation_name, index_name = node["Relation Name"], node['Index Name']
        if len(condition_seq_index) == 1 and re.match(r'[a-zA-Z]+', condition_seq_index[0].right_value) is not None:
            return Scan('Index Scan', condition_seq_filter, condition_seq_index, relation_name,
                        index_name, plan_rows, plan_width), condition_seq_index
        else:
            return Scan('Index Scan', condition_seq_filter, condition_seq_index, relation_name, index_name, plan_rows, plan_width), None
    elif node['Node Type'] == 'Bitmap Index Scan':
        if 'Index Cond' in node:
            condition_seq_index = pre2seq(node['Index Cond'], alias2table, relation_name, index_name)
        else:
            condition_seq_index = []
        condition_seq_filter, relation_name, index_name = [], None, node['Index Name']
        if len(condition_seq_index) == 1 and re.match(r'[a-zA-Z]+', condition_seq_index[0].right_value) is not None:
            return Scan('Bitmap Index Scan', condition_seq_filter, condition_seq_index, relation_name,
                        index_name, plan_rows, plan_width), condition_seq_index
        else:
            return Scan('Bitmap Index Scan', condition_seq_filter, condition_seq_index, relation_name, index_name, plan_rows, plan_width), None
    elif node['Node Type'] == 'Index Only Scan':
        if 'Index Cond' in node:
            condition_seq_index = pre2seq(node['Index Cond'], alias2table, relation_name, index_name)
        else:
            condition_seq_index = []
        condition_seq_filter, relation_name, index_name = [], None, node['Index Name']
        if len(condition_seq_index) == 1 and re.match(r'[a-zA-Z]+', condition_seq_index[0].right_value) is not None:
            return Scan('Index Only Scan', condition_seq_filter, condition_seq_index, relation_name,
                        index_name, plan_rows, plan_width), condition_seq_index
        else:
            return Scan('Index Only Scan', condition_seq_filter, condition_seq_index, relation_name, index_name, plan_rows, plan_width), None
    else:
        raise Exception('Unsupported Node Type: ' + node['Node Type'])
        return None, None
