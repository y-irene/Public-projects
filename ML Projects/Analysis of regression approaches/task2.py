from dataset import *
from plot import *

def extract_polynomial_features(X, M):
    result = []
    for x in X:
        x_m = [1]
        for m in range(1, M + 1):
            for val in x:
                x_m.append(val ** m)
        result.append(x_m)
    return np.array(result)

class RidgeRegression(object):
    def __init__(self, alpha: float=1.):
        self.alpha = alpha

    def fit(self, X, t):
        N, D = X.shape
        self.w = np.linalg.inv(X.T @ X + self.alpha * np.identity(D)) @ X.T @ t

    def predict(self, X):
        y = X @ self.w
        return y

def ridge_regression(X_train, X_test, t_train, alpha, M):
    X_train_feat = extract_polynomial_features(X_train, M)
    X_test_feat = extract_polynomial_features(X_test, M)

    model = RidgeRegression(alpha)
    model.fit(X_train_feat, t_train)
    y_train = model.predict(X_train_feat)
    y_test = model.predict(X_test_feat)

    return y_train, y_test

def error_function(y, t):
    return np.mean(np.square(t - y))

def split_data(X, T, M):
    X_t = list(map(lambda x, t: [x, t], list(X), list(T)))
    np.random.shuffle(X_t)
    batches = []
    for i in range(0, len(X), M):
        batch = X_t[i : (i + M)]
        batch_X = np.array(list(map(lambda b: b[0], batch)))
        batch_t = np.array(list(map(lambda b: b[1], batch)))
        batches.append([batch_X, batch_t])
    return batches

def ten_fold_validation(alpha, dataset):
    if dataset == 'simple':
        X, t = get_simple_dataset()
        M = 1
    else:
        X, t = get_complex_dataset()
        M = 4

    no_tests = 100
    dimension = int(len(t) / 10)
    errors = []
    test_mean_errors = []

    for i in range(no_tests):
        subsets = split_data(X, t, dimension)
        test_errors = []

        for j in range(len(subsets)):
            test = subsets[j]
            x_test = test[0]
            t_test = test[1]

            train = subsets[:j] + subsets[(j + 1):]
            x_train = []
            t_train = []
            for subset in train:
                x_train += list(subset[0])
                t_train += list(subset[1])

            y_train, y_test = ridge_regression(np.array(x_train), x_test, np.array(t_train), alpha, M)
            error = error_function(np.array(list(y_test)), np.array(list(t_test)))
            errors.append(error)
            test_errors.append(error)

        test_mean_errors.append(np.mean(np.array(test_errors)))

    errors = np.array(errors)
    mean_error = np.mean(errors)
    return errors, mean_error, test_mean_errors

def ten_fold_validation_test(dataset):
    errors, mean_error, test_mean_errors = ten_fold_validation(0.1, dataset)
    plot_error_problem2(test_mean_errors, range(1, len(test_mean_errors) + 1), "10-fold validation tests errors means, alpha = 0.1")

def best_alpha(alphas, no_tests, dataset):
    all_mses ={}
    best_alpha = []
    for a in alphas:
        all_mses[a] = []

    for i in range(no_tests):
        errors = []
        for a in alphas:
            errs, mean_error, test_mean_errors = ten_fold_validation(a, dataset)
            all_mses[a].append(mean_error)
            errors.append(mean_error)
        min_error = min(errors)
        best_alpha_index = errors.index(min_error)
        best_alpha.append(alphas[best_alpha_index])

    plot_mse(all_mses, alphas, range(1, 11))
    print(best_alpha)
    plot_best_alphas(range(1, 11), best_alpha)

alphas_simple = list(np.linspace(0.01, 0.2, 20))
alphas_complex = list(np.linspace(0.1, 2, 20))

# ten_fold_validation_test('simple')
# best_alpha(alphas_simple, 10, 'simple')

# ten_fold_validation_test('complex')
# best_alpha(alphas_simple, 10, 'complex')
