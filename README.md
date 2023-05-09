# MSP: Learned Query Performance Prediction Using MetaInfo and Structure of Plans
Source code of Feature Encoding and Model Training for QPP based on PostgreSQL Execution Plans.
Query performance prediction(QPP) without actual execution could be used by other database tasks, including admission control decision, query scheduling decision, query monitoring, and resource management.

### Unitest
```bash
export PYTHONPATH=code/
python -m unittest code.test.test_feature_extraction.TestFeatureExtraction
python -m unittest code.test.test_feature_encoding.TestFeatureEncoding
python -m unittest code.test.test_training.TestTraining
```

### Test Data
For Nemerical workload: https://github.com/andreaskipf/learnedcardinalities

For Complete JOB: https://pan.baidu.com/s/1n9mf9IwPgSduJORDslSTFg password: 3sjs 

### Contact

If you have any issue, feel free to post on [Project](https://github.com/shulanglhh/Learning-based-QPP).

