import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
from task1_metrics import mean_average_precision, mean_ndcg


def plot_multiple_train_loss(train_loss, title, y_label, plot_labels, file_name=None):
    _, (ax1) = plt.subplots(1, 1, figsize=(10, 7))
    for i in range(len(train_loss)):
        plt.plot(range(1, len(train_loss[i]) + 1), train_loss[i], label=plot_labels[i])
    plt.xlabel("epoch")
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    if file_name:
        plt.savefig(f'{file_name}.svg', bbox_inches='tight')
        plt.savefig(f'{file_name}.png', bbox_inches='tight')
    


def save_output_file(candidate_passages, scores, alg):
    candidate_passages.rename(columns={0: 'qid', 1: 'pid', 2: 'query', 3: 'passage'}, inplace=True)
    candidate_passages['score'] = scores
    candidate_passages.sort_values(by=['qid', 'score'], ascending=[True, False], inplace=True)
    candidate_passages.drop(columns=['query', 'passage'], inplace=True)
    candidate_passages['A2'] = 'A2'
    candidate_passages['alg'] = alg
    candidate_passages['rank'] = candidate_passages.groupby('qid')['score'].rank(method='first', ascending=False).astype('int')
    candidate_passages = candidate_passages[candidate_passages['rank'] <= 100]
    col_order = ['qid', 'A2', 'pid', 'rank', 'score', 'alg']
    candidate_passages = candidate_passages[col_order]
    candidate_passages.to_csv(f'{alg}.txt', header=None, index=None, sep=' ')


class LogisticRegression:
    def __init__(self, lr=0.01, n_iters=1000):
        self.lr = lr
        self.n_iters = n_iters
        self.w = None
        self.b = None
    
    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))
    
    def ce_loss(self, y, z):
        loss = y * np.log(z) + (1 - y) * np.log(1 - z)
        loss = -np.mean(loss)
        return loss
    
    def get_gradients(self, X, y, z):
        n_samples, n_features = X.shape
        diff = y - z
        gradient_b = -np.mean(diff)
        gradient_w = - 1 / n_samples * (X.T @ diff)
        return gradient_w, gradient_b
    
    def fit(self, X, y):
        # Get shape of input
        n_samples, n_features = X.shape
        # Initialise weights and bias
        self.w = np.zeros(n_features)
        self.b = 0
        
        losses = []
        with tqdm(range(self.n_iters)) as titer:
            for i in titer:
                titer.set_description(f'Iteration {i}')
                # Compute predictions
                z = self.sigmoid(self.w @ X.T + self.b)
                # Compute and store loss
                loss = self.ce_loss(y, z)
                losses.append(loss)
                # Compute gradients
                gradient_w, gradient_b = self.get_gradients(X, y, z)
                # Update weights
                self.w = self.w - self.lr * gradient_w
                self.b = self.b - self.lr * gradient_b
                titer.set_postfix(loss=loss)
        
        self.fit = True
        return losses
    
    def predict(self, X):
        if not self.fit:
            raise Exception('Logistic Regression model is not fitted!')
        return self.sigmoid(self.w @ X.T + self.b)


if __name__ == '__main__':
    train_data_path = 'T2_train_data_no_stopwords_100.npy'
    validation_data_path = 'T2_validation_data_no_stopwords_100.npy'
    test_data_path = 'T2_test_data_no_stopwords_100.npy'
    
    # Read training data
    with open(train_data_path, 'rb') as f:
        train_embeddings_data = np.load(f)
    X_train = train_embeddings_data[:, :-1]
    y_train = train_embeddings_data[:, -1]
    
    # Define values for learning rate
    n_iters = 2000
    lrs = [0.1, 0.01, 0.001]
    all_losses = {}
    all_models = {}

    # Train Logistic Regression models
    for lr in lrs:
        print(f'Training Logistic Regression model with lr = {lr}...')
        log_reg = LogisticRegression(n_iters=n_iters, lr=lr)
        losses = log_reg.fit(X_train, y_train)
        all_losses[lr] = losses
        all_models[lr] = log_reg
        print('Done!\n')
    
    # Plot losses for different learning rates
    plot_labels = [f'lr = {lr}' for lr in all_losses]
    train_losses = [all_losses[lr] for lr in all_losses]
    plot_multiple_train_loss(train_losses,
                            'Train losses for the Logistic Regression model for different learning rate values',
                            'learning rate',
                            plot_labels,
                            'test')
    
    print(f'Evaluating the Logistic Regression model with lr = {lrs[0]} on the validation set..')
    # Read validation data
    validation_data = pd.read_csv('validation_data.tsv', sep='\t')
    with open(validation_data_path, 'rb') as f:
        validation_embeddings_data = np.load(f)
    X_val = validation_embeddings_data[:, :-1]
    y_val = validation_embeddings_data[:, -1]

    # Evaluate model on validation set
    model = all_models[lrs[0]]
    y_val_pred = model.predict(X_val)
    log_reg_val_data = validation_data[['qid', 'pid', 'relevancy']].astype({'relevancy': 'int32'})
    log_reg_val_data['score'] = y_val_pred
    map = mean_average_precision(log_reg_val_data)
    mndcg = mean_ndcg(log_reg_val_data)

    # Print performance
    print('Performance of the Logistic Regression model on the validation set')
    print(f'Mean AP: {map}')
    print(f'Mean NDCG: {mndcg}\n')

    # Predict on test data
    print('Predicting on test set...')
    test_data = pd.read_csv('candidate_passages_top1000.tsv', sep='\t', header=None)
    with open(test_data_path, 'rb') as f:
        test_embeddings_data = np.load(f)
    test_scores = model.predict(test_embeddings_data)
    save_output_file(test_data, test_scores, 'LR')
    print('Done!')