import numpy as np

# Convert inaccessible types from objects to json types.
def convert_np_int_to_int(data):
        if isinstance(data, dict):
            return {_int: convert_np_int_to_int(_numpyInt) for _int , _numpyInt in data.items()}
        elif isinstance(data, list):
            return [convert_np_int_to_int(_numpyInt) for _numpyInt in data]
        elif isinstance(data, (np.int64, np.int32, np.intc)):
            return int(data)
        else:
            return data