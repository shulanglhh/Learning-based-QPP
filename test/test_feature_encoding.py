import unittest


from src.feature_extraction.database_loader import *
from src.training.train_and_test import *
from src.internal_parameters import *

class TestFeatureEncoding(unittest.TestCase):
    def test(self):
        dataset = load_dataset('/home/lhh/Learning-based-QPP/test_files_open_source/imdb_data_csv')
        column2pos, indexes_id, tables_id, table_vec, columns_id, column_datatype_vec, column_vec, physic_ops_id, compare_ops_id, bool_ops_id, table_names, index2column = prepare_dataset(dataset)
        print ('data prepared')
        word_vectors = load_dictionary('/home/lhh/Learning-based-QPP/test_files_open_source/wordvectors_updated.kv')
        print ('word_vectors loaded')
        min_max_column = load_numeric_min_max('/home/lhh/Learning-based-QPP/test_files_open_source/min_max_vals.json')
        print ('min_max loaded')

        index_total_num = len(indexes_id)
        table_total_num = len(tables_id)
        type_total_number = 6
        column_total_num = len(columns_id)
        physic_op_total_num = len(physic_ops_id)
        compare_ops_total_num = len(compare_ops_id)
        bool_ops_total_num = len(bool_ops_id)
        condition_op_dim = bool_ops_total_num + compare_ops_total_num+column_total_num+1000
        plan_node_max_num, condition_max_num, cost_label_min, cost_label_max, plan_row_max, plan_row_min, plan_width_max, plan_width_min = obtain_upper_bound_query_size('/home/lhh/Learning-based-QPP/test_files_open_source/plans_seq.json')
        print ('query upper size prepared')

        parameters = Parameters(condition_max_num, indexes_id, tables_id, table_vec, columns_id, column_datatype_vec, column_vec, physic_ops_id, column_total_num,
                                table_total_num, type_total_number, index_total_num, physic_op_total_num, condition_op_dim, compare_ops_id, bool_ops_id,
                                bool_ops_total_num, compare_ops_total_num, dataset, min_max_column, word_vectors, cost_label_min,
                                cost_label_max, plan_row_max, plan_row_min, plan_width_max, plan_width_min,index2column)

        encode_test_plan_seq_save('/home/lhh/Learning-based-QPP/test_files_open_source/plans_seq.json', parameters, batch_size=8, directory='/home/lhh/Learning-based-QPP/test_files_open_source/job')
if __name__ == '__main__':
    unittest.main()