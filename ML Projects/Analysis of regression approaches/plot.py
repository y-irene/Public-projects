import numpy as np
import matplotlib.pyplot as plt

colors = ['r', 'b', 'g', 'm', 'c', 'y', 'k', 'coral', 'rebeccapurple', 'lime', 'dimgrey', 'indianred', 'maroon', 'tomato', 'darkorange', 'darkgoldenrod', 'darkkhaki', 'lawngreen', 'deeppink', 'darkolivegreen']

def plot_prediction(X_train, X_test, t_train, t_test, y_train, y_test, title):
    X = np.array(list(X_train) + list(X_test))
    y = np.array(list(y_train) + list(y_test))
    X = np.concatenate(X).ravel()
    sort = np.argsort(X)
    y = y[sort]
    X = X[sort]
    plt.scatter(X_train, t_train, facecolor="b", edgecolor="b", label="Training data")
    plt.scatter(X_test, t_test, facecolor="r", edgecolor="r", label="Test data")
    plt.title(title)
    plt.xlabel("x (feature)")
    plt.ylabel("y (output)")
    plt.plot(X, y, label="Prediction")
    plt.legend()
    plt.savefig('./Graphs/' + title + '.png')
    plt.show()

def plot_comparative_graphs_cfs_gd(X_train, X_test, t_train, t_test, y_train_cfs, y_test_cfs, y_train_gd, y_test_gd, lr, title1, title2):
    X = np.array(list(X_train) + list(X_test))
    y_csf = np.array(list(y_train_cfs) + list(y_test_cfs))
    y_gd = np.array(list(y_train_gd) + list(y_test_gd))
    X = np.concatenate(X).ravel()
    sort = np.argsort(X)
    y_csf = y_csf[sort]
    y_gd = y_gd[sort]
    X = X[sort]

    f = plt.figure()
    f.set_figwidth(8)
    f.set_figheight(7)

    plt.scatter(X_train, t_train, facecolor="b", edgecolor="b", label="Training data", alpha=0.5)
    plt.scatter(X_test, t_test, facecolor="r", edgecolor="r", label="Test data", alpha=0.5)
    plt.title(title1)
    plt.xlabel("x (feature)")
    plt.ylabel("y (output)")
    plt.plot(X, y_csf, label="Closed-form solution", linewidth=2, color="c", alpha=0.5)
    plt.plot(X, y_gd, label="Gradient descent solution, lr = " + str(lr), linewidth=2, color="m", alpha=0.5)
    plt.legend()
    plt.savefig('./Graphs/' + title1 + '.png')
    plt.show()

    f = plt.figure()
    f.set_figwidth(8)
    f.set_figheight(7)
    plt.scatter(t_train, y_train_cfs, facecolor="c", edgecolor="c", label="Closed-form solution", alpha=0.5)
    plt.scatter(t_test, y_test_cfs, facecolor="c", edgecolor="c", alpha=0.5)
    plt.scatter(t_train, y_train_gd, facecolor="m", edgecolor="m", label="Gradient descent solution, lr = " + str(lr), alpha=0.5)
    plt.scatter(t_test, y_test_gd, facecolor="m", edgecolor="m", alpha=0.5)
    t = list(t_train) + list(t_test)
    x = np.linspace(min(t), max(t), 1000)
    plt.plot(x, x + 0, linestyle='dotted')
    plt.title(title2)
    plt.xlabel("True output")
    plt.ylabel("Predicted output")
    plt.legend()
    plt.savefig('./Graphs/' + title2 + '.png')
    plt.show()


def plot_quality_of_prediction(t_train, t_test, y_train, y_test, title):
    plt.scatter(t_train, y_train, facecolor="b", edgecolor="b", label="Training data")
    plt.scatter(t_test, y_test, facecolor="r", edgecolor="r", label="Test data")
    t = list(t_train) + list(t_test)
    x = np.linspace(min(t), max(t), 1000)
    plt.plot(x, x + 0, linestyle='dotted')
    plt.title(title)
    plt.xlabel("True output")
    plt.ylabel("Predicted output")
    plt.legend()
    plt.savefig('./Graphs/' + title + '.png')
    plt.show()

def plot_error(errors, epochs, title, xlabel):
    plt.plot(epochs, errors, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Empirical risk")
    plt.savefig('./Graphs/' + title + '.png')
    plt.show()

def plot_errors(errors_list, epochs, lrs, title, graph_labels):
    for i in range(len(errors_list)):
        label = graph_labels + str(lrs[i])
        plt.plot(epochs, errors_list[i], color=colors[i], marker='o', label=label)
    plt.title(title)
    plt.legend()
    plt.xlabel("Number of iterations")
    plt.ylabel("Empirical risk")
    plt.savefig('./Graphs/' + title + '.png')
    plt.show()

def plot_error_problem2(errors, tests, title):
    f = plt.figure()
    f.set_figheight(7)
    f.set_figwidth(20)
    plt.plot(tests, errors, marker='o')
    plt.title(title)
    plt.xlabel("Test")
    plt.ylabel("Average error")
    plt.savefig('./Graphs/' + title + '.png')
    plt.show()

def plot_mse(all_mses, alphas, x):
    f = plt.figure()
    f.set_figheight(15)
    f.set_figwidth(15)
    for i in range(len(alphas)):
        plt.plot(x, all_mses[alphas[i]], marker='o', label='alpha = ' + str(alphas[i]))
    plt.title("Mean Square Errors")
    plt.legend()
    plt.xlabel("Iteration")
    plt.ylabel("MSE")
    plt.savefig('./Graphs/MSEs.png')
    plt.show()

def plot_best_alphas(tests, best_alpha):
    plt.plot(tests, best_alpha, marker='o')
    plt.title("Best alphas")
    plt.xlabel("Test")
    plt.ylabel("Best alpha")
    plt.savefig('./Graphs/Best_alphas.png')
    plt.show()

def plot_rmses(rmses, alphas):
    f = plt.figure()
    f.set_figheight(10)
    f.set_figwidth(15)
    plt.plot(alphas, rmses, marker='o')
    plt.title("Root Mean Square Errors")
    plt.xlabel("Alpha")
    plt.ylabel("RMSE")
    plt.savefig('./Graphs/RMSEs.png')
    plt.show()