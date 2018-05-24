import tensorflow as tf
import numpy as np
import random
tf.set_random_seed(777)  # for reproducibility

BATCH_SIZE = 32
N_FEATURES = 2
LEARNING_RATE = 0.1
HIDDEN_LAYER_INPUTS = [2, 2, 2]

index = 0
file_name = "../data/problem1/points_" + str(index) + ".csv"
points_file = open(file_name, "r")
data_num = int(points_file.readline())

# for test
xy = np.loadtxt(file_name, delimiter=',', dtype=np.float32, skiprows=1)
x_data = xy[:, 0:-1]
y_data = xy[:, [-1]]

filename_queue = tf.train.string_input_producer([file_name], shuffle=False, name='filename_queue')

reader = tf.TextLineReader(skip_header_lines=1)
key, value = reader.read(filename_queue)

record_defaults = [[0.0], [0.0], [0]]
data = tf.decode_csv(value, record_defaults=record_defaults, field_delim=',')

train_x_batch, train_y_batch = tf.train.batch([data[0:-1], data[-1:]], batch_size=BATCH_SIZE)

X = tf.placeholder(tf.float32, [None, N_FEATURES], name='x-input')
Y = tf.placeholder(tf.float32, [None, 1], name='y-input')

with tf.name_scope("layer1") as scope:
    W1 = tf.Variable(tf.random_normal([N_FEATURES, HIDDEN_LAYER_INPUTS[0]]), name='weight1')
    b1 = tf.Variable(tf.random_normal([HIDDEN_LAYER_INPUTS[0]]), name='bias1')
    layer1 = tf.sigmoid(tf.matmul(X, W1) + b1)

    w1_hist = tf.summary.histogram("weights1", W1)
    b1_hist = tf.summary.histogram("biases1", b1)
    layer1_hist = tf.summary.histogram("layer1", layer1)

with tf.name_scope("layer2") as scope:
    W2 = tf.Variable(tf.random_normal([HIDDEN_LAYER_INPUTS[0], HIDDEN_LAYER_INPUTS[2]]), name='weight2')
    b2 = tf.Variable(tf.random_normal([HIDDEN_LAYER_INPUTS[2]]), name='bias2')
    layer2 = tf.sigmoid(tf.matmul(layer1, W2) + b2)

    w2_hist = tf.summary.histogram("weights2", W2)
    b2_hist = tf.summary.histogram("biases2", b2)
    layer2_hist = tf.summary.histogram("layer2", layer2)

with tf.name_scope("layer3") as scope:
    Wh = tf.Variable(tf.random_normal([HIDDEN_LAYER_INPUTS[2], 1]), name='weight_h')
    bh = tf.Variable(tf.random_normal([1]), name='bias_h')
    hypothesis = tf.sigmoid(tf.matmul(layer2, Wh) + bh)

    wh_hist = tf.summary.histogram("weights_h", Wh)
    bh_hist = tf.summary.histogram("biases_h", bh)
    hypothesis_hist = tf.summary.histogram("hypothesis", hypothesis)

with tf.name_scope("cost") as scope:
    cost = -tf.reduce_mean(Y * tf.log(hypothesis) + (1 - Y) * tf.log(1 - hypothesis))

with tf.name_scope("train") as scope:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=LEARNING_RATE).minimize(cost)

# Calculate accuracy
predicted = tf.cast(hypothesis > 0.5, dtype=tf.float32)
accuracy = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), dtype=tf.float32))
accuracy_summ = tf.summary.scalar("accuracy", accuracy)

training_epochs = 150

with tf.Session() as sess:
    merged_summary = tf.summary.merge_all()
    writer = tf.summary.FileWriter("./logs/problem1_batch_r01_w4_d3")
    writer.add_graph(sess.graph)  # Show the graph

    # Initialize TensorFlow variables
    sess.run(tf.global_variables_initializer())
    sess.run(tf.local_variables_initializer())
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    for epoch in range(training_epochs):
        avg_cost = 0
        total_batch = int(data_num / BATCH_SIZE)

        for i in range(total_batch):
            x_batch, y_batch = sess.run([train_x_batch, train_y_batch])

            c, _ = sess.run([cost, optimizer], feed_dict={
                            X: x_batch, Y: y_batch})
            avg_cost += c / total_batch

        summary = sess.run([merged_summary], feed_dict={X:x_data, Y:y_data})
        writer.add_summary(summary[0], global_step=epoch)

        print('Epoch:', '%04d' % (epoch + 1),
              'cost =', '{:.9f}'.format(avg_cost))

    print("Learning finished")

    # Test the model using test sets

    # Accuracy report
    h, c, a = sess.run([hypothesis, predicted, accuracy],
                       feed_dict={X: x_data, Y: y_data})
    print('\nHypothesis: %d', h)
    print("\nCorrect (Y): ", c, "\nAccuracy: ", a)

    coord.request_stop()
    coord.join(threads)

