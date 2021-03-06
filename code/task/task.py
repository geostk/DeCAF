# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from abc import abstractmethod, ABCMeta
import tensorflow as tf
import numpy as np

from utils import decaf
import dataset


class Task(object):
    __metaclass__ = ABCMeta

    def __init__(self, decaf_tensor_function):
        self.sess = tf.Session()
        self.input_tensor = tf.placeholder(tf.float32, (None, 227, 227, 3))
        self.decaf_tensor, _ = decaf_tensor_function(self.input_tensor)
        self.sess.run(tf.global_variables_initializer())

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def test(self):
        pass


class ObjectRecognitionTask(Task):
    def __init__(self):
        super(ObjectRecognitionTask, self).__init__(decaf.get_decaf_tensor_6)

        print "Running object recognition task"

        # define dataset
        self.dataset = dataset.Caltech101Dataset()

        # define model
        from sklearn import svm
        self.model = svm.LinearSVC()

    def train(self):
        all_train_data = []
        all_train_labels = []
        for (train_data, train_labels) in self.dataset.get_train_batch_iter():
            train_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: train_data})
            all_train_data.extend(train_decaf_data)
            all_train_labels.extend(train_labels)
        self.model.fit(all_train_data, all_train_labels)

        print 'Train: done!'

    def test(self):
        from sklearn.metrics import accuracy_score
        scores = []
        for (test_data, test_labels) in self.dataset.get_test_batch_iter():
            test_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: test_data})
            test_predictions = self.model.predict(test_decaf_data)
            scores.append(accuracy_score(test_labels, test_predictions))
        print 'Accuracy: {}'.format(np.average(scores))
        print 'Test: done!'


class DomainAdaptationTask(Task):
    def __init__(self, origin_domain, target_domain, combo):
        super(DomainAdaptationTask, self).__init__(decaf.get_decaf_tensor_6)

        print "Running domain adaptation task"

        # define dataset. domains = {0: "amazon", 1: "dslr", 2: "webcam"}
        print "Transfering from " + origin_domain + " to " + target_domain

        if combo == "S":
            self.origin_domain_dataset = dataset.OfficeDataset(domain=origin_domain, split=[1, 0, 0])
            self.target_domain_dataset = dataset.OfficeDataset(domain=target_domain, split=[0, 0, 1])
        else:
            self.origin_domain_dataset = dataset.OfficeDataset(domain=origin_domain, split=[1, 0, 0])
            self.target_domain_dataset = dataset.OfficeDataset(domain=target_domain, split=[0.19, 0, 0.81])

        self.combo = combo

        # define model
        from sklearn import svm
        self.model = svm.LinearSVC()

    def train(self):

        all_train_data = []
        all_train_labels = []
        if "S" in self.combo:
            for (train_data, train_labels) in self.origin_domain_dataset.get_train_batch_iter():
                train_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: train_data})
                all_train_data.extend(train_decaf_data)
                all_train_labels.extend(train_labels)
            self.model.fit(all_train_data, all_train_labels)

        if "T" in self.combo:
            print "Origin Domain Train: done!"
            for (train_data, train_labels) in self.target_domain_dataset.get_train_batch_iter():
                train_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: train_data})
                all_train_data.extend(train_decaf_data)
                all_train_labels.extend(train_labels)
            self.model.fit(all_train_data, all_train_labels)

            print "Target Domain Train: done!"
        print 'Train: done!'

    def test(self):
        from sklearn.metrics import accuracy_score
        scores = []
        for (test_data, test_labels) in self.target_domain_dataset.get_test_batch_iter():
            test_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: test_data})
            test_predictions = self.model.predict(test_decaf_data)
            scores.append(accuracy_score(test_labels, test_predictions))
        print 'Accuracy: {}'.format(np.average(scores))
        print 'Test: done!'


class SubcategoryRecognitionTask(Task):
    def __init__(self):
        super(SubcategoryRecognitionTask, self).__init__(decaf.get_decaf_tensor_6)

        print "Running subcategory recognition task"

        # define dataset
        self.dataset = dataset.BirdsDataset()

        # define model
        from sklearn import linear_model
        self.model = linear_model.LogisticRegression()

    def train(self):
        all_train_data = []
        all_train_labels = []

        for (train_data, train_labels) in self.dataset.get_train_batch_iter():
            train_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: train_data})

            all_train_data.extend(train_decaf_data)
            all_train_labels.extend(train_labels)

        self.model.fit(all_train_data, all_train_labels)
        print 'Train: done!'

    def test(self):
        from sklearn.metrics import accuracy_score
        scores = []
        for (test_data, test_labels) in self.dataset.get_test_batch_iter():
            test_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: test_data})
            test_predictions = self.model.predict(test_decaf_data)
            scores.append(accuracy_score(test_labels, test_predictions))
        print 'Accuracy: {}'.format(np.average(scores))
        print 'Test: done!'


class SceneObjectRecognitionTask(Task):

    def __init__(self):
        super(SceneObjectRecognitionTask, self).__init__(decaf.get_decaf_tensor_6)

        print "Running scene recognition task"

        # define dataset
        self.dataset = dataset.SUN397Dataset()

        # define model
        from sklearn import linear_model
        self.model = linear_model.LogisticRegression()

    def train(self):
        all_train_data = []
        all_train_labels = []
        for (train_data, train_labels) in self.dataset.get_train_batch_iter():
            train_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: train_data})

            all_train_data.extend(train_decaf_data)
            all_train_labels.extend(train_labels)

        self.model.fit(all_train_data, all_train_labels)
        print 'Train: done!'

    def test(self):
        from sklearn.metrics import accuracy_score
        scores = []
        for (test_data, test_labels) in self.dataset.get_test_batch_iter():
            test_decaf_data = self.sess.run(self.decaf_tensor, feed_dict={self.input_tensor: test_data})
            test_predictions = self.model.predict(test_decaf_data)
            scores.append(accuracy_score(test_labels, test_predictions))
        print 'Accuracy: {}'.format(np.average(scores))
        print 'Test: done!'
