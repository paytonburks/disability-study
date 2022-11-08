import random
import numpy as np

def shuffle_1(X, random_state):
    random.seed(random_state)
    k = random.sample(range(len(X)), len(X))
    X = [X[i] for i in k]
    return X

def randomize_in_place(alist, seed, parallel_list=None):
    np.random.seed(seed)
    for i in range(len(alist)):
        # generate a random index to swap values with 
        rand_index = np.random.randint(0, len(alist)) # [0, len(alist))
        alist[i], alist[rand_index] = alist[rand_index], alist[i]
        if parallel_list is not None:
            parallel_list[i], parallel_list[rand_index] =\
                parallel_list[rand_index], parallel_list[i]
    return alist, parallel_list

def groupby(X,y):
    X_group = [] # list of list of ints (indexes)
    y_group = [] # 1D list 
    for i in range(len(y)):
        if y[i] not in y_group:
            y_group.append(y[i])
            X_group.append([i])
        else:
            X_group[y_group.index(y[i])].append(i)
        
    return X_group, y_group

def X_train_test_CV(n_splits, folds):
    X_train_folds = []
    X_test_folds = []

    # holdout sets = X_test_folds
    # training sets = X_train_folds

    # iterate through each train/test set
    for i in range(n_splits):
        # iterate through each fold
        test = []
        train = []
        for j in range(len(folds)):
            # if the fold matches the iteration number, add to testing
            if j == i:
                for item in folds[j]:
                    test.append(item)
            # if the fold doesn't match, add to training
            else:
                for item in folds[j]:
                    train.append(item)
        X_test_folds.append(test)
        X_train_folds.append(train)

    return X_train_folds, X_test_folds

def euclidean_distance(v1, v2):
    sum = 0
    for i in range(len(v1)):
        sum += (v1[i] - v2[i]) ** 2
    sum = sum ** (1/2)
    return sum

def get_frequencies(y_vals):
    y_vals.sort() 
    
    values = []
    counts = []
    for value in y_vals:
        if value in values: 
            counts[-1] += 1
        else: 
            values.append(value)
            counts.append(1)

    return values, counts 

def get_cols(X):
    cols = []
    for item in X[0]:
        cols.append([])
    
    for item in X:
        for i in range(len(cols)):
            cols[i].append(item[i])

    return cols
    
def prepend_equal(table, header):
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = header[j] + "=" + str(table[i][j])

def select_features(table, columns):
    t = []

    for instance in table:
        row = []
        for item in columns:
            row.append(instance[item-1])
        t.append(row)
    
    return t
