class Parameters():
    def __init__(self, condition_max_num, indexes_id, tables_id, table_vec, columns_id, column_datatype_vec, column_vec, physic_ops_id,
                 column_total_num,
                 table_total_num, type_total_number, index_total_num, physic_op_total_num, condition_op_dim,
                 compare_ops_id, bool_ops_id,
                 bool_ops_total_num, compare_ops_total_num, data, min_max_column, word_vectors, cost_label_min,
                 cost_label_max, plan_row_max, plan_row_min, plan_width_max,
                 plan_width_min, index2column):
        self.condition_max_num = condition_max_num
        self.indexes_id = indexes_id
        self.tables_id = tables_id
        self.table_vec = table_vec
        self.columns_id = columns_id
        self.column_datatype_vec = column_datatype_vec
        self.column_vec = column_vec
        self.physic_ops_id = physic_ops_id
        self.column_total_num = column_total_num
        self.table_total_num = table_total_num
        self.type_total_number = type_total_number
        self.index_total_num = index_total_num
        self.physic_op_total_num = physic_op_total_num
        self.condition_op_dim = condition_op_dim
        self.compare_ops_id = compare_ops_id
        self.bool_ops_id = bool_ops_id
        self.bool_ops_total_num = bool_ops_total_num
        self.compare_ops_total_num = compare_ops_total_num
        self.data = data
        self.min_max_column = min_max_column
        self.word_vectors = word_vectors
        self.cost_label_min = cost_label_min
        self.cost_label_max = cost_label_max
        self.plan_row_max = plan_row_max
        self.plan_row_min = plan_row_min
        self.plan_width_max = plan_width_max
        self.plan_width_min = plan_width_min
        self.index2column = index2column
