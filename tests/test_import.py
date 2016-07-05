import pytest


def test_import():

    from dfs_sdk import DateraApi


def test_failed_import():

    with pytest.raises(ImportError):
        from dfs_sdk import NotDateraApi
