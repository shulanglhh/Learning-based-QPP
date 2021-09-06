import psycopg2


def extract_datatype():
    conn = psycopg2.connect(database="imdb", user="postgres", password="123456", host="127.0.0.1",
                            port="5432")
    table = ['aka_name', 'aka_title', 'cast_info', 'char_name', 'company_name', 'company_type', 'comp_cast_type',
             'complete_cast', 'info_type', 'keyword', 'kind_type', 'link_type', 'movie_companies', 'movie_info',
             'movie_info_idx', 'movie_keyword', 'movie_link', 'name', 'person_info', 'role_type', 'title']

    # 获取表中字段的数据类型
    sql = 'select * from information_schema.columns where table_name = %s'

    datatype = {}

    for table_name in table:
        datatype[table_name] = {}
        value = (table_name,)
        cur = conn.cursor()
        cur.execute(sql, value)
        rows = cur.fetchall()
        for row in rows:
            datatype[table_name][row[3]] = {}
            datatype[table_name][row[3]]['ORDINAL_POSITION'] = row[4]
            datatype[table_name][row[3]]['DATA_TYPE'] = row[7]
            datatype[table_name][row[3]]['MAX_LENGTH'] = row[8]
            datatype[table_name][row[3]]['NUMERIC_PRECISION'] = row[10]
            datatype[table_name][row[3]]['UDT_NAME'] = row[27]

    conn.close()

    return datatype
