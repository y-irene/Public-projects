import numpy as np
from tensorflow.keras.layers import Input, LSTM, Dense, Concatenate, Reshape
from tensorflow.keras.models import Model, Sequential
import keras
import pandas as pd
from task1_metrics import mean_average_precision, mean_ndcg
import optuna


# # Read data
with open(f'T2_train_data_no_stopwords_100.npy', 'rb') as f:
    train_embeddings_data = np.load(f)
X_train = train_embeddings_data[:, :-1]
X_query_train = X_train[:, :100]
X_passage_train = X_train[:, 100:]
y_train = train_embeddings_data[:, -1]

with open(f'T2_validation_data_no_stopwords_100.npy', 'rb') as f:
    validation_embeddings_data = np.load(f)
X_validation = validation_embeddings_data[:, :-1]
X_query_val = X_validation[:, :100]
X_passage_val = X_validation[:, 100:]
y_val = validation_embeddings_data[:, -1]
val_data = pd.read_csv(f'validation_data.tsv', sep='\t')


# # Define model
def get_NN_model(layer_dims = None, activation='relu', learning_rate=1e-3):
    model = Sequential()
    model.add(Input(shape=(200,), name='query_passage_rep'))
    if layer_dims == None:
        layer_dims = [128, 64, 32, 16]
    for layer_dim in layer_dims:
        model.add(Dense(layer_dim, activation=activation))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=learning_rate), 
                  loss='binary_crossentropy')
    return model


# # Hyperparameter tuning

global hyperparam_search_space

def objective(trial):
    # Train trial model
    learning_rate = trial.suggest_categorical('learning_rate', hyperparam_search_space['learning_rate'])
    layer_dims = trial.suggest_categorical('layer_dims', hyperparam_search_space['layer_dims'])
    activation = trial.suggest_categorical('activation', hyperparam_search_space['activation'])
    model = get_NN_model(layer_dims=layer_dims, activation=activation, learning_rate=learning_rate)
    model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_validation, y_val), verbose=2)

    # Evaluate on validation data
    val_preds = model.predict(X_validation)
    val_data_eval = val_data[['qid', 'pid', 'relevancy']]
    val_data_eval['score'] = list(val_preds[:, -1])
    mndcg_score = mean_ndcg(val_data_eval)
    map_score = mean_average_precision(val_data_eval)
    return mndcg_score, map_score


hyperparam_search_space = {
    'learning_rate': [1e-3, 1e-2, 1e-1],
    'layer_dims': [[128, 64, 32, 16, 8], [128, 64, 32, 16], [128, 64, 32]],
    'activation': ['relu', 'tanh']
}
hyperparam_sampler = optuna.samplers.GridSampler(hyperparam_search_space)
study = optuna.create_study(study_name='NN hyperparameter tuning', directions=['maximize', 'maximize'], sampler=hyperparam_sampler)
study.optimize(objective, n_jobs=6, n_trials=18)


# ## Hyperparameter tuning results

# ### Get best parameters
trial_with_highest_ndcg = max(study.best_trials, key=lambda t: t.values[0])
trial_with_highest_map = max(study.best_trials, key=lambda t: t.values[1])

print('Best hyperparameters for the NN model with highest mNDCG:')
best_params_str = ["\t\'{key}\': {value}".format(key=key, value=value) 
                   for key, value in trial_with_highest_ndcg.params.items()]
print('\n'.join(best_params_str))
print(f'The scores for this configuration are: {trial_with_highest_ndcg.values[0]} mNDCG, {trial_with_highest_ndcg.values[1]} mAP\n')

print('Best hyperparameters for the NN model with highest mAP:')
best_params_str = ["\t\'{key}\': {value}".format(key=key, value=value) 
                   for key, value in trial_with_highest_map.params.items()]
print('\n'.join(best_params_str))
print(f'The scores for this configuration are: {trial_with_highest_map.values[0]} mNDCG, {trial_with_highest_map.values[1]} mAP\n')


# # Retrain model with best parameters
model = get_NN_model(**trial_with_highest_ndcg.params)
model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_validation, y_val), verbose=2)


# # Evaluate on validation
val_preds = model.predict(X_validation)
val_data_eval = val_data[['qid', 'pid', 'relevancy']]
val_data_eval['score'] = list(val_preds[:, -1])
mndcg = mean_ndcg(val_data_eval)
map = mean_average_precision(val_data_eval)
print('Performance on validation set of NN architecture:')
print(f'Mean NBCG: {mndcg}')
print(f'Mean Average Precision: {map}')


# # Save results on test set

# ## Predict on test set
test_data = pd.read_csv('candidate_passages_top1000.tsv', sep='\t', header=None, names=['qid', 'pid', 'query', 'passage'])
X_test = np.load('T2_test_data_no_stopwords_100.npy')
X_query_test = X_test[:, :100]
X_passage_test = X_test[:, 100:]
test_preds = model.predict(X_test)
test_data['score'] = list(test_preds[:, -1])
test_data.drop(columns=['query', 'passage'], inplace=True)


# ## Save results
test_data.sort_values(by=['qid', 'score'], ascending=[True, False], inplace=True)
test_data['rank'] = test_data.groupby('qid')['score'].rank(method='first', ascending=False).astype('int')
test_data['A2'] = 'A2'
test_data['alg'] = 'NN'
test_results_top_100 = test_data[test_data['rank'] <= 100]
col_order = ['qid', 'A2', 'pid', 'rank', 'score', 'alg']
test_results_top_100 = test_results_top_100[col_order]
test_results_top_100.to_csv('NN.txt', header=None, index=None, sep=' ')

