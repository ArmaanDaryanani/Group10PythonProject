"""
* Project 10, ENGR1110
* Neural Processing File
* Last Updated 10/19/23
"""
import tensorflow as tf
import matplotlib.pyplot as plt

#get data and splits it into training and testing datasets
#The first section trains the NN on data its seen before, and the 2nd section trains it on data it hasnt seen before
(train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

#scales down pixel values from 0-255 to 0-1 so our NN can parse it easily
train_images = train_images / 255.0
test_images = test_images / 255.0

#visualizes the data
print(train_images.shape)
print(test_images.shape)
print(train_labels)

#display the first image
plt.imshow(train_images[0], cmap='gray')
plt.show()
#if you observe the output, you will see something like this for the first one:
#training set: (60000, 28, 28), 60000 images total (has seen), 28x28 pixels
#testing set: (10000, 28, 28), 10000 images total (never seen), 28x28 pixels

#defines the neural netowrk model
#using the easiest neural network model by stacking neural network layers on top of eachother (sequential)
my_model = tf.keras.models.Sequential()

"""1st layer"""
#flattens the 28x28 layer of pixels into a single line of pixels so we can feed them to the neural network in the most simple way possible (1 line at a time)
my_model.add(tf.keras.layers.Flatten(input_shape=(28,28))) #adds layers sequentially

"""2nd layer"""
#dense layer which receives input from all the neurons of the previous layer (dense)
#smaller networks use less memory and run faster
#activation: decides whether a neuron should be activated or not. Outputs a small value for small inputs and larger values of inputs exceed a threshold
#relu activation is one of the most computationally effective activation functions
#128 is the number of neurons
my_model.add(tf.keras.layers.Dense(128, activation='relu'))

"""3rd layer"""
#10 is the number of neurons, should match the number of classifications we have (0-9, so 10)
#multiclass classifications, so softmax function is used, which turns values into probabilistic range we can interpret (ex: outputs 0.70 (70%) if it thinks an image is a "5" or something)
my_model.add(tf.keras.layers.Dense(10, activation='softmax'))

"""compile"""
#compile the model and optimizes it using the adam optimizer (common)
#multiclass classification, so loss= sparse_categorical_crossentropy
#you can experiment each for performance
#metrics we want to track: accuracy of this model (for testing/debug)
my_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

"""training"""
#once we create and compile the neural network, lets feed it with our own data and what they should be
#we are training it 3 times, (3*60000)
#if we have epochs too high, it might be prone to overfitting, where the NN starts to memorize parts of the images (not generalizable and bad)
my_model.fit(train_images, train_labels, epochs=3)

"""testing"""
#lets see how well it does with 10000 of unseen data
#takes a guess on whats it thinks is the number
val_loss, val_acc = my_model.evaluate(test_images, test_labels)
print('Test accuracy: ', val_acc)
#if there is a large difference between training accuracy and testing accuracy (ex: 70% training, 97% testing) it could be a sign of overfitting


"""saving the model"""
my_model.save('my_mnist_model') #saved under this folder

"""loading the model from the file"""
my_new_model = tf.keras.models.load_model('my_mnist_model')
#check for performance so it gives us the exact same result
new_val_loss, new_val_acc = my_new_model.evaluate(test_images, test_labels)
print("New testing accuracy: ", new_val_acc)





