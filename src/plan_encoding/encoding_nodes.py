from src.plan_encoding.encoding_predicates import *


def encode_sample(sample):
    return np.array([int(i) for i in sample])


def bitand(sample1, sample2):
    return np.minimum(sample1, sample2)


def encode_node_job(node, parameters):


    operator_vec = np.array([0 for _ in range(parameters.physic_op_total_num)])
    extra_info_vec = np.array([0 for _ in range(parameters.type_total_number)])
    extra_info_vec = np.insert(extra_info_vec, -1, values=np.array([0]), axis=0)
    cardinality_vec = np.array([0 for _ in range(2)])
    condition1_vec = np.array(
        [[0 for _ in range(parameters.condition_op_dim)] for _ in range(parameters.condition_max_num)])
    condition2_vec = np.array(
        [[0 for _ in range(parameters.condition_op_dim)] for _ in range(parameters.condition_max_num)])

    if node != None:
        operator = node['node_type']
        plan_row = node['plan_rows']
        plan_width = node['plan_width']
        cardinality_vec[0] = (plan_row - parameters.plan_row_min) / (parameters.plan_row_max - parameters.plan_row_min)
        cardinality_vec[1] = (plan_width - parameters.plan_width_max) / (
                parameters.plan_width_max - parameters.plan_width_min)
        operator_idx = parameters.physic_ops_id[operator]
        operator_vec[operator_idx - 1] = 1
        if operator == 'Materialize' or operator == 'BitmapAnd' or operator == 'Result':
            pass
        elif operator == 'Sort':
            for key in node['sort_keys']:
                extra_info_vec = np.insert(parameters.column_vec[key], -1, values=np.array([0]), axis=0)
                # extra_info_inx = parameters.columns_id[key]
                # extra_info_vec[extra_info_inx - 1] = 1
        elif operator == 'Hash Join' or operator == 'Merge Join' or operator == 'Nested Loop':
            condition1_vec = encode_condition(node['condition'], None, None, parameters)
        elif operator == 'Aggregate':
            for key in node['group_keys']:
                extra_info_vec = np.insert(parameters.column_vec[key], -1, values=np.array([0]), axis=0)
                # extra_info_inx = parameters.columns_id[key]
                # extra_info_vec[extra_info_inx - 1] = 1
        elif operator == 'Seq Scan' or operator == 'Bitmap Heap Scan' or operator == 'Index Scan' \
                or operator == 'Bitmap Index Scan' or operator == 'Index Only Scan':
            relation_name = node['relation_name']
            index_name = node['index_name']
            if relation_name is not None:
                extra_info_vec = np.insert(parameters.table_vec[relation_name], -1, values=np.array([0]), axis=0)
            else:
                extra_info_vec = np.insert(parameters.column_datatype_vec[parameters.index2column[index_name]], -1,
                                           values=np.array([1]), axis=0)
            condition1_vec = encode_condition(node['condition_filter'], relation_name, index_name, parameters)
            condition2_vec = encode_condition(node['condition_index'], relation_name, index_name, parameters)

    return operator_vec, extra_info_vec, cardinality_vec, condition1_vec, condition2_vec
