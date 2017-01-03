
# coding: utf-8

# In[229]:

#get_ipython().magic(u'matplotlib inline')
import pandas as pd
import numpy as np

import fxtool as ft


# In[230]:

def get_candle_list(data, rate_types=["Open", "Close"]):
    
    change_list = []
    for o,c in zip(data[rate_types[0]],data[rate_types[1]]):
        change =  np.log(c/o)
        change_list.append(change)
    return change_list


# In[256]:

months = pd.date_range('2015-1', periods=6, freq='M')
months = months.tolist()
months_list = [m.strftime('%Y%m' ) for m in months]
months_list


# In[257]:

data = ft.read_csv(months_list)


# In[258]:

ohlc = ft.get_ohlc(data, '1H')

ohlc["Change(Close)"] =  ohlc["Close"].diff()
ohlc["Change(Open)"] = ohlc["Open"].diff()
ohlc["Change(Open-Close)"] = get_candle_list(ohlc)

ohlc.describe()


# In[271]:

ohlc['change_positive'] = 0
ohlc.ix[ohlc['Change(Open-Close)'] >= 0, 'change_positive'] = 1
ohlc['change_negative'] = 0
ohlc.ix[ohlc['Change(Open-Close)'] < 0, 'change_negative'] = 1

num_predictors = 50

data_columns = [
    'change_positive',  
    'change_negative'
]
for i in range(1,num_predictors+1):
    data_columns.append("change_"+str(i))

training_test_data = pd.DataFrame(columns=data_columns )

for i in range(4+i, len(ohlc)):
    data_dic = {}
    data_dic["change_positive"] = ohlc['change_positive'].ix[i]
    data_dic["change_negative"] = ohlc['change_negative'].ix[i]
    for j in range(1, num_predictors+1):
        data_dic["change_"+str(j)] = ohlc['Change(Open-Close)'].ix[i-j]
    
    training_test_data = training_test_data.append(
        data_dic,
        ignore_index=True
    )
    if i % 1000 == 0:
        print("{}".format(i))

training_test_data.head()


# In[272]:

predictors_tf = training_test_data[training_test_data.columns[2:]]

classes_tf = training_test_data[training_test_data.columns[:2]]

training_set_size = int(len(training_test_data) * 0.8)
test_set_size = len(training_test_data) - training_set_size

training_predictors_tf = predictors_tf[:training_set_size]
training_classes_tf = classes_tf[:training_set_size]

test_predictors_tf = predictors_tf[training_set_size:]
test_classes_tf = classes_tf[training_set_size:]

training_predictors_tf.head()


# In[274]:

#get_ipython().system(u'rm -rf tmp/tensorflow_log/*')

import tensorflow as tf
import numpy as np
import random


num_of_input_nodes = 1
num_of_hidden_nodes = 80
num_of_output_nodes = 1
num_of_training_epochs = 500000
batch_size = 100
num_of_prediction_epochs = 100
learning_rate = 0.001
forget_bias = 0.9
num_of_sample = 1000
num_layers = 1

batch_size = 100
sequences_length = num_predictors 
test_num = int(num_of_sample*0.3)
class_num = 2

def get_batch(batch_size, X, t):
    rnum = [random.randint(0, len(X) - 1) for x in range(batch_size)]
    xs = np.array([[[y] for y in list(X[r])] for r in rnum])
    ts = np.array([t[r] for r in rnum])
    return xs, ts


def create_batch(batch_size, X, t):
    X = X.as_matrix()
    t = t.as_matrix()
    rnum = [random.randint(0, len(X) - 1) for x in range(batch_size)]
    xs = np.array([[[y] for y in list(X[r])] for r in rnum])
    ts = np.array([t[r] for r in rnum])
    return xs, ts


def unpack_sequence(tensor):
    return tf.unpack(tf.transpose(tensor, perm=[1, 0, 2]))

def pack_sequence(sequence):
    return tf.transpose(tf.pack(sequence), perm=[1, 0, 2])

def inference(input_ph):
    with tf.name_scope("inference") as scope:
        in_size = num_of_hidden_nodes
        out_size = class_num
        weight = tf.Variable(tf.truncated_normal([in_size, out_size], stddev=0.1))
        bias = tf.Variable(tf.constant(0.1, shape=[out_size]))
        
       
        # network = tf.nn.rnn_cell.LSTMCell(num_of_hidden_nodes)
        network = tf.nn.rnn_cell.GRUCell(num_of_hidden_nodes)
        network = tf.nn.rnn_cell.DropoutWrapper(network, output_keep_prob=0.5)
        network = tf.nn.rnn_cell.MultiRNNCell([network] * num_layers)
        inputs =  unpack_sequence(input_ph)
        
        rnn_output, states_op = tf.nn.rnn(network,inputs,dtype=tf.float32)
        #rnn_output = pack_sequence(rnn_output)
        #state_op = pack_sequence(states_op)
        output_op = tf.nn.softmax(tf.matmul(rnn_output[-1], weight) + bias)

 
        tf.histogram_summary("weights", weight)
        tf.histogram_summary("biases", bias)
        tf.histogram_summary("output",  output_op)
        results = [weight, bias]
        return output_op, states_op, results


def loss(output_op, supervisor_ph):
    with tf.name_scope("loss") as scope:
        loss_op = - tf.reduce_sum(supervisor_ph * tf.log(output_op))
        tf.scalar_summary("loss", loss_op)
        return loss_op


def training(loss_op):
    with tf.name_scope("training") as scope:
        training_op = optimizer.minimize(loss_op)
        return training_op

def accuracy(output_op, supervisor_ph):
    with tf.name_scope("accuracy") as scope:
        correct_prediction = tf.equal(tf.argmax(output_op,1), tf.argmax(supervisor_ph,1))
        accuracy_op = tf.reduce_mean(tf.cast(correct_prediction, "float"))
        tf.scalar_summary("accuracy", accuracy_op)
        return accuracy_op

def calc_accuracy(accuracy_opp, X, t):
    inputs, targets = create_batch(len(X), X, t)
    pred_dict = {
        input_ph:  inputs,
        supervisor_ph: targets
    }
    accurecy = sess.run(accuracy_op, feed_dict=pred_dict)
    print(accurecy)



random.seed(0)
np.random.seed(0)
tf.set_random_seed(0)

#optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
optimizer = tf.train.AdadeltaOptimizer(learning_rate=learning_rate)

with tf.Graph().as_default():
    input_ph = tf.placeholder(tf.float32, [None, sequences_length, num_of_input_nodes], name="input")
    supervisor_ph = tf.placeholder(tf.float32, [None, class_num], name="supervisor")

    output_op, states_op, datas_op = inference(input_ph)
    loss_op = loss(output_op, supervisor_ph)
    training_op = training(loss_op)
    accuracy_op = accuracy(output_op, supervisor_ph)

    summary_op = tf.merge_all_summaries()
    init = tf.initialize_all_variables()

    with tf.Session() as sess:
        saver = tf.train.Saver()
        summary_writer = tf.train.SummaryWriter("tmp/tensorflow_log", graph=sess.graph)
        sess.run(init)

        for epoch in range(num_of_training_epochs):
            inputs, supervisors = create_batch(batch_size, training_predictors_tf , classes_tf[:training_set_size])
            train_dict = {
                input_ph:   inputs,
                supervisor_ph: supervisors
            }
            sess.run(training_op, feed_dict=train_dict)

            if (epoch) % 1000 == 0:
                summary_str, train_loss = sess.run([summary_op, loss_op], feed_dict=train_dict)
                print("train#{}, loss: {}".format(epoch, train_loss))
                summary_writer.add_summary(summary_str, epoch)
                if (epoch) % 5000 == 0:
                    calc_accuracy(output_op, test_predictors_tf, test_classes_tf)
        calc_accuracy(output_op, X_test, t_test)
        datas = sess.run(datas_op)
        saver.save(sess, "model.ckpt")


