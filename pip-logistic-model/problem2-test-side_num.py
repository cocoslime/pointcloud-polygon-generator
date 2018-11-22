import os
from loaddata import *
from func1 import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import colors

models = __import__("problem2-models")

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

tf.reset_default_graph()

PIXEL = 32

TEST_EPOCHS = 200
BATCH_SIZE = 100

# DENSITY_OPT = "p---100"
BUFFER_OPT = "001"
DIR_NAME = "side_num"
MODEL = "model1"
DATA_DIR = "../data/problem2/non_convex/raster_pc/" + DIR_NAME + "/"

TEST_FILEPATH = DATA_DIR + "test_" + BUFFER_OPT + ".csv"
SAVER_FILEPATH = "../tmp/problem2/" + MODEL + "/model.ckpt"

record_defaults = [[0.]] * (PIXEL * PIXEL + 3)

test_xy_data = make_decode_CSV_list([TEST_FILEPATH], record_defaults)

print("=========== BATCH - TEST ===========")

test_x_data = test_xy_data[2:-1]
test_y_data = test_xy_data[-1]
test_y_data = tf.reshape(test_y_data, [1])
test_index_data = test_xy_data[0]
test_sidenum_data = test_xy_data[1]

batch_test_x, batch_test_y, batch_test_index, batch_test_sidenum = tf.train.batch([test_x_data, test_y_data, test_index_data, test_sidenum_data],
                                                                                  enqueue_many=False, batch_size=BATCH_SIZE, num_threads=8)

print("=========== BUILD GRAPH ===========")

# input place holders
X = tf.placeholder(tf.float32,  [None, PIXEL * PIXEL])
X_img = tf.reshape(X, [-1, PIXEL, PIXEL, 1])
Y = tf.placeholder(tf.float32, [None, 1])
keep_prob = tf.placeholder(tf.float32)

if MODEL == "model1":
    hypothesis = models.model1(X_img, keep_prob)
elif MODEL == "model2":
    hypothesis = models.model2(X_img, keep_prob)
else:
    exit(1)

cost = -tf.reduce_mean(Y * tf.log(hypothesis) + (1 - Y) * tf.log(1 - hypothesis))

# Calculate accuracy
predicted = tf.cast(hypothesis > 0.5, dtype=tf.float32)
accuracy = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), dtype=tf.float32))

saver = tf.train.Saver()

with tf.Session() as sess:
    sess.run(tf.local_variables_initializer())
    sess.run(tf.global_variables_initializer())

    # initialize the queue threads to start to shovel data
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    print("RESTORE VARIABLE")
    saver.restore(sess, SAVER_FILEPATH)

    # Evaluation
    sidenum_acc_dict = np.zeros((10, 2))

    total_accuracy = 0
    for epoch in range(TEST_EPOCHS):
        if epoch % 10 == 0:
            print(epoch)
        batch_xs, batch_ys, batch_index, batch_sidenum = sess.run([batch_test_x, batch_test_y, batch_test_index, batch_test_sidenum])
        _h, _predicted, _a = sess.run([hypothesis, predicted, accuracy],
                                      feed_dict={X: batch_xs, Y: batch_ys, keep_prob: 1.0})
        for index, value in enumerate(batch_ys):
            side_num = int(batch_sidenum[index])
            sidenum_acc_dict[side_num][0] += 1
            sidenum_acc_dict[side_num][1] += int(_predicted[index][0] == value[0])

        total_accuracy += _a
    total_accuracy /= TEST_EPOCHS

    print("\nAccuracy: ", total_accuracy)

    pltx = []
    plty = []

    for index, value in enumerate(sidenum_acc_dict):
        if value[0] == 0:
            continue
        pltx.append(index)
        plty.append(value[1] / value[0])

    # fig = plt.figure()
    # ax1 = fig.add_subplot(1, 1, 1)
    # ax1.set_yticks(np.arange(0.7, 1.0, 0.02))
    # ax1.plot(pltx, plty)
    # plt.grid()
    # plt.show()

    plt.plot(pltx, plty)
    plt.axis([3, 8, 0.0, 1.0])
    for i, j in zip(pltx, plty):
        plt.annotate(str(j), xy = (i, j + 0.1))
    plt.grid()
    plt.show()

    print(sidenum_acc_dict)

    coord.request_stop()
    coord.join(threads)
    sess.close()

