import numpy as np

from src.feature_extraction.extract_datatype import extract_datatype


def encoding_datatype():
    datatype_id = {'smallint': 1, 'integer': 1, 'bigint': 1, 'decimal': 2, 'numeric': 2, 'real': 2,
                   'double precision': 2,
                   'serial': 1, 'bigserial': 1, 'character varying': 3, 'varchar': 3, 'character': 4, 'char': 4,
                   'text': 3, 'timestamp': 5, 'timestamp with time zone': 5, 'interval': 5, 'date': 5, 'time': 5,
                   'time with time zone': 6, 'boolean': 6}

    type_total_number = 6
    table_datatype_vec = {}
    datatype_matrix = {}
    column_datatype_vec = {}
    datatype = extract_datatype()
    for key in datatype:
        datatype_matrix[key] = np.zeros(shape=[type_total_number], dtype=int)
        column_type = datatype[key]
        for column_key, column_value in column_type.items():
            column_datatype_vec[column_key] = np.array([0 for _ in range(type_total_number)])
            datatype_inx = datatype_id[column_value['DATA_TYPE']]
            column_datatype_vec[column_key][datatype_inx - 1] = 1
            datatype_matrix[key] = np.vstack((datatype_matrix[key], column_datatype_vec[column_key]))
        datatype_matrix[key] = np.vstack((datatype_matrix[key][1:-1, :], datatype_matrix[key][-1, :]))
        table_datatype_vec[key] = np.sum(datatype_matrix[key], axis=0)

    return table_datatype_vec, datatype_matrix, column_datatype_vec


if __name__ == '__main__':
    table_datatype_vec, datatype_matrix, column_datatype_vec = encoding_datatype()
    print(table_datatype_vec)
    print(datatype_matrix)
    print(column_datatype_vec['info_type_id'])
