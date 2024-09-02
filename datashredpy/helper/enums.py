from enum import Enum

from aenum import Enum as AEnum, MultiValueEnum

class FileType(MultiValueEnum):
    CSV = 'csv'
    
    TXT = 'txt'

    TSV = 'tsv'