class System_Information:
	
	default_version = 1000

	def systemSettings(self):
		return [self.default_version]

	def getVersion(self):
		return self.default_version