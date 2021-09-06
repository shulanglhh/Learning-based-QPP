from src.feature_extraction.database_loader import *
from src.feature_extraction.plan_features import *


def get_subplan(root):
    results = []
    if 'Actual Rows' in root and 'Actual Total Time' in root and 'Actual Rows' in root > 0:
        results.append((root, root['Actual Total Time'], root['Actual Rows']))
    if 'Plans' in root:
        for plan in root['Plans']:
            results += get_subplan(plan)
    return results

def get_plan(root):
    return root, root['Actual Total Time']

class PlanInSeq(object):
    def __init__(self, seq, time):
        self.seq = seq
        self.time = time

def get_alias2table(root, alias2table):
    if 'Relation Name' in root and 'Alias' in root:
        alias2table[root['Alias']] = root['Relation Name']
    if 'Plans' in root:
        for child in root['Plans']:
            get_alias2table(child, alias2table)

def feature_extractor(input_path, out_path):
    with open(out_path, 'w') as out:
        with open(input_path, 'r') as f:
            for index, plan in enumerate(f.readlines()):
                print (index)
                if plan != 'null\n':
                    plan = json.loads(plan)
                    plan = plan[0]['Plan']
                    if plan['Node Type'] == 'Aggregate':
                        plan = plan['Plans'][0]
                    alias2table = {}
                    get_alias2table(plan, alias2table)
                    subplan, time = get_plan(plan)
                    seq, _ = plan2seq(subplan, alias2table)
                    seqs = PlanInSeq(seq, time)
                    out.write(class2json(seqs)+'\n')

