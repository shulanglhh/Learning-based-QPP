class Materialize(object):
    def __init__(self, plan_rows, plan_width):
        self.node_type = 'Materialize'
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return 'Materialize'


class Aggregate(object):
    def __init__(self, strategy, keys, plan_rows, plan_width):
        self.node_type = 'Aggregate'
        self.strategy = strategy
        self.group_keys = keys
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return 'Aggregate ON: ' + ','.join(self.group_keys)


class Sort(object):
    def __init__(self, sort_keys, plan_rows, plan_width):
        self.sort_keys = sort_keys
        self.node_type = 'Sort'
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return 'Sort by: ' + ','.join(self.sort_keys)


class Hash(object):
    def __init__(self, plan_rows, plan_width):
        self.node_type = 'Hash'
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return 'Hash'


class Join(object):
    def __init__(self, node_type, condition_seq, plan_rows, plan_width):
        self.node_type = node_type
        self.condition = condition_seq
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return self.node_type + ' ON ' + ','.join([str(i) for i in self.condition])


class Scan(object):
    def __init__(self, node_type, condition_seq_filter, condition_seq_index, relation_name, index_name, plan_rows, plan_width):
        self.node_type = node_type
        self.condition_filter = condition_seq_filter
        self.condition_index = condition_seq_index
        self.relation_name = relation_name
        self.index_name = index_name
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return self.node_type + ' ON ' + ','.join([str(i) for i in self.condition_filter]) + '; ' + ','.join(
            [str(i) for i in self.condition_index])


class BitmapCombine(object):
    def __init__(self, operator, plan_rows, plan_width):
        self.node_type = operator
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return self.node_type


class Result(object):
    def __init__(self, plan_rows, plan_width):
        self.node_type = 'Result'
        self.plan_rows = plan_rows
        self.plan_width = plan_width

    def __str__(self):
        return 'Result'
