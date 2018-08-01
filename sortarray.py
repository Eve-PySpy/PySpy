# !/usr/local/bin/python3.6
# MIT licensed
# Copyright (c) 2018 White Russsian
# Github: <https://github.com/WhiteRusssian/PySpy>**********************
'''SortArray() provides functionality to sort an array (list of lists
or tuples) containing string or numeric values (or a mix thereof).
Ability to sort by two "columns", to break a tie in the primary sort
column. Can be case sensitive.
'''
# cSpell Checker - Correct Words****************************************
# // cSpell:words russsian
# **********************************************************************


class SortArrayError(Exception):
    '''
    Base exception for any exceptions raised by SortArray.
    '''
    def __init__(self, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "SortArray encountered a problem and stopped."
        super(SortArrayError, self).__init__(msg)


class OutOfBoundError(SortArrayError):
    '''
    Gets raised when `prim_col` is greater than the last column in `array`.
    '''
    def __init__(self, prim_col, sort_array):
        prim_col = prim_col
        array_columns = len(sort_array[0])
        msg = (
            "Sort column index (%s) exceeds number of columns in the unsorted input array (%s)." % (prim_col, array_columns)
            )
        super(SortArrayError, self).__init__(msg)


class NothingToSortError(SortArrayError):
    '''
    Gets raised when there are less than two sortable objects.
    '''
    def __init__(self):
        msg = (
            "The unsorted input array does not contain sufficient sortable values."
            )
        super(SortArrayError, self).__init__(msg)


def _determineApproach(array, sort_col):
    '''
    Takes an array (list of lists/tuples) and determines whether values
    in a given column should be sorted as numbers or strings. Returns
    a boolean which is True if column should be sorted as string and
    False if to be sorted as float.

    :param `array`: A list of list or tuples.

    :param `sort_col`: The number of the sort column as integer.

    :return: Boolean indicating if sort type is string (True) or float
    (False).
    '''

    if sort_col > len(array[0]):
        raise OutOfBoundError(sort_col, array)

    # Check type of each element to be sorted_list
    is_num = is_str = is_other = is_none = 0
    for r in array:
        if isinstance(r[sort_col], (int, float)):
            is_num += 1
        elif isinstance(r[sort_col], str):
            try:
                float(r[sort_col])
                is_num += 1
            except ValueError:
                is_str += 1
        elif r[sort_col] is None:
            is_none += 1
        else:
            is_other += 1

    # Make sure all elements are sortable, if not return TypeError
    if is_other > 0:
        raise TypeError

    # If any element is not or cannot be converted to a number,
    # treat all elements as string.
    elif is_str > 0:
        sort_as_str = True
    else:
        sort_as_str = False

    # If there is nothing to sort, raise error.
    if (is_num + is_str + is_none) < 2:
        raise NothingToSortError

    return sort_as_str


def sort_array(array, prim_col, sec_col=None, prim_desc=False, sec_desc=False, case_sensitive=False):
    '''
    Take an array (list of lists/tuples) with numeric or text values (or
    mix of both) and sort it by a primary column and optionally by a
    secondary column. It is tollerant to None values.

    :param `array`: List of lists or tuples containing strings
    or numbers.

    :param `prim_col`: Index (integer) of primary sort column.

    :param `sec_col`: Index (integer) of secondary sort column.

    :param `prim_desc`: Boolean indicating sort order of primary sort
    column(`True` for descending `False` for ascending)

    :param `sec_desc`: Boolean indicating sort order of secondary sort
    column(`True` for descending `False` for ascending)

    :param `case_sensitive`: Boolean set to True if cases matters.

    :return: The sorted array as list of tuples.
    '''

    # Determine if we need to convert values to str or float
    prim_is_str = _determineApproach(array, prim_col)
    if sec_col is not None and sec_col != prim_col:
        sec_is_str = _determineApproach(array, sec_col)
    else:
        sec_col = None

    # We mke use of the fact that sorted() is stable and first sort by
    # the secondary sort column, if any, and then by the primary.

    # Secondary  Sort --------------------------------------------------
    if sec_col is not None:
        if sec_is_str and case_sensitive:
            sorted_array = sorted(
                array,
                key=lambda r: str(r[sec_col]) if r[sec_col] is not None else "",
                reverse=sec_desc
                )
        elif sec_is_str and not case_sensitive:
            sorted_array = sorted(
                array,
                key=lambda r: str(r[sec_col]).lower() if r[sec_col] is not None else "",
                reverse=sec_desc
                )
        else:
            sorted_array = sorted(
                array,
                key=lambda r: float(r[sec_col]) if r[sec_col] is not None else float("-inf"),
                reverse=sec_desc
                )
        array = sorted_array

    # Primary Sort -----------------------------------------------------
    if prim_is_str and case_sensitive:
        sorted_array = sorted(
            array,
            key=lambda r: str(r[prim_col]) if r[prim_col] is not None else "",
            reverse=prim_desc
            )
    elif prim_is_str and not case_sensitive:
        sorted_array = sorted(
            array,
            key=lambda r: str(r[prim_col]).lower() if r[prim_col] is not None else "",
            reverse=prim_desc
            )
    else:
        sorted_array = sorted(
            array,
            key=lambda r: float(r[prim_col]) if r[prim_col] is not None else float("-inf"),
            reverse=prim_desc
            )

    return sorted_array
