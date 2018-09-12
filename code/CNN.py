# CNN卷积神经网络
import tensorflow as tf
import numpy as np
import os

train_path = 'J:/study/tensorflow_learnning/data/'
class_list = ['0','1','2','3','4','5','6','7','8','9']

def get_data(file_dir,batch_size,n_classes):
    imge_paths = []
    labels = []
    for n in range(len(class_list)):
        sub_files = os.listdir(file_dir  + class_list[n])
        for m in range(len(sub_files)):
            imge_paths.append(file_dir  + class_list[n]+'/'+sub_files[m])
            labels.append(n)
    print(imge_paths)
    print(labels)

    paths_lt = tf.cast(imge_paths, tf.string)
    labels_lt = tf.cast(labels, tf.int32)
    paths_list,label_list = tf.train.slice_input_producer([paths_lt,labels_lt])

    print(paths_list)
    print(label_list)
    images1 = tf.read_file(paths_list)
    print(images1)
    images_decode = tf.image.decode_png(images1, channels=1)
    #images_decode = tf.image.decode_bmp(images1, channels=3)
    images_resize = tf.image.resize_image_with_crop_or_pad(images_decode, 28, 28)
    images_standardization = tf.image.per_image_standardization(images_resize)
    #print(images_standardization)
    images_batch,labels_batch = tf.train.batch([images_standardization,label_list],batch_size=batch_size,num_threads=64,
                                                       capacity=512)
    images_batch = tf.cast(images_batch, tf.float32)
    labels_batch = tf.one_hot(labels_batch,depth=n_classes)
    labels_batch = tf.reshape(labels_batch, [batch_size, n_classes])
    #print(labels_batch)
    return images_batch,labels_batch



# 模型构建函数
def weights(shape):
    return tf.Variable(tf.truncated_normal(shape,stddev=0.01))

def baise(shape):
    return tf.Variable(tf.constant(0.1, shape=shape))

def conv2d(x,w):
    out = tf.nn.conv2d(x,w,strides=[1,1,1,1],padding="SAME")
    return out

def max_pool_2x2(x):
    out = tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding="SAME")
    return out
def cnn(x):
    # 2，cnn模型构建，变量定义

    #layer1
    weigh1 = weights([5,5,1,32])
    bas_1 = baise([32])
    conv2_1 = tf.nn.relu(conv2d(x,weigh1)+bas_1)         # 28*28*32
    max_pool_1 = max_pool_2x2(conv2_1) #out 14*14*32


    #layer2
    weight2 = weights([5,5,32,64])
    bas_2 = baise([64])
    conv2_2 = tf.nn.relu(conv2d(max_pool_1,weight2)+bas_2)  #14*14*64
    max_pool_2 = max_pool_2x2(conv2_2)  # 7*7*64


    #layer_f
    w_f = weights([7*7*64,1024])
    b_f = baise([1024])
    f_in = tf.reshape(max_pool_2,[-1,7*7*64])
   # f_drop = tf.nn.dropout(f_in,0.5)
    f_out = tf.nn.relu(tf.matmul(f_in,w_f)+b_f)

    #layer_f_2
    w_f_2 = weights([1024,10])
    b_f_2 = baise([10])
    y_pre = tf.nn.softmax(tf.matmul(f_out,w_f_2)+b_f_2)

    return y_pre


# 1,数据准备

images,labels = get_data(train_path,100,10)
ckpt_path = './ckpt/test-model.ckpt'


# 3，构建损失函数及选择优化器

y_pre = cnn(images)

#cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=y_pre, labels=labels,name='cross-entropy')
#loss = tf.reduce_mean(cross_entropy, name='loss')
#train_op = tf.train.AdamOptimizer(1e-4).minimize(loss)

loss = tf.reduce_mean(-tf.reduce_sum(labels * tf.log(y_pre),reduction_indices=[1]))       # loss
train_op = tf.train.AdamOptimizer(1e-4).minimize(loss)
#train_op = tf.train.GradientDescentOptimizer(1e-4).minimize(loss)

correct = tf.equal(tf.argmax(y_pre, 1), tf.argmax(labels, 1))
correct = tf.cast(correct, tf.float32)
accuracy = tf.reduce_mean(correct) * 100.0

# 4，启动会话，初始化变量，训练
sess = tf.Session()
init = tf.global_variables_initializer()

save = tf.train.Saver()
coord = tf.train.Coordinator()
threads = tf.train.start_queue_runners(sess=sess, coord=coord)
sess.run(init)

for step in range(2000):
    sess.run(train_op)
    if step % 50 == 0:
        print(sess.run(loss),":",sess.run(accuracy))
       #print(sess.run(images).shape)
        save.save(sess,ckpt_path)

coord.request_stop()
coord.join(threads)