





class CommonException(Exception):
    def __init__(self,code,msg):
        self.error=msg
        self.code=code
