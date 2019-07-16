# Copyright (C) 2019 Harvard University. All Rights Reserved. Unauthorized
# copying of this file, via any medium is strictly prohibited Proprietary and
# confidential
# Developed by Mohammad Haft-Javaherian <mhaft_javaherian@mgh.harvard.edu>,
#                                       <7javaherian@gmail.com>.
# ==============================================================================

"""CNN related operations"""

import numpy as np
import tensorflow as tf

from util.make_data_h5 import make_data_h5


def weight_variable(shape):
    initial = tf.random.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.0, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2_2(x):
    return tf.nn.max_pool2d(x, ksize=[1, 2, 2, 1],
                            strides=[1, 2, 2, 1], padding='SAME')


def conv_bn_relu(x, ChIn, ChOut):
    W_conv = weight_variable([3, 3, ChIn, ChOut])
    b_conv = bias_variable([ChOut])
    # h_conv = tf.nn.leaky_relu(tf.keras.layers.BatchNormalization()(conv2d(x, W_conv) + b_conv))
    h_conv = tf.nn.leaky_relu(conv2d(x, W_conv) + b_conv)
    return h_conv, W_conv, b_conv


def up_conv_2_2(x):
    x_shape = x.get_shape()
    # w = weight_variable([2, 2, x_shape[3].value, x_shape[3].value])
    # return tf.nn.conv2d_transpose(x, filter=w, output_shape=[2, 2 * x_shape[1].value,
    #                                             2 * x_shape[2].value, x_shape[3].value], strides=2)
    return tf.keras.layers.Conv2DTranspose(x_shape[3].value, 2, 2)(x)


def img_aug(im, l):
    """Data augmentation"""
    p_lim = 0.05
    for i in range(im.shape[0]):
        im_, l_ = im[i, ...], l[i, ...]
        if np.random.rand() > p_lim:  # y=x mirror
            im_ = im_.swapaxes(0, 1)
            l_ = l_.swapaxes(0, 1)
        if np.random.rand() > p_lim:  # y mirror
            im_ = im_[:, ::-1, :]
            l_ = l_[:, ::-1]
        if np.random.rand() > p_lim:  # x mirror
            im_ = im_[::-1, :, ]
            l_ = l_[::-1, :]
        if np.random.rand() > p_lim:  # 1st 90 deg rotation
            im_ = np.rot90(im_, k=1, axes=(0, 1))
            l_ = np.rot90(l_, k=1, axes=(0, 1))
        if np.random.rand() > p_lim:  # 2nd 90 degree rotation
            im_ = np.rot90(im_, k=1, axes=(0, 1))
            l_ = np.rot90(l_, k=1, axes=(0, 1))
        if np.random.rand() > p_lim:  # 3rd 90 degree rotation
            im_ = np.rot90(im_, k=1, axes=(0, 1))
            l_ = np.rot90(l_, k=1, axes=(0, 1))
        # if np.random.rand() > p_lim:  # salt-and-pepper noise
        #     im_ = im_ + 0.01 * (np.random.rand() - 0.5)
        im[i, ...], l[i, ...] = im_, l_
    return im, l


def one_hot(l, num_classes):
    return np.reshape(np.squeeze(np.eye(num_classes)[l.reshape(-1)]), l.shape + (num_classes, ))


def accuracy(labels, logits):
    """measure accuracy metrics"""
    accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(logits, -1), tf.argmax(labels, -1)), tf.float32), [1, 2])
    allButTN = tf.maximum(tf.argmax(logits, -1), tf.argmax(labels, -1))
    correct_prediction = tf.multiply(tf.argmax(logits, -1), tf.argmax(labels, -1))
    jaccard = tf.divide(tf.reduce_sum(tf.cast(correct_prediction, tf.float32)),
                        tf.reduce_sum(tf.cast(allButTN, tf.float32)))
    return accuracy, jaccard


def placeholder_inputs(im_shape, outCh):
    """Generate placeholder variables to represent the input tensors."""
    if im_shape[0] == 1:
        image = tf.placeholder(tf.float32, shape=[None, im_shape[1], im_shape[2], im_shape[3]])
        label = tf.placeholder(tf.float32, shape=[None, im_shape[1], im_shape[2], outCh])
    else:
        image = tf.placeholder(tf.float32, shape=[None, im_shape[0], im_shape[1], im_shape[2], im_shape[3]])
        label = tf.placeholder(tf.float32, shape=[None, im_shape[0], im_shape[1], im_shape[2], outCh])
    return image, label


def load_train_data(folder_path, im_shape):
    im, label = make_data_h5(folder_path, im_shape)
    assert im.size > 0, "The data folder is empty: %s" % folder_path

    im = im.astype(np.float32) / 255
    # label = np.clip(label, 1, None) - 1
    label = (label == 3).astype(np.uint8)
    im, label = np.squeeze(im, axis=1), np.squeeze(np.squeeze(label, axis=1), axis=-1)
    label = one_hot(label, 2)
    return im, label


def load_batch(im, label, datasetID, nBatch, iBatch=0, isTrain=True, isRandom=True, isAug=True):
    if isRandom:
        j = np.random.randint(0, len(datasetID), nBatch)
        im = im[datasetID[j], ...]
        if isTrain:
            label =label[datasetID[j], ...]
    else:
        j1, j2 = (iBatch * nBatch), ((iBatch + 1) * nBatch)
        im = im[datasetID[j1:j2], ...]
        if isTrain:
            label =label[datasetID[j1:j2], ...]
    if isAug:
        im, label = img_aug(im, label)
    if not isTrain:
        label = None
    return im, label
