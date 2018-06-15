import csv
import shutil
import os
import tensorflow as tf
from func2 import *
from func1 import *
import random

os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
tf.set_random_seed(777)  # reproducibility

# polygon data will grid by WIDTH_NUM X HEIGHT_NUM
WIDTH_NUM = 20
HEIGHT_NUM = 20

TRAINING_NUM = 10000
TEST_NUM = 1000
LEARNING_RATE = 0.001
TRAINING_EPOCHS = 201

BATCH_SIZE = 500

DATA_FOLDER = "buffer_005"

print("=========== LOAD DATA ===========")

train_x_data, train_y_data = load_data("../data/problem2/" + DATA_FOLDER + "/training_", TRAINING_NUM)
test_x_data, test_y_data = load_data("../data/problem2/" + DATA_FOLDER + "/test_", TEST_NUM)

train_x_data = grid(train_x_data, WIDTH_NUM, HEIGHT_NUM, [-5.0, 5., -5., 5.])  # -1,20,20,1
test_x_data = grid(test_x_data, WIDTH_NUM, HEIGHT_NUM, [-5.0, 5., -5., 5.])

print("=========== BATCH ===========")

batch_train_x, batch_train_y = tf.train.batch([train_x_data, train_y_data], enqueue_many=True, batch_size=BATCH_SIZE)


print("=========== BUILD GRAPH ===========")

# input place holders
X = tf.placeholder(tf.float32, [None, WIDTH_NUM, HEIGHT_NUM, 1])
Y = tf.placeholder(tf.float32, [None, 1])

keep_prob = tf.placeholder(tf.float32)

# L1 ImgIn shape=(?, 20, 20, 1)
W1 = tf.Variable(tf.random_normal([3, 3, 1, 32], stddev=0.01))
#    Conv     -> (?, 20, 20, 32)
#    Pool     -> (?, 10, 10, 32)
L1 = tf.nn.conv2d(X, W1, strides=[1, 1, 1, 1], padding='SAME')
L1 = tf.nn.relu(L1)
L1 = tf.nn.max_pool(L1, ksize=[1, 2, 2, 1],
                    strides=[1, 2, 2, 1], padding='SAME')
L1 = tf.nn.dropout(L1, keep_prob=keep_prob)

# L2 ImgIn shape=(?, 20, 20, 32)
W2 = tf.Variable(tf.random_normal([3, 3, 32, 64], stddev=0.01))
#    Conv      ->(?, 10, 10, 64)
#    Pool      ->(?, 5, 5, 64)
L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')
L2 = tf.nn.relu(L2)
L2 = tf.nn.max_pool(L2, ksize=[1, 2, 2, 1],
                    strides=[1, 2, 2, 1], padding='SAME')
L2_flat = tf.reshape(L2, [-1, 5 * 5 * 64])
L2_flat = tf.nn.dropout(L2_flat, keep_prob=keep_prob)

# FC 7x7x64 inputs -> 10 outputs
W3 = tf.get_variable("W3", shape=[5 * 5 * 64, 10],
                     initializer=tf.contrib.layers.xavier_initializer())
b = tf.Variable(tf.random_normal([10]))
L3 = tf.nn.relu(tf.matmul(L2_flat, W3) + b)
L3 = tf.nn.dropout(L3, keep_prob=keep_prob)

W_hypo, b_hypo, hypothesis = make_layer_sigmoid("W4", L3, 10, 1)
hypothesis = hypothesis * 0.998 + 0.001
cost = -tf.reduce_mean(Y * tf.log(hypothesis) + (1 - Y) * tf.log(1 - hypothesis))
tf.summary.scalar("cost", cost)

optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE).minimize(cost)

# Calculate accuracy
predicted = tf.cast(hypothesis > 0.5, dtype=tf.float32)
accuracy = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), dtype=tf.float32))
accuracy_summ = tf.summary.scalar("accuracy", accuracy)

print("=========== LEARNING START ===========")

# initialize
with tf.Session() as sess:
    sess.run(tf.local_variables_initializer())
    sess.run(tf.global_variables_initializer())

    # initialize the queue threads to start to shovel data
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    merged_summary = tf.summary.merge_all()
    log_file_path = "../logs/problem2"
    if os.path.exists(log_file_path):
        shutil.rmtree(log_file_path)
    writer = tf.summary.FileWriter(log_file_path)
    writer.add_graph(sess.graph)  # Show the graph

    for epoch in range(TRAINING_EPOCHS):
        avg_cost = 0
        total_batch = int(len(train_x_data) / BATCH_SIZE)

        for bi in range(total_batch):
            batch_xs, batch_ys = sess.run([batch_train_x, batch_train_y])
            c, _ = sess.run([cost, optimizer], feed_dict={X: batch_xs, Y: batch_ys, keep_prob: 0.7})
            avg_cost += c
        avg_cost /= total_batch

        batch_xs, batch_ys = sess.run([batch_train_x, batch_train_y])
        summary = sess.run(merged_summary, feed_dict={X: batch_xs, Y: batch_ys, keep_prob: 1.0})
        writer.add_summary(summary, global_step=epoch)

        if epoch % int(TRAINING_EPOCHS / 10) == 0:
            print(epoch, ' cost = ', avg_cost)
            # print("TEST accuarcy ", sess.run(accuracy, feed_dict={X: test_x_data, Y: test_y_data, keep_prob: 1.0}))
            assert (avg_cost == avg_cost)

    print("Learning finished\n")
    tf.summary.FileWriterCache.clear()
    writer.close()

    # print("\nTrain Accracy : ", sess.run(accuracy, feed_dict={X: train_x_data, Y: train_y_data, keep_prob: 1.0}))
    h, c, a = sess.run([hypothesis, predicted, accuracy], feed_dict={X: test_x_data, Y: test_y_data, keep_prob: 1.0})
    print("\nAccuracy: ", a)

    result_filename = "../result/problem2_model2_01_" + DATA_FOLDER + ".txt"
    os.makedirs(os.path.dirname(result_filename), exist_ok=True)
    result = open(result_filename, 'w')
    result.write("%f\n" % a)
    for item1, item2 in zip(h, c):
        result.write("%s %s\n" % (item1[0], item2[0]))