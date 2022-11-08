from mysklearn import myutils

class MyKNeighborsClassifier:
    """Represents a simple k nearest neighbors classifier.

    Attributes:
        n_neighbors(int): number of k neighbors
        X_train(list of list of numeric vals): The list of training instances (samples).
                The shape of X_train is (n_train_samples, n_features)
        y_train(list of obj): The target y values (parallel to X_train).
            The shape of y_train is n_samples

    Notes:
        Terminology: instance = sample = row and attribute = feature = column
        Assumes data has been properly normalized before use.
    """
    def __init__(self, n_neighbors=3):
        """Initializer for MyKNeighborsClassifier.

        Args:
            n_neighbors(int): number of k neighbors
        """
        self.n_neighbors = n_neighbors
        self.X_train = None
        self.y_train = None

    def fit(self, X_train, y_train):
        """Fits a kNN classifier to X_train and y_train.

        Args:
            X_train(list of list of numeric vals): The list of training instances (samples).
                The shape of X_train is (n_train_samples, n_features)
            y_train(list of obj): The target y values (parallel to X_train)
                The shape of y_train is n_train_samples

        Notes:
            Since kNN is a lazy learning algorithm, this method just stores X_train and y_train
        """
        self.X_train = X_train
        self.y_train = y_train

    def kneighbors(self, X_test):
        """Determines the k closes neighbors of each test instance.

        Args:
            X_test(list of list of numeric vals): The list of testing samples
                The shape of X_test is (n_test_samples, n_features)

        Returns:
            distances(list of list of float): 2D list of k nearest neighbor distances
                for each instance in X_test
            neighbor_indices(list of list of int): 2D list of k nearest neighbor
                indices in X_train (parallel to distances)
        """
        raw_distances = []

        for test in X_test:
            row_dist = []
            for train in self.X_train:
                d = myutils.euclidean_distance(train, test)
                row_dist.append(d)
            raw_distances.append(row_dist)

        # finding the nearest distances
        sorted_distances = []
        sorted_neighbors = []
        
        for item in raw_distances:
            row_sort_dist = []
            row_sort_neighbors = []
            for i in range(self.n_neighbors):
                index = item.index(min(item))
                dist = item.pop(index)
                item.insert(index, max(item)+1)

                row_sort_neighbors.append(index)
                row_sort_dist.append(dist)

            sorted_distances.append(row_sort_dist)
            sorted_neighbors.append(row_sort_neighbors)

        return sorted_distances, sorted_neighbors

    def predict(self, X_test):
        """Makes predictions for test instances in X_test.

        Args:
            X_test(list of list of numeric vals): The list of testing samples
                The shape of X_test is (n_test_samples, n_features)

        Returns:
            y_predicted(list of obj): The predicted target y values (parallel to X_test)
        """
        y_predicted = []
        distances, neighbors = self.kneighbors(X_test)

        for item in neighbors:
            item_pred = []
            for index in item:
                item_pred.append(self.y_train[index])
            values, count = myutils.get_frequencies(item_pred)

            # find max of count for tie purposes
            _max_ = max(count)
            _max_index_ = count.index(_max_)

            max_list = []
            for i in range(len(count)):
                if count[i] == _max_:
                    max_list.append(values[i])
            
            # if tie, use whichever value appears first in prediction, ordered by proximity
            if len(max_list) > 1:
                for item in item_pred:
                    if item in max_list:
                        y_predicted.append(item)
                        break

            # if no tie, simply append whatever value has max count
            else:
                y_predicted.append(values[_max_index_])

        return y_predicted