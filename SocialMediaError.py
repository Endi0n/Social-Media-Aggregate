class SocialMediaError(Exception):

	def __init__(self, code, message):
		self.__code = code
		self.__message = message

	@property
	def code(self):
		return self.__code
		
	@property
	def message(self):
		return self.__message
