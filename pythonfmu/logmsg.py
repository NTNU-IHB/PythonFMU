
class LogMsg:

    def __init__(self, status: int, category: str, msg: str, debug: bool):
        '''Register a log message (during build process). Only used indirectly through fmi2slave.log()
        
        Args:
            status (int): message status. See also enums.Fmi2Status
            category (str or None) : Message category (normally derived from status)
            msg (str): the message text
            debug (bool) : signal whether this is a debug message
        '''
        self.status = status
        self.category = category
        self.msg = msg
        self.debug = debug

    def __str__(self) -> str:
        '''String representation of log message'''
        return "LogMsg(status={}, category={}, msg={}, debug={}".format(self.status, self.category, self.msg, self.debug)



