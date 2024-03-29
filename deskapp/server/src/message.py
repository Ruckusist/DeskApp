import sys, math, lzma, base64  # pickle
import _pickle as cPickle
# from cryptography.fernet import Fernet


class Message(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Message, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delitem__(self, key):
        super(Message, self).__delitem__(key)
        del self.__dict__[key]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)
 
    def pad(self):
        pad = "$"
        org_size = (sys.getsizeof(self.file) / 1024) / 1024
        needed_size = ((math.ceil(org_size) - org_size)*1024)*1024
        single_pad_size = sys.getsizeof(pad)
        print(f"single_pad_size: {single_pad_size} needed_size: {needed_size}")
        self.pad = pad * (int(needed_size / single_pad_size))
        pad_size = sys.getsizeof(self.pad)
        print(f"added {pad_size:.1f}")
        
    def serialize(self):
        org_size = (sys.getsizeof(self.file) / 1024) / 1024
        # print(f"Data Size: {org_size:.3f} mb")
        # PICKLE
        pdata = cPickle.dumps(self)
        p_size = (sys.getsizeof(pdata) / 1024) / 1024
        # print(f"Pickle Size: {p_size:.3f} mb")
        # lzma
        cdata = lzma.compress(pdata)
        c_size = (sys.getsizeof(cdata) / 1024) / 1024
        saved = ((org_size / c_size)-1)*100
        # print(f"Compressed Size: {c_size:.3f} mb  saved: {saved:.2f}%")
        # base 64 encode
        b64data = base64.b64encode(cdata)
        b64_size = (sys.getsizeof(b64data) / 1024) / 1024
        # print(f"B64 Size: {b64_size:.3f} mb | base 64 should be 33% larger filesize. actual: {(b64_size/c_size)-1:.2f}")
        # encrypt
        if not self.get('key', 0):
            return b64data
        obj = Fernet(self.key)
        edata = obj.encrypt(b64data)
        edata_size = (sys.getsizeof(edata) / 1024) / 1024
        # print(f"Encrypted Size: {edata_size:.3f} mb")
        return edata
        
    @staticmethod
    def deserialize(edata, key=None):
        # decrypt
        if key:
            edata_size = (sys.getsizeof(edata) / 1024) / 1024
            # print(f"Encrypted Size: {edata_size:.3f} mb")
            obj = Fernet(key)
            b64data = obj.decrypt(edata)
        else:
            b64data = edata
        b64data_size = (sys.getsizeof(b64data) / 1024) / 1024
        # print(f"B64 Size: {b64data_size:.3f} mb")
        cdata = base64.b64decode(b64data)
        c_size = (sys.getsizeof(cdata) / 1024) / 1024
        # print(f"Compressed Size: {c_size:.3f} mb")
        pdata = lzma.decompress(cdata)
        pdata_size = (sys.getsizeof(pdata) / 1024) / 1024
        # print(f"Pickle Size: {pdata_size:.3f} mb")
        data = cPickle.loads(pdata)
        data_size = (sys.getsizeof(data.file) / 1024) / 1024
        # print(f"Actual Size: {data_size:.3f} mb")
        return data