import pytest

def test_case_1():
    print("test_case_1")
    raise ValueError

def test_case_2(sess_ft_1):
    print("test_case_2")
    print('sess_ft_1 id = {}'.format(id(sess_ft_1)))

def test_case_3(sess_ft_2):
    print("test_case_3")
    print('sess_ft_2 id = {}'.format(id(sess_ft_2)))

def test_case_4(sess_ft_4):
    print("test_case_4")
    print('sess_ft_4 id = {}'.format(id(sess_ft_4)))
