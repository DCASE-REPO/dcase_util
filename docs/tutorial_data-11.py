import dcase_util
onehot_encoder = dcase_util.data.OneHotEncoder(label_list=['class A','class B','class C'], time_resolution=0.02)
binary_matrix = onehot_encoder.encode(label='class B', length_seconds=10.0)
binary_matrix.plot()