
class LogMsg:

    def __init__(self, status: int, category: str, msg: str):
        self.status = status
        self.category = category
        self.msg = msg

    def __str__(self) -> str:
        return "LogMsg(status={}, category={}, msg={}".format(self.status, self.category, self.msg)



