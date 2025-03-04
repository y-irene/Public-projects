import math
import pandas as pd
import re
import numpy as np
from copy import deepcopy
from plot import *

class Data:
    def __init__(self, attributes, attributes_values, attribute_types, target_attribute, identifier = False):
        self.values = {}
        self.target_attribute = target_attribute
        for i in range(len(attributes)):
            if attributes[i] == target_attribute:
                self.target_attribute_value = attributes_values[i]
            else:
                self.values[attributes[i]] = attributes_values[i]

    def __str__(self):
        return str(self.values)

class Node:
    def __init__(self, attribute, attribute_type, cut_values, children, average_target_value, rss, data):
        self.attribute = attribute
        self.attribute_type = attribute_type
        self.cut_values = cut_values
        self.children = children
        self.average_target_value = average_target_value
        self.rss = rss
        self.data = data

    def print(self):
        print(self.to_string(1))

    def to_string(self, num_tabs):
        if not self.children:
            return str(self.average_target_value)
        s = self.attribute + " = [" + str(self.cut_values) + "]"
        for c in self.children:
            s += "\n" + num_tabs * "\t" + c.to_string(num_tabs + 1)
        return s

    def predict(self, data):
        node = self
        while(node.children != None):
            attribute_value = data.values[node.attribute]
            if attribute_value == '?':
                node = node.children[0]
                continue
            if node.attribute_type == 'c':
                cut_value = node.cut_values[0]

                if attribute_value <= cut_value:
                    node = node.children[0]
                else:
                    node = node.children[1]
            else:
                index_of_child = -1
                if attribute_value in node.cut_values:
                    index_of_child = node.cut_values.index(attribute_value)
                else:
                    smalles_diff = float('inf')
                    for i in range(len(node.cut_values)):
                        if abs(node.cut_values[i] - attribute_value) < smalles_diff:
                            smalles_diff = abs(node.cut_values[i] - attribute_value)
                            index_of_child = i
                node = node.children[index_of_child]

        return node.average_target_value


def mean_square_error(target_attribute_values, mean_target_attribute_value):
    return np.mean(np.square(np.array([target_value - mean_target_attribute_value  for target_value in target_attribute_values])))

def rss_node(sections):
    val = 0
    for section in sections:
        target_attribute_values = list(map(lambda data: data.target_attribute_value, section))
        mean_target_attribute_value = np.mean(np.array(target_attribute_values))
        val += np.sum(np.square(np.array(list(map(lambda target: target - mean_target_attribute_value, target_attribute_values)))))
    return val

def rss_leaf(data):
    target_attribute_values = list(map(lambda data: data.target_attribute_value, data))
    mean_target_attribute_value = np.mean(np.array(target_attribute_values))
    return np.sum(np.square(np.array(target_attribute_values) - np.array([mean_target_attribute_value for x in target_attribute_values])))

def get_attribute_cuts(data, attribute, attribute_type):
    cuts = []
    if attribute_type == 'c':
        attribute_values = list(set([d.values[attribute] for d in data]))
        attribute_values = list(filter(lambda x: x != '?', attribute_values))
        attribute_values.sort()
        for i in range(len(attribute_values) - 1):
            cuts.append((attribute_values[i] + attribute_values[i + 1]) / 2)
    elif attribute_type == 'd':
        cuts = list(set([d.values[attribute] for d in data]))
        cuts = list(filter(lambda x: x != '?', cuts))
        cuts.sort()
    return cuts

def create_tree(data, attributes, attributes_types_d, target_attribute):
    target_attribute_values = list(map(lambda data: data.target_attribute_value, data))
    mean_target_attribute_value = np.mean(np.array(target_attribute_values))
    mse = mean_square_error(target_attribute_values, mean_target_attribute_value)

    if len(data) <= 5 or mse == 0:
        leaf_rss = rss_leaf(data)
        return Node(None, None, None, None, mean_target_attribute_value, leaf_rss, data)

    best_cut_attribute = None
    best_cut_value = None
    best_rss = None
    best_sections = None
    for attribute in attributes:
        if attribute != target_attribute:
            cuts = get_attribute_cuts(data, attribute, attributes_types_d[attribute])
            if attributes_types_d[attribute] == 'c':
                for cut in cuts:
                    sections = []
                    sections.append(list(filter(lambda d: d.values[attribute] <= cut if d.values[attribute] != '?' else True, data)))
                    sections.append(list(filter(lambda d: d.values[attribute] > cut if d.values[attribute] != '?' else False, data)))
                    rss_val = rss_node(sections)
                    if not best_rss or rss_val < best_rss:
                        best_rss = rss_val
                        best_cut_attribute = attribute
                        best_cut_value = [cut]
                        best_sections = sections
            elif attributes_types_d[attribute] == 'd':
                sections = []
                for cut in cuts:
                    sections.append(list(filter(lambda d: d.values[attribute] == cut, data)))
                rss_val = rss_node(sections)
                if not best_rss or rss_val < best_rss:
                    best_rss = rss_val
                    best_cut_attribute = attribute
                    best_sections = sections
                    best_cut_value = cuts

    children = []
    for section in best_sections:
        children.append(create_tree(section, attributes, attributes_types_d, target_attribute))

    return Node(best_cut_attribute, attributes_types_d[best_cut_attribute], best_cut_value, children, None, best_rss, None)

def tree_leafs(root):
    if not root.children:
        return 1

    no_leafs = 0
    for c in root.children:
        no_leafs += tree_leafs(c)
    return no_leafs

def tree_nodes(root):
    if not root.children:
        return 1

    no_nodes = 0
    for c in root.children:
        no_nodes += tree_nodes(c)
    return no_nodes + 1

def tree_rsses(root):
    if not root.children:
        return [root.rss]

    rss = []
    for c in root.children:
        rss = rss + tree_rsses(c)
    return rss

def tree_leafs_data(root):
    if not root.children:
        return root.data

    data = []
    for c in root.children:
        data = data + tree_leafs_data(c)
    return data

def cost_complexity_prunning(root):
    T = root
    no_leafs = tree_leafs(T)
    no_nodes = tree_nodes(T)

    Ts = []
    alphas = []

    Ts. append(deepcopy(T))
    alphas.append(0)

    while (no_nodes > no_leafs + 1):
        nodes = T.children
        nodes = list(filter(lambda node: node.children != None, nodes))

        min_alpha = float('inf')
        min_t = None

        while len(nodes):
            t = nodes[0]
            children_nodes_t = list(filter(lambda node: node.children != None, t.children))
            nodes = nodes[1:] + children_nodes_t

            rss_t = t.rss
            T_rsses = tree_rsses(t)
            rss_T = np.mean(np.array(T_rsses))
            alpha = (rss_t - rss_T) / (len(T_rsses) - 1)

            if alpha < min_alpha:
                min_alpha = alpha
                min_t = t

        nodes = T.children
        nodes = list(filter(lambda node: node.children != None, nodes))
        while len(nodes):
            t = nodes[0]

            if t == min_t:
                t.data = tree_leafs_data(t)
                t.average_target_value = np.mean(np.array(list(map(lambda data: data.target_attribute_value, t.data))))
                t.rss = rss_leaf(t.data)
                t.attribute = None
                t.attribute_type = None
                t.cut_values = None
                t.children = None
                break

            children_nodes_t = list(filter(lambda node: node.children != None, t.children))
            nodes = nodes[1:] + children_nodes_t

        alphas.append(min_alpha)
        Ts.append(deepcopy(T))
        no_leafs = tree_leafs(T)
        no_nodes = tree_nodes(T)

    return Ts, alphas

def get_auto_data():
    file1 = open('auto-mpg.data', 'r')
    auto_attributes = ["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model year", "origin"]
    auto_attributes_types = ["c", "d", "c", "c", "c", "c", "d", "d"]
    auto_attributes_types_d = {}
    for i in range(len(auto_attributes)):
        auto_attributes_types_d[auto_attributes[i]] = auto_attributes_types[i]
    auto_target_attribute = "mpg"
    auto_data = []
    Lines = file1.readlines()
    for line in Lines:
        l = re.sub("  +", '_', line)
        l = re.sub('\t', '', l)
        l = re.sub('\n', '', l)
        parsed_line = re.split(r'_|"', l)
        parsed_line = parsed_line[:-2]
        parsed_line = list(map(lambda x: float(x) if x != '?' else x, parsed_line))
        auto_data.append(Data(auto_attributes, parsed_line, auto_attributes_types, auto_target_attribute, False))

    return auto_attributes, auto_attributes_types_d, auto_target_attribute, auto_data

def get_wine_data():
    df = pd.read_csv('winequality-red.csv', sep=';')
    wine_attributes = df.columns
    wine_attributes_types = ["c" for i in wine_attributes]
    wine_attributes_types[len(wine_attributes_types) - 1] = "d"
    wine_attributes_types_d = {}
    for i in range(len(wine_attributes)):
        wine_attributes_types_d[wine_attributes[i]] = wine_attributes_types[i]
    wine_target_attribute = "quality"
    wine_data = []
    df = df.reset_index()
    for index, row in df.iterrows():
        attributes_values = [row[attr] for attr in wine_attributes]
        wine_data.append(Data(wine_attributes, attributes_values, wine_attributes_types, wine_target_attribute, False))
    return wine_attributes, wine_attributes_types_d, wine_target_attribute, wine_data

def RMSE(predictions, actual_vaues):
    return np.sqrt(np.mean(np.square(np.array(predictions) - np.array(actual_vaues))))

def RMSEs_multiple_trees(Ts, test):
    RMSEs = []
    for T in Ts:
        predicted_values = []
        actual_values = []
        for t in test:
            prediction = T.predict(t)
            predicted_values.append(prediction)
            actual_values.append(t.target_attribute_value)
        RMSEs.append(RMSE(predicted_values, actual_values))
    return RMSEs

def split_into_folds(K, train, train_data_len):
    fold_len = math.floor(train_data_len / K)
    remaining = train_data_len - fold_len * K
    index = 0
    folds = []
    for i in range(K):
        if remaining > 0:
            folds.append(train[index: (index + fold_len + 1)])
            remaining -= 1
            index += fold_len + 1
        else:
            folds.append(train[index: (index + fold_len)])
            index += fold_len
    return folds

def k_fold_cross_validation(attributes, attributes_types_d, target_attribute, data, K):
    train_data_len = math.floor(len(data) * 0.8)
    train = data[:(train_data_len + 1)]
    test = data[(train_data_len + 1):]

    tree = create_tree(train, attributes, attributes_types_d, target_attribute)
    Ts, alphas = cost_complexity_prunning(tree)
    RMSEs = RMSEs_multiple_trees(Ts, test)
    plot_rmses(RMSEs, alphas)

    folds = split_into_folds(K, train, train_data_len)
    alpha_rmses_d = {}

    for k in range(K):
        test_fold = folds[k]
        train_folds = folds[:k] + folds[(k + 1):]
        train_data = [d for fold in train_folds for d in fold]

        folds_tree = create_tree(train_data, attributes, attributes_types_d, target_attribute)
        prunning_trees, prunning_alphas = cost_complexity_prunning(folds_tree)

        all_RMSEs = []
        RMSEs_k_fold = RMSEs_multiple_trees(prunning_trees, test_fold)
        all_RMSEs.append(RMSEs_k_fold)
        for fold in train_folds:
            RMSEs_fold = RMSEs_multiple_trees(prunning_trees, fold)
            all_RMSEs.append(RMSEs_fold)

        all_RMSEs = list(np.array(all_RMSEs).T)
        avg_RMSEs = list(map(lambda errs: np.mean(errs), all_RMSEs))

        for i in range(len(prunning_alphas)):
            alpha = prunning_alphas[i]
            alpha_rmse = avg_RMSEs[i]
            if alpha in alpha_rmses_d:
                alpha_rmses_d[alpha].append(alpha_rmse)
            else:
                alpha_rmses_d[alpha] = [alpha_rmse]

    best_alpha = None
    min_rmse_avg = None
    for alpha in alpha_rmses_d:
        alpha_rmses_d[alpha] = np.mean(np.array(alpha_rmses_d[alpha]))
        if alpha in alphas:
            if not min_rmse_avg or alpha_rmses_d[alpha] < min_rmse_avg:
                min_rmse_avg = alpha_rmses_d[alpha]
                best_alpha = alpha

    best_index = alphas.index(best_alpha)
    best_tree = Ts[best_index]

    predictions = []
    actual_values = []
    for d in test:
        prediction = best_tree.predict(d)
        predictions.append(prediction)
        actual_values.append(d.target_attribute_value)

    rmse = RMSE(predictions, actual_values)
    return rmse


auto_attributes, auto_attributes_types_d, auto_target_attribute, auto_data = get_auto_data()
wine_attributes, wine_attributes_types_d, wine_target_attribute, wine_data = get_wine_data()
rmse_auto = k_fold_cross_validation(auto_attributes, auto_attributes_types_d, auto_target_attribute, auto_data, 10)
rmse_wine = k_fold_cross_validation(wine_attributes, wine_attributes_types_d, wine_target_attribute, wine_data, 10)
print("RMSE auto dataset = " + str(rmse_auto))
print("RMSE wine dataset = " + str(rmse_wine))

# Output
# RMSE auto dataset = 5.42663835145372
# RMSE wine dataset = 0.8810072684353267