import numpy as np
import pandas as pd
from task1_metrics import mean_average_precision, mean_ndcg
import xgboost as xgb
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.base import BaseEstimator
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV


# # Auxiliary functions and classes

# Function that prepare data for training
def prepare_data_for_lambdamart(feature_file, 
                                original_file,
                                label_column, 
                                is_npy=True,
                                has_labels=True,
                                has_header=True):
    
    if is_npy:
        data_train = np.load(feature_file)
        df = pd.DataFrame(data=data_train)
    if has_labels:
        df.rename(columns={label_column: 'relevancy'}, inplace=True)
    if has_header:
        original_data = pd.read_csv(original_file, sep='\t')
    else:
        original_data = pd.read_csv(original_file, sep='\t', header=None, names=['qid', 'pid', 'query', 'passage'])
    df['qid'] = original_data['qid']
    df.sort_values(by='qid', inplace=True)
    if has_labels:
        y_train = df['relevancy']
        X_train = df.drop(columns=['relevancy'])
    else:
        y_train = None
        X_train = df
    return df, X_train, y_train


# XGBRanker wrapper class for hyperparameter tuning
class XGBRankerWrapper(BaseEstimator):
    def __init__(self, 
                 eta=0.3,
                 max_depth=6,
                 subsample=1,
                 n_estimators=50,
                 lambda_=1):
        self.eta = eta
        self.max_depth = max_depth
        self.subsample = subsample
        self.n_estimators = n_estimators
        self.lambda_ = lambda_
        self.model = None
    
    def fit(self, X, y=None):
        self.model = xgb.XGBRanker(tree_method="hist",
                                   objective="rank:ndcg", 
                                   lambdarank_pair_method="topk",
                                   lambdarank_num_pair_per_sample=1000,
                                   random_state=14,
                                   eta=self.eta,
                                   max_depth=self.max_depth,
                                   subsample=self.subsample,
                                   n_estimators=self.n_estimators,
                                   reg_lambda=self.lambda_)
        self.model.fit(X, y)
        return self.model
    
    def predict(self, X):
        scores = self.model.predict(X)
        qids = X['qid']
        return pd.DataFrame(data=list(zip(qids, scores)), columns=['qid', 'score'])


# Score functions that use the metrics defined in Task 1
def mean_ndcg_score(y_true, y_pred):
    df = y_pred.copy()
    df['relevancy'] = y_true.values
    score = mean_ndcg(df)
    return score


def mean_ap_score(y_true, y_pred):
    df = y_pred.copy()
    df['relevancy'] = y_true.values
    score = mean_average_precision(df)
    return score


# # Task 3

# ## Read training and validation data
df_train, X_train, y_train = prepare_data_for_lambdamart('T2_train_data_no_stopwords_100.npy',
                                                         'train_data_sample.tsv',
                                                         200)
df_val, X_val, y_val = prepare_data_for_lambdamart('T2_validation_data_no_stopwords_100.npy',
                                                   'validation_data.tsv',
                                                   200)

# ## Hyperparameter tuning
# Parameter grid
param_grid = {
    'eta': [0.01, 0.1, 0.3],
    'max_depth': [4, 6, 8],
    'subsample': [0.5, 0.75, 1],
    'n_estimators': [10, 50, 100],
    'lambda_': [0.1, 1, 10]
}
# Scorers
scoring = {
    'mndcg': make_scorer(mean_ndcg_score, greater_is_better=True),
    'map': make_scorer(mean_ap_score, greater_is_better=True)
}

# Stratified Group 3-fold 
groups = X_train['qid'].values
sgkf = StratifiedGroupKFold(n_splits=3)
cv = sgkf.split(X_train, y_train, groups=groups)
# Model
xgbranker = XGBRankerWrapper()

# Grid search cross-validation object
grid_search_cv = GridSearchCV(
    estimator=xgbranker,
    param_grid=param_grid,
    scoring=scoring,
    refit='mndcg',
    cv=cv,
    n_jobs=10,
    verbose=2
)

# Do grid search cross validation
grid_search_cv.fit(X_train, y_train)


# # Validate best model
best_estimator = grid_search_cv.best_estimator_
val_results = best_estimator.predict(X_val)
val_results['relevancy'] = y_val.values
mndcg = mean_ndcg(val_results)
map = mean_average_precision(val_results)
print(f'Performance on validation set of XGBRanker with best parameters {grid_search_cv.best_params_}:')
print(f'Mean NBCG: {mndcg}')
print(f'Mean Average Precision: {map}')


# Prepare test data
test_data = pd.read_csv('candidate_passages_top1000.tsv', sep='\t', header=None, names=['qid', 'pid', 'query', 'passage'])
test_features = np.load('T2_test_data_no_stopwords_100.npy')
test_features_df = pd.DataFrame(data=test_features)
test_features_df['qid'] = test_data['qid'].values
test_features_df['pid'] = test_data['pid'].values
test_features_df.sort_values(by='qid', inplace=True)
X_test = test_features_df.drop(columns=['pid'])


# Predict on test set
test_results = best_estimator.predict(X_test)
test_results['pid'] = test_features_df['pid'].values


# Save results
test_results.sort_values(by=['qid', 'score'], ascending=[True, False], inplace=True)
test_results['rank'] = test_results.groupby('qid')['score'].rank(method='first', ascending=False).astype('int')
test_results['A2'] = 'A2'
test_results['alg'] = 'LM'
test_results_top_100 = test_results[test_results['rank'] <= 100]
col_order = ['qid', 'A2', 'pid', 'rank', 'score', 'alg']
test_results_top_100 = test_results_top_100[col_order]
test_results_top_100.to_csv('LM.txt', header=None, index=None, sep=' ')
