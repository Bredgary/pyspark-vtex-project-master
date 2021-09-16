#!/usr/bin/env python3

from collections import OrderedDict
import json
import logging
import re
import sys


FIELD_MATCHER = re.compile(r'(^[^a-zA-Z])')

line_number = 0


def normalize_file(file):
    global line_number
    for line in file:
        line_number += 1
        json_object = json.loads(line)

        if not isinstance(json_object, dict):
            logging.error('%s: Top level record must be a dict but was a %s',
                         line_number, type(json_object))
            continue

        try:
            normalized_dict = normalize_dict(json_object)
        except Exception as e:
            logging.error('%s: %s', line_number, e)
            continue
        json.dump(normalized_dict, sys.stdout)
        print()
    logging.info("Processed %s lines", line_number)


def normalize_dict(json_dict):
    normalized_dict = OrderedDict()
    for key, value in json_dict.items():
        key = FIELD_MATCHER.sub('_', key)
        if isinstance(value, dict):
            value = normalize_dict(value)
        normalized_dict[key] = value
    return normalized_dict


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    normalize_file(sys.stdin)
