from enum import IntEnum, EnumMeta


class WeekdayEnum(EnumMeta):
    def __call__(cls, value, *args, **kw):
        if isinstance(value, str):
            if value.lower() in ("monday", "mon", "mo", "m",):
                value = 0
            elif value.lower() in ("tuesday", "tue", "tu", "t"):
                value = 1
            elif value.lower() in ("wednesday", "wed", "we", "w"):
                value = 2
            elif value.lower() in ("thursday", "thu", "th", "r"):
                value = 3
            elif value.lower() in ("friday", "fri", "fr", "f"):
                value = 4
            elif value.lower() in ("saturday", "sat", "sa", "s"):
                value = 5
            elif value.lower() in ("sunday", "sun", "su", "u"):
                value = 6
        return super().__call__(value, *args, **kw)


class Weekday(IntEnum, metaclass=WeekdayEnum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6
    NoneDay = 7

    def to_ical(self):
        if self.value == 0:
            return "MO"
        elif self.value == 1:
            return "TU"
        elif self.value == 2:
            return "WE"
        elif self.value == 3:
            return "TH"
        elif self.value == 4:
            return "FR"
        elif self.value == 5:
            return "SA"
        elif self.value == 6:
            return "SU"
        elif self.value == 7:
            return "NA"
