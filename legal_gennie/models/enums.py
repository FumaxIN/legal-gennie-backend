from django.db.models import IntegerChoices


class LawyerTypeEnum(IntegerChoices):
    CORPORATE = 1
    CRIMINAL = 2
    FAMILY = 3
    TAX = 4
    IMMIAGRATION = 5
    INTELLECTUAL_PROPERTY = 6
    REAL_ESTATE = 7
    LABOUR = 8
    ENTERTAINMENT = 9
    GENERAL = 10