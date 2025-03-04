import numpy as np
from sklearn.model_selection import train_test_split
from dataset import *
from plot import *
from math import sqrt

def split_data(type, test_size):
    if type == 'simple':
        X, y = get_simple_dataset()
        return X, y, train_test_split(X, y, test_size=test_size, shuffle=True)
    if type == 'complex':
        X, y = get_complex_dataset()
        return X, y, train_test_split(X, y, test_size=test_size, shuffle=True)

def extract_polynomial_features(X, M):
    result = []
    for x in X:
        x_m = [1]
        for m in range(1, M + 1):
            for val in x:
                x_m.append(val ** m)
        result.append(x_m)
    return np.array(result)

def mean_squared_error(y, t):
    return np.mean(np.square(y - t))

#######################################################################################################################
# Close Form Solution
#######################################################################################################################
class CloseFormSolution(object):
    def fit(self, X_train, t_train):
        N, D = X_train.shape
        self.w = np.zeros(D)
        self.w = np.linalg.inv(X_train.T @ X_train) @ X_train.T @ t_train

    def predict(self, X):
        y = X @ self.w
        return y

def close_form_solution(X_train_feat, X_test_feat, t_train):
    model = CloseFormSolution()
    model.fit(X_train_feat, t_train)
    y_train = model.predict(X_train_feat)
    y_test = model.predict(X_test_feat)
    return y_train, y_test

#######################################################################################################################
# Gradient descent
#######################################################################################################################
class GradientDescent(object):
    def __init__(self, lr = .01, epochs_no = 50):
        self.lr = lr
        self.epochs_no = epochs_no

    def train(self, X, t):
        N, D = X.shape
        self.w = np.random.randn(D)
        errors_through_epochs = []

        for k in range(self.epochs_no):
            y = X @ self.w
            errors_through_epochs.append(mean_squared_error(y, t))
            y_t_diff = y - t
            X_train_T = X.T
            grad = []
            for j in range(len(X_train_T)):
                grad.append(self.lr * np.sum(np.multiply(y_t_diff, X_train_T[j])))
            grad = np.array(grad)
            self.w = self.w - grad

        return errors_through_epochs

    def predict(self, X):
        y = X @ self.w
        return y

def gradient_descent_solution(X_train_feat, X_test_feat, t_train, lr, epochs_no):
    model = GradientDescent(lr, epochs_no)
    errors_through_epochs = model.train(X_train_feat, t_train)
    y_train = model.predict(X_train_feat)
    y_test = model.predict(X_test_feat)
    return y_train, y_test, errors_through_epochs

#######################################################################################################################
# Mini-Batch Gradient Descent
#######################################################################################################################
class MiniBatchGradientDescent(object):
    def __init__(self, lr = .01, epochs_no = 50, M = 10):
        self.lr = lr
        self.epochs_no = epochs_no
        self.M = M

    @staticmethod
    def create_mini_batches(X, T, M):
        X_t = list(map(lambda x, t: [x, t], list(X), list(T)))
        batches = []
        for i in range(0, len(X), M):
            batch = X_t[i : (i + M)]
            batch_X = np.array(list(map(lambda b: b[0], batch)))
            batch_t = np.array(list(map(lambda b: b[1], batch)))
            batches.append([batch_X, batch_t])
        return batches

    @staticmethod
    def cost_function(w, X, T, M):
        return (X.T @ (X @ w - T)) / M

    def train(self, X, t):
        N, D = X.shape
        self.w = np.random.randn(D)
        batches = MiniBatchGradientDescent.create_mini_batches(X, t, self.M)

        for k in range(self.epochs_no):
            for b in batches:
                x_b = b[0]
                t_b = b[1]
                y = x_b @ self.w
                grad = MiniBatchGradientDescent.cost_function(self.w, x_b, t_b, self.M)
                self.w = self.w - self.lr * grad

    def predict(self, X):
        y = X @ self.w
        return y

def mini_batch_gradient_descent(X_train_feat, X_test_feat, t_train, lr, epochs_no, M):
    model = MiniBatchGradientDescent(lr, epochs_no, M)
    model.train(X_train_feat, t_train)
    y_train = model.predict(X_train_feat)
    y_test = model.predict(X_test_feat)
    return y_train, y_test

#######################################################################################################################
# Stochastic Gradient Descent
#######################################################################################################################
class StochasticGradientDescent(object):
    def __init__(self, lr = .01, epochs_no = 50):
        self.lr = lr
        self.epochs_no = epochs_no

    @staticmethod
    def create_mini_batches(X, T):
        batches = list(map(lambda x, t: [np.array([x]), t], list(X), list(T)))
        np.random.shuffle(batches)
        return batches

    @staticmethod
    def cost_function(w, X, T):
        return (X.T @ (X @ w - T))

    def train(self, X, t):
        N, D = X.shape
        self.w = np.random.randn(D)
        errors = []

        for k in range(self.epochs_no):
            batches = StochasticGradientDescent.create_mini_batches(X, t)
            for b in batches:
                x_b = b[0]
                t_b = b[1]
                y = x_b @ self.w
                grad = StochasticGradientDescent.cost_function(self.w, x_b, t_b)
                self.w = self.w - self.lr * grad
            y = self.predict(X)
            errors.append(mean_squared_error(y, t))

        return errors

    def predict(self, X):
        y = X @ self.w
        return y

def stochastic_gradient_descent(X_train_feat, X_test_feat, t_train, lr, epochs_no):
    model = StochasticGradientDescent(lr, epochs_no)
    errors = model.train(X_train_feat, t_train)
    y_train = model.predict(X_train_feat)
    y_test = model.predict(X_test_feat)
    return y_train, y_test, errors


def test_noise_influence_over_rmse():
    noises_simple = [5, 10, 15, 25, 30, 35]
    Xs_simple, ys_simple = get_simple_dataset_different_noise(noises_simple)
    noises_complex = [0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 1, 2]
    Xs_complex, ys_complex = get_complx_dataset_different_noise(noises_complex)

    errors_simple = []
    for i in range(len(Xs_simple)):
        X = Xs_simple[i]
        y = ys_simple[i]
        X_train, X_test, t_train, t_test = train_test_split(X, y, test_size=.2, shuffle=True)
        X_train_feat = extract_polynomial_features(X_train, 1)
        X_test_feat = extract_polynomial_features(X_test, 1)
        y_train_cf, y_test_cf = close_form_solution(X_train_feat, X_test_feat, t_train)
        t = list(t_train) + list(t_test)
        predictions = list(y_train_cf) + list(y_test_cf)
        error = sqrt(mean_squared_error(np.array(predictions), np.array(t)))
        # error = sqrt(mean_squared_error(y_test_cf, t_test))
        errors_simple.append(error)

    errors_complex = []
    for i in range(len(Xs_complex)):
        X = Xs_complex[i]
        y = ys_complex[i]
        X_train, X_test, t_train, t_test = train_test_split(X, y, test_size=.2, shuffle=True)
        X_train_feat = extract_polynomial_features(X_train, 4)
        X_test_feat = extract_polynomial_features(X_test, 4)
        y_train_cf, y_test_cf = close_form_solution(X_train_feat, X_test_feat, t_train)
        t = list(t_train) + list(t_test)
        predictions = list(y_train_cf) + list(y_test_cf)
        error = sqrt(mean_squared_error(np.array(predictions), np.array(t)))
        # error = sqrt(mean_squared_error(y_test_cf, t_test))
        errors_complex.append(error)
    print(errors_complex)

    plt.plot(noises_simple, errors_simple, marker='o')
    plt.title("How noise affects RMSE for closed form, simple dataset")
    plt.xlabel("Noise")
    plt.ylabel("RMSE")
    plt.savefig('./Graphs/noiseRMSEsimple.png')
    plt.show()

    plt.plot(noises_complex, errors_complex, marker='o')
    plt.title("How noise affects RMSE for closed form, complex dataset")
    plt.xlabel("Noise")
    plt.ylabel("RMSE")
    plt.savefig('./Graphs/noiseRMSEcomplex.png')
    plt.show()

def test(dataset, lrs):
    X, y, (X_train, X_test, t_train, t_test) = split_data(dataset, 0.2)
    w, v = np.linalg.eig(X @ X.T)
    lr_gd = 1 / max(w).real
    lrs = [lr_gd] + lrs
    lr_gd_cmp = {'simple': lr_gd, 'complex': .0001}
    epochs_no = 100
    Ms = [5, 10, 20, 25, 50]

    # no_features = range(1, 7)
    if dataset == 'simple':
        no_features = [1, 2, 3, 4, 5]
    else:
        no_features = [4, 6, 5, 3, 2, 1]

    for no_feat in no_features[:1]:
        X_train_feat = extract_polynomial_features(X_train, no_feat)
        X_test_feat = extract_polynomial_features(X_test, no_feat)

        # Closed Form Solution
        y_train_cf, y_test_cf = close_form_solution(X_train_feat, X_test_feat, t_train)
        error_train_cf = mean_squared_error(y_train_cf, t_train)
        error_test_cf = mean_squared_error(y_test_cf, t_test)
        plot_prediction(X_train, X_test, t_train, t_test, y_train_cf, y_test_cf,
                        ("Closed Form Solution Prediction, number of features = " + str(no_feat)))
        plot_quality_of_prediction(t_train, t_test, y_train_cf, y_test_cf,
                                   "Closed Form Solution Quality of Prediction, number of features = " + str(no_feat)
                                   + "\n(err_train = " + str(error_train_cf) + "; err_test = " +
                                   str(error_test_cf)  +")")

        err_gd = []
        y_train_gds = []
        y_test_gds = []
        for lr in lrs:
            # Gradient Descent
            y_train_gd, y_test_gd, errors_gd = gradient_descent_solution(X_train_feat, X_test_feat, t_train, lr, epochs_no)
            y_train_gds.append(y_train_gd)
            y_test_gds.append(y_test_gd)
            err_gd.append(errors_gd[:(int(epochs_no / 2))])
            plot_prediction(X_train, X_test, t_train, t_test, y_train_gd, y_test_gd,
                            ("Gradient Descent Prediction\nnumber of features = " + str(no_feat) + " | lr = " + str(lr)))
            plot_quality_of_prediction(t_train, t_test, y_train_gd, y_test_gd,
                                       ("Gradient Descent Quality of Prediction\nnumber of features = " + str(no_feat) +
                                        " | lr = " + str(lr)))
            plot_error(errors_gd, range(epochs_no),
                                      ("Gradient Descent error values\nnumber of features = " + str(no_feat) +
                                       " | lr = " + str(lr)), "Number of iterations")

            err_mb = []
            for M in Ms:
                # Mini Batch Gradient Descent
                y_train_mb, y_test_mb = mini_batch_gradient_descent(X_train_feat, X_test_feat, t_train, lr, epochs_no, M)
                y_mb = np.array(list(y_train_mb) + list(y_test_mb))
                t = np.array(list(t_train) + list(t_test))
                err_mb.append(mean_squared_error(y_mb, t))
                plot_prediction(X_train, X_test, t_train, t_test, y_train_mb, y_test_mb,
                                ("Mini-Batch Gradient Descent (M = " + str(M) + "), Prediction\nnumber of features = " +
                                 str(no_feat) + " | lr = " + str(lr)))
                plot_quality_of_prediction(t_train, t_test, y_train_mb, y_test_mb,
                                           ("Mini-Batch Gradient Descent (M = " + str(
                                               M) + "), Quality of Prediction\nnumber of features = " +
                                            str(no_feat) + " | lr = " + str(lr)))

            plot_error(err_mb, Ms, ("Mini-Batch Gradient Descent errors\nnumber of features = " +
                       str(no_feat) + " | lr = " + str(lr)), "Batch size")

            # Stochastic Gradient Descent
            y_train_sgd, y_test_sgd, errors_sgd = stochastic_gradient_descent(X_train_feat, X_test_feat, t_train, lr, epochs_no)
            plot_prediction(X_train, X_test, t_train, t_test, y_train_sgd, y_test_sgd, ("Stochastic Gradient Descent Prediction\nnumber of features = " +
                                                      str(no_feat) + " | lr = " + str(lr)))
            plot_error(errors_sgd, range(epochs_no), ("Stochastic Gradient Descent Errors\nnumber of features = " +
                                                      str(no_feat) + " | lr = " + str(lr)), "Number of iterations")


        plot_errors(err_gd[1:-3], range(int(epochs_no / 2)), lrs[1:-3], ("Gradient Descent error values\nnumber of features = " + str(no_feat)),
                                   "lr = ")

        y_train_gd = y_train_gds[lrs.index(lr_gd_cmp[dataset])]
        y_test_gd = y_test_gds[lrs.index(lr_gd_cmp[dataset])]
        plot_comparative_graphs_cfs_gd(X_train, X_test, t_train, t_test, y_train_cf, y_test_cf, y_train_gd, y_test_gd,
                                       lrs[lrs.index(lr_gd_cmp[dataset])],
                                       'Prediction comparation between Closed Form (CF) and Gradient Descent (GD)\n no features = ' + str(no_feat),
                                       'Quality of prediction comparation between Closed Form (CF) and Gradient Descent (GD)\n no features = ' + str(no_feat))

    for no_feat in no_features[1:]:
        X_train_feat = extract_polynomial_features(X_train, no_feat)
        X_test_feat = extract_polynomial_features(X_test, no_feat)

        # Closed Form Solution
        y_train_cf, y_test_cf = close_form_solution(X_train_feat, X_test_feat, t_train)
        plot_prediction(X_train, X_test, t_train, t_test, y_train_cf, y_test_cf,
                        ("Closed Form Solution Prediction, number of features = " + str(no_feat)))

        # Gradient Descent
        y_train_gd, y_test_gd, errors_gd = gradient_descent_solution(X_train_feat, X_test_feat, t_train, 0.0001, epochs_no)
        plot_prediction(X_train, X_test, t_train, t_test, y_train_gd, y_test_gd,
                        ("Gradient Descent Prediction\nnumber of features = " + str(no_feat) + " | lr = " + str(0.0001)))

        # Mini Batch Gradient Descent
        y_train_mb, y_test_mb = mini_batch_gradient_descent(X_train_feat, X_test_feat, t_train, lr_gd, epochs_no, 5)
        plot_prediction(X_train, X_test, t_train, t_test, y_train_mb, y_test_mb,
                        ("Mini-Batch Gradient Descent (M = " + str(5) + "), Prediction\nnumber of features = " +
                         str(no_feat) + " | lr = " + str(lr_gd)))

        # Stochastic Gradient Descent
        y_train_sgd, y_test_sgd, errors_sgd = stochastic_gradient_descent(X_train_feat, X_test_feat, t_train, lr_gd,
                                                                          epochs_no)
        plot_prediction(X_train, X_test, t_train, t_test, y_train_sgd, y_test_sgd,
                        ("Stochastic Gradient Descent Prediction\nnumber of features = " +
                         str(no_feat) + " | lr = " + str(lr_gd)))


lrs_simple = [.0005, .001, .005, .01, .02]
lrs_complex = [.00001, .00005, .0001, .0005, .001, .002]
# test('simple', lrs_simple)
# test_noise_influence_over_rmse()
