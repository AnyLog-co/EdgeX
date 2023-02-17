import base64
import json
import numpy as np

# https://stackoverflow.com/questions/3488934/simplejson-and-numpy-array/24375113#24375113
class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict
        holding dtype, shape and the data
        """
        if isinstance(obj, np.ndarray):
            obj_data = np.ascontiguousarray(obj).data
            data_list = obj_data.tolist()
            return dict(__ndarray__=data_list,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        super(NumpyEncoder, self).default(obj)

class NumpyEncoderBase64(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict
        holding dtype, shape and the data
        """
        if isinstance(obj, np.ndarray):
            obj_data = np.ascontiguousarray(obj).data
            data_list = base64.b64encode(obj_data)
            if isinstance(data_list, bytes):
                data_list = data_list.decode(encoding='UTF-8')
            return dict(__ndarray__=data_list,
                        dtype=str(obj.dtype),
                        shape=obj.shape)

        # Let the base class default method raise the TypeError
        super(NumpyEncoderBase64, self).default(obj)
