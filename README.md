# Learning Data Mode and Tree Structure Information for Query Performance Prediction

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

For Complete JOB: https://pan.baidu.com/s/15TaOAZqjlZxfwLiD3Si07w  password: ftuy

### Contact

If you have any issue, feel free to post on [Project](https://github.com/shulanglhh/Learning-based-QPP).

