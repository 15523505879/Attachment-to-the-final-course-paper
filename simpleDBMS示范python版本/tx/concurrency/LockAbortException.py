class LockAbortException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "simpleDBMS示范python版本.tx.concurrency.LockAbortException"
