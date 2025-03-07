# -*- coding: utf-8 -*-
"""Copy of 02 Image Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u_SdSrZVAvU1blZzUc5mXkNTyoZtMjSQ
"""



import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import random,os





"""# Define Constants"""

FAST_RUN = False
IMAGE_WIDTH=128
IMAGE_HEIGHT=128
IMAGE_SIZE=(IMAGE_WIDTH, IMAGE_HEIGHT)
IMAGE_CHANNELS=3

! unzip /content/ImageClassification.zip

"""# Prepare Traning Data"""

len(os.listdir('/content/ImageClassification/training')),len(os.listdir('/content/ImageClassification/testing'))

filenames = os.listdir("/content/ImageClassification/training")
categories = []
for filename in filenames:
    category = filename.split('.')[0]
    if category == 'cat':
        categories.append(1)
    else:
        categories.append(0)

df = pd.DataFrame({
    'filename': filenames,
    'category': categories
})

df.head()

df.tail()

df[df['category']==0]

df['category'].unique()

len([i for i in df['filename'].tolist() if 'cat' in i]) , len([i for i in df['filename'].tolist() if 'dog' in i])

"""### See Total In count"""

df['category'].value_counts().plot.bar()

"""From our data we have 12000 cats and 12000 dogs

# See sample image
"""

sample = random.choice(filenames)
image = load_img("/content/ImageClassification/training/"+sample)
plt.imshow(image)



"""# Build Model

<img src="https://i.imgur.com/ebkMGGu.jpg" width="100%"/>

* **Input Layer**: It represent input image data. It will reshape image into single diminsion array. Example your image is 64x64 = 4096, it will convert to (4096,1) array.
* **Conv Layer**: This layer will extract features from image.
* **Pooling Layer**: This layerreduce the spatial volume of input image after convolution.
* **Fully Connected Layer**: It connect the network from a layer to another layer
* **Output Layer**: It is the predicted values layer.
"""

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Activation, BatchNormalization

model = Sequential()

model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_CHANNELS)))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.25))
# 63*63*32
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.25))
# 30*30*64
# model.add(Conv2D(128, (3, 3), activation='relu'))
# model.add(BatchNormalization())
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.25))
# 14*14*128
model.add(Flatten())
model.add(Dense(512, activation='tanh'))
model.add(Dense(64, activation='sigmoid'))
model.add(Dense(2, activation='softmax'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

"""# Callbacks"""

from keras.callbacks import EarlyStopping, ReduceLROnPlateau

"""

**Early Stop**

To prevent over fitting we will stop the learning after 10 epochs and val_loss value not decreased"""

earlystop = EarlyStopping(patience=10)

"""**Learning Rate Reduction**

We will reduce the learning rate when then accuracy not increase for 2 steps
"""

learning_rate_reduction = ReduceLROnPlateau(monitor='val_acc',
                                            patience=2,
                                            verbose=1,
                                            factor=0.5,
                                            min_lr=0.00001)

# 0.01
# 0.005
# 0.01
# 0.005
# 0.0025
# 0.000125
# 0.0000000001

callbacks = [earlystop, learning_rate_reduction]

"""# Prepare data

Because we will use image genaretor `with class_mode="categorical"`. We need to convert column category into string. Then imagenerator will convert it one-hot encoding which is good for our classification.

So we will convert 1 to dog and 0 to cat
"""

df["category"] = df["category"].replace({1: 'cat', 0: 'dog'})

train_df, validate_df = train_test_split(df, test_size=0.20, random_state=42)
train_df = train_df.reset_index(drop=True)
validate_df = validate_df.reset_index(drop=True)

train_df['category'].value_counts().plot.bar()

validate_df['category'].value_counts().plot.bar()

total_train = train_df.shape[0]
total_validate = validate_df.shape[0]
batch_size=15

"""# Traning Generator"""

train_datagen = ImageDataGenerator(
    rotation_range=15,
    rescale=1./255,
    shear_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1
)

train_df

train_generator = train_datagen.flow_from_dataframe(
    train_df,
    "/content/ImageClassification/training",
    x_col='filename',
    y_col='category',
    target_size=IMAGE_SIZE,
    class_mode='categorical',
    batch_size=batch_size
)

"""### Validation Generator"""

validation_datagen = ImageDataGenerator(rescale=1./255)
validation_generator = validation_datagen.flow_from_dataframe(
    validate_df,
    "/content/ImageClassification/training",
    x_col='filename',
    y_col='category',
    target_size=IMAGE_SIZE,
    class_mode='categorical',
    batch_size=batch_size
)

"""# See how our generator work"""

example_df = train_df.sample(n=1).reset_index(drop=True)
example_generator = train_datagen.flow_from_dataframe(
    example_df,
    "/content/ImageClassification/training",
    x_col='filename',
    y_col='category',
    target_size=IMAGE_SIZE,
    class_mode='categorical'
)

plt.figure(figsize=(12, 12))
for i in range(0, 15):
    plt.subplot(5, 3, i+1)
    for X_batch, Y_batch in example_generator:
        image = X_batch[0]
        plt.imshow(image)
        break
plt.tight_layout()
plt.show()

"""Seem to be nice

# Fit Model
"""

import warnings
from warnings import filterwarnings
filterwarnings('ignore')

epochs=20
history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=total_validate//batch_size,
    steps_per_epoch=total_train//batch_size,
    callbacks=callbacks
)

"""# Save Model"""

model.save_weights('model.weights.h5')

"""# Virtualize Training"""

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
ax1.plot(history.history['loss'], color='b', label="Training loss")
ax1.plot(history.history['val_loss'], color='r', label="validation loss")
ax1.set_xticks(np.arange(1, epochs, 1))
ax1.set_yticks(np.arange(0, 1, 0.1))

ax2.plot(history.history['accuracy'], color='b', label="Training accuracy")
ax2.plot(history.history['val_accuracy'], color='r',label="Validation accuracy")
ax2.set_xticks(np.arange(1, epochs, 1))

legend = plt.legend(loc='best', shadow=True)
plt.tight_layout()
plt.show()

"""# Prepare Testing Data"""

test_filenames = os.listdir("/content/ImageClassification/testing")
test_df = pd.DataFrame({
    'filename': test_filenames
})
nb_samples = test_df.shape[0]
nb_samples



"""# Create Testing Generator"""

test_gen = ImageDataGenerator(rescale=1./255)
test_generator = test_gen.flow_from_dataframe(
    test_df,
    "/content/ImageClassification/testing",
    x_col='filename',
    y_col=None,
    class_mode=None,
    target_size=IMAGE_SIZE,
    batch_size=batch_size,
    shuffle=False
)

"""# Predict"""

predict = model.predict(test_generator, steps=int(np.ceil(nb_samples/batch_size)))

"""For categoral classication the prediction will come with probability of each category. So we will pick the category that have the highest probability with numpy average max"""

test_df['category'] = np.argmax(predict, axis=-1)

"""We will convert the predict category back into our generator classes by using `train_generator.class_indices`. It is the classes that image generator map while converting data into computer vision"""

test_df['category']

test_df['category'].value_counts()

label_map = dict((v,k) for k,v in train_generator.class_indices.items())
test_df['category'] = test_df['category'].replace(label_map)
test_df['category'].value_counts()

"""From our prepare data part. We map data with `{1: 'dog', 0: 'cat'}`. Now we will map the result back to dog is 1 and cat is 0"""

test_df['label'] = test_df['filename'].apply(lambda x : 'cat' if 'cat' in x else 'dog')

test_df

test_df['label'].value_counts()

"""### Virtaulize Result"""

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

CM = confusion_matrix(test_df['label'], test_df['category'])
print('Confusion Matrix is : \n', CM)

# drawing confusion matrix
sns.heatmap(CM, center = True,cmap='Blues_r')
plt.show()

