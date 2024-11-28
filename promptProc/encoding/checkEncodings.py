import langdetect
import base64

class encodingChecker():
    def checkEncoding(self, data):
        # Check if the data is encoded
        if self.isBase64(data):
            return "Base64"
        elif self.isBase32(data):
            return "Base32"
        elif self.isBase16(data):
            return "Base16"
        elif self.isBase85(data):
            return "Base85"
        else:
            return "None"

    def isBase64(self, data):
        try:
            # Check if the data is base64 encoded
            base64.b64decode(data)
            return True
        except:
            return False

    def isBase32(self, data):
        try:
            # Check if the data is base32 encoded
            base64.b32decode(data)
            return True
        except:
            return False

    def isBase16(self, data):
        try:
            # Check if the data is base16 encoded
            base64.b16decode(data)
            return True
        except:
            return False

    def isBase85(self, data):
        try:
            # Check if the data is base85 encoded
            base64.b85decode(data)
            return True
        except:
            return False

    def checkLanguage(self, data):
        # Check the language of the data
        language = langdetect.detect(data)
        return language

