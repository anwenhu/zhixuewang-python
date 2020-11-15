import datetime


def timestamp2datetime(timestamp: float) -> datetime.datetime:
    return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)


def get_property(arg_name: str) -> property:
    def setter(self, mill_timestamp):
        self.__dict__[arg_name] = timestamp2datetime(mill_timestamp / 1000)

    return property(fget=lambda self: self.__dict__[arg_name],
                    fset=setter)
