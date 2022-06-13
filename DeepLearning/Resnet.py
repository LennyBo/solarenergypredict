import tensorflow as tf
import tensorflow_addons as tfa
from keras import layers
import keras
from DataEngine import loadDFsToCrunch,Preprocessing
import matplotlib.pyplot as plt
import numpy as np

TEST_SIZE = 0.16 # Precent
VAL_SIZE = 360 # Days

batch_size = 64
num_epochs = 200


print("Loading dataset...")
df = loadDFsToCrunch()
print(f"Loaded {len(df)} rows\tStartDate: {df.index[0]}\tEndDate: {df.index[-1]}\n")

print("Preprocessing...")
x,y = Preprocessing(df)
print(f"Done preprocessing.\tX: {len(x)} shape:{x.shape}\tY: {len(y)}\n")

print(f"Splitting into train val and test with test size {TEST_SIZE * 100}%...")
length = len(y)
X_train, X_test, y_train, y_test = (
    x[0:int(length*(1-TEST_SIZE))],
    x[int(length*(1-TEST_SIZE)):],
    y[0:int(length*(1-TEST_SIZE))],
    y[int(length*(1-TEST_SIZE)):],
)
val_length = 360
length = len(y_train)

X_train, X_val, y_train, y_val = (
    X_train[0:length - val_length],
    X_train[length - val_length:],
    y_train[0:length - val_length],
    y_train[length - val_length:],
)

input_shape = X_train.shape[1:]

print(f"Done splitting.\tTrain: {len(X_train)}\tVal: {len(X_val)}\tTest: {len(X_test)}\n")

data_augmentation = keras.Sequential(
[
    layers.Normalization(),
    layers.Resizing(32, 32),
],
name="data_augmentation",
)

inner_model = tf.keras.applications.resnet50.ResNet50(
    include_top=False,
    weights='imagenet',
)

inner_model.trainable = False
model = keras.Sequential([
    keras.Input(shape=X_train[0].shape),
    data_augmentation,
    inner_model,
    layers.Flatten(),
    layers.Dense(200, activation='relu'),
    layers.Dense(100, activation='relu'),
    layers.Dense(50, activation='relu'),
    layers.Dense(10, activation='relu'),
    #Dense(50, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(1),
])

model.compile(
    optimizer="adam",
    loss=keras.losses.MeanSquaredError(reduction="auto", name="mean_squared_error"),
    metrics=[
        "mae",
    ],
)

callbacks = [keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)]

history = model.fit(
    x=X_train,
    y=y_train,
    batch_size=batch_size,
    epochs=num_epochs,
    validation_split=0.1,
    callbacks=callbacks,
)