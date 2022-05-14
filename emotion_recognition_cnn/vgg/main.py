# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
from keras.layers import Input, Lambda, Dense, Flatten
from keras.models import Model
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.metrics import confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
from skimage.io import imread, imshow


IMSIZE = [100, 100]
# IMSIZE = [48, 48]
# IMSIZE = [224, 224]

NBCLASSES = 7

src_path_train = "fruits-360_dataset/fruits-360/Training"
src_path_train = "FER-2013/train"
src_path_test = "fruits-360_dataset/fruits-360/Test"
src_path_test = "FER-2013/test"

image_gen = ImageDataGenerator(
    rescale=1 / 255.0,
    rotation_range=20,
    zoom_range=0.05,
    width_shift_range=0.05,
    height_shift_range=0.05,
    shear_range=0.05,
    horizontal_flip=True,
    fill_mode="nearest",
    validation_split=0.20,
)

batch_size = 32

# create generators
train_generator = image_gen.flow_from_directory(
    src_path_train,
    target_size=IMSIZE,
    shuffle=True,
    batch_size=batch_size,
)

test_generator = image_gen.flow_from_directory(
    src_path_test,
    target_size=IMSIZE,
    shuffle=True,
    batch_size=batch_size,
)

from glob import glob

train_image_files = glob(src_path_train + "/*/*.jp*g")
test_image_files = glob(src_path_test + "/*/*.jp*g")
# len(image_files), len(valid_image_files)


def create_model():
    vgg = VGG16(
        input_shape=IMSIZE + [3],
        weights="vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5",
        include_top=False,
    )

    # Freeze existing VGG already trained weights
    for layer in vgg.layers:
        layer.trainable = False

    # get the VGG output
    out = vgg.output

    # Add new dense layer at the end
    x = Flatten()(out)
    x = Dense(NBCLASSES, activation="softmax")(x)

    model = Model(inputs=vgg.input, outputs=x)

    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

    model.summary()

    return model


mymodel = create_model()

epochs = 10
early_stop = EarlyStopping(monitor="val_loss", patience=2)
r = mymodel.fit_generator(
    train_generator,
    validation_data=test_generator,
    epochs=epochs,
    steps_per_epoch=len(train_image_files) // batch_size,
    validation_steps=len(test_image_files) // batch_size,
    callbacks=[early_stop],
)

score = mymodel.evaluate_generator(test_generator)
print("Test loss:", score[0])
print("Test accuracy:", score[1])

mymodel.save("vggSavedModel")
