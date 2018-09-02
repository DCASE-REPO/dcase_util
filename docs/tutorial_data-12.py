import dcase_util
manyhot_encoder = dcase_util.data.ManyHotEncoder(label_list=['class A','class B','class C'], time_resolution=0.02)
binary_matrix = manyhot_encoder.encode(label_list=['class A', 'class B'], length_seconds=10.0)
binary_matrix.plot()