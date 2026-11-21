import pickle

load = pickle.load

SAFE_MODULES = {
    "collections": {"OrderedDict"},
    "torch": {
        "HalfStorage", "FloatStorage", "DoubleStorage", "ByteStorage",
        "CharStorage", "ShortStorage", "IntStorage", "LongStorage",
        "BoolStorage", "BFloat16Storage", "ComplexFloatStorage",
        "ComplexDoubleStorage", "QUInt8Storage", "QInt8Storage",
        "QInt32Storage", "Size", "device", "dtype",
    },
    "torch._utils": {
        "_rebuild_tensor", "_rebuild_tensor_v2", "_rebuild_tensor_v3",
        "_rebuild_parameter", "_rebuild_qtensor",
    },
    "torch.nn.parameter": {"Parameter"},
    "numpy": {"dtype", "ndarray"},
    "numpy.core.multiarray": {"scalar", "_reconstruct"},
    "builtins": {"set", "frozenset", "slice", "complex", "bytearray"},
}


class Empty:
    pass


class Unpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module.startswith("pytorch_lightning"):
            return Empty
        if module in SAFE_MODULES and name in SAFE_MODULES[module]:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Unsafe global '{module}.{name}' is forbidden during checkpoint loading.")
