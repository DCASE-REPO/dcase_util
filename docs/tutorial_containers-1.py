import dcase_util
import numpy
data_container = dcase_util.containers.DataMatrix2DContainer(
  data=numpy.random.rand(10,100),
  time_resolution=0.02
)
data_container.plot()