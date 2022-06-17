import tensorflow as tf

model_to_convert = "./models/VisualCrossing_LSTM_model.h5"

model = tf.keras.models.load_model(model_to_convert)

converter = tf.lite.TFLiteConverter.from_keras_model(model)

converter.target_spec.supported_ops = [
  tf.lite.OpsSet.TFLITE_BUILTINS, # enable TensorFlow Lite ops.
  tf.lite.OpsSet.SELECT_TF_OPS, # enable TensorFlow ops.
]

tflite_model = converter.convert()
open(model_to_convert + ".tflite", "wb").write(tflite_model)