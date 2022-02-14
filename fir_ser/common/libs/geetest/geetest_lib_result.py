# sdk lib包的返回结果信息。
class GeetestLibResult:

    def __init__(self):
        self.status = 0  # 成功失败的标识码，1表示成功，0表示失败
        self.data = ''  # 返回数据，json格式
        self.msg = ''  # 备注信息，如异常信息等

    def set_all(self, status, data, msg):
        self.status = status
        self.data = data
        self.msg = msg

    def __str__(self):
        return "GeetestLibResult{{status={0}, data={1}, msg={2}}}".format(self.status, self.data, self.msg)
