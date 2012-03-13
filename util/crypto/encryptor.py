from ConcurrenTree.model import ModelBase

class Encryptor(ModelBase):
	def encrypt(self, s):
		raise NotImplementedError("Encryptor must define 'encrypt'")

	def decrypt(self, s):
		raise NotImplementedError("Encryptor must define 'decrypt'")

class Flip(Encryptor):
	def __init__(self, parent):
		self.encrypt = parent.decrypt
		self.decrypt = parent.encrypt

def make(data):
	if type(data) in (str, unicode):
		import json
		data = json.loads(data)
	t = data[0]
	args = data[1:]
	if t=="rotate":
		import rotate
		return rotate.RotateEncryptor(*args)
	elif t=="aes":
		import aes
		return aes.AESEncryptor(*args)
	elif t=="rsa":
		import rsa
		return rsa.RSA(*args)

