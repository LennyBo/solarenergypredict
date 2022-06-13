import tensorflow as tf
import tensorflow_addons as tfa
from keras import layers
import keras
from DataEngine import loadDFsToCrunch,Preprocessing
import matplotlib.pyplot as plt
import numpy as np

def mlp(x, hidden_units, dropout_rate):
    for units in hidden_units:
        x = layers.Dense(units, activation=tf.nn.gelu)(x)
        x = layers.Dropout(dropout_rate)(x)
    return x

class Patches(layers.Layer):
    def __init__(self, patch_size):
        super(Patches, self).__init__()
        self.patch_size = patch_size

    def call(self, images):
        batch_size = tf.shape(images)[0]
        patches = tf.image.extract_patches(
            images=images,
            sizes=[1, self.patch_size, self.patch_size, 1],
            strides=[1, self.patch_size, self.patch_size, 1],
            rates=[1, 1, 1, 1],
            padding="VALID",
        )
        patch_dims = patches.shape[-1]
        patches = tf.reshape(patches, [batch_size, -1, patch_dims])
        return patches

class PatchEncoder(layers.Layer):
    def __init__(self, num_patches, projection_dim):
        super(PatchEncoder, self).__init__()
        self.num_patches = num_patches
        self.projection = layers.Dense(units=projection_dim)
        self.position_embedding = layers.Embedding(
            input_dim=num_patches, output_dim=projection_dim
        )

    def call(self, patch):
        positions = tf.range(start=0, limit=self.num_patches, delta=1)
        encoded = self.projection(patch) + self.position_embedding(positions)
        return encoded
    

def create_vit_classifier():
    inputs = layers.Input(shape=input_shape)
    # Augment data.
    augmented = data_augmentation(inputs)
    # Create patches.
    patches = Patches(patch_size)(augmented)
    # Encode patches.
    encoded_patches = PatchEncoder(num_patches, projection_dim)(patches)

    # Create multiple layers of the Transformer block.
    for _ in range(transformer_layers):
        # Layer normalization 1.
        x1 = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
        # Create a multi-head attention layer.
        attention_output = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=projection_dim, dropout=0.1
        )(x1, x1)
        # Skip connection 1.
        x2 = layers.Add()([attention_output, encoded_patches])
        # Layer normalization 2.
        x3 = layers.LayerNormalization(epsilon=1e-6)(x2)
        # MLP.
        x3 = mlp(x3, hidden_units=transformer_units, dropout_rate=0.1)
        # Skip connection 2.
        encoded_patches = layers.Add()([x3, x2])

    # Create a [batch_size, projection_dim] tensor.
    representation = layers.LayerNormalization(epsilon=1e-6)(encoded_patches)
    representation = layers.Flatten()(representation)
    representation = layers.Dropout(0.5)(representation)
    # Add MLP.
    features = mlp(representation, hidden_units=mlp_head_units, dropout_rate=0.1)
    # Classify outputs.
    logits = layers.Dense(1)(features)
    # Create the Keras model.
    model = keras.Model(inputs=inputs, outputs=logits)
    return model

def run_experiment(model):
    optimizer = tfa.optimizers.AdamW(
        learning_rate=learning_rate, weight_decay=weight_decay
    )

    model.compile(
        optimizer=optimizer,
        loss=keras.losses.MeanSquaredError(reduction="auto", name="mean_squared_error"),
        metrics=[
            "mae",
        ],
    )
    
    callbacks = [keras.callbacks.EarlyStopping(patience=50, restore_best_weights=True)]
    
    history = model.fit(
        x=X_train,
        y=y_train,
        batch_size=batch_size,
        epochs=num_epochs,
        validation_split=0.1,
        callbacks=callbacks,
    )

    score = model.evaluate(X_test, y_test, verbose=0)

    roundDecimal = 2
    print("\n\nTest results:")
    print('Mean absolute error:', round(score[1], roundDecimal))
    print('Mean squared error :', round(score[0], roundDecimal))

    return history


TEST_SIZE = 0.16 # Precent
VAL_SIZE = 360 # Days

learning_rate = 0.001
weight_decay = 0.0001
batch_size = 64
num_epochs = 200
image_size = 72  # We'll resize input images to this size
patch_size = 6  # Size of the patches to be extract from the input images
num_patches = (image_size // patch_size) ** 2
projection_dim = 64
num_heads = 4
transformer_units = [
    projection_dim * 2,
    projection_dim,
]  # Size of the transformer layers
transformer_layers = 10
mlp_head_units = [200, 100,50,10]  # Size of the dense layers of the final classifier


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
    layers.Resizing(image_size, image_size),
],
name="data_augmentation",
)
# Compute the mean and the variance of the training data for normalization.
data_augmentation.layers[0].adapt(X_train)

plt.figure(figsize=(4, 4))
image = X_train[np.random.choice(range(X_train.shape[0]))]
plt.imshow(image.astype("uint8"))
plt.axis("off")

resized_image = tf.image.resize(
    tf.convert_to_tensor([image]), size=(image_size, image_size)
)
patches = Patches(patch_size)(resized_image)
print(f"Image size: {image_size} X {image_size}")
print(f"Patch size: {patch_size} X {patch_size}")
print(f"Patches per image: {patches.shape[1]}")
print(f"Elements per patch: {patches.shape[-1]}")

n = int(np.sqrt(patches.shape[1]))
plt.figure(figsize=(4, 4))
for i, patch in enumerate(patches[0]):
    ax = plt.subplot(n, n, i + 1)
    patch_img = tf.reshape(patch, (patch_size, patch_size, 1))
    plt.imshow(patch_img.numpy().astype("uint8"))
    plt.axis("off")
    

optimizer = tfa.optimizers.AdamW(
    learning_rate=learning_rate, weight_decay=weight_decay
)

vit_classifier = create_vit_classifier()
history = run_experiment(vit_classifier)


    

