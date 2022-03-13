import pytest as pytest

from ripper.context import *


class TestContext:
    def test_can_store_error_details(self):
        context = Context()
        context.errors.clear()
        error_key = ErrorCodes.CannotGetServerIP.value

        assert error_key == 'CANNOT_GET_SERVER_IP'

        actual = Errors(code=error_key, message='Cannot get server ip')
        context.errors[error_key] = actual

        assert len(context.errors) == 1
        assert context.errors.get(error_key).code == error_key
        assert context.errors.get(error_key).count == 1
        assert context.errors.get(error_key).message == 'Cannot get server ip'

    def test_can_count_the_same_error(self):
        context = Context()
        context.errors.clear()
        error_key = ErrorCodes.CannotGetServerIP.value

        assert len(context.errors) == 0

        actual = Errors(code=error_key, message='Cannot get server ip')
        context.add_error(actual)

        assert len(context.errors) == 1
        assert context.errors.get(error_key) == actual
        assert context.errors.get(error_key).count == 1

        context.add_error(actual)
        assert len(context.errors) == 1
        assert context.errors.get(error_key).count == 2

    def test_can_delete_existing_error(self):
        context = Context()
        context.errors.clear()

        error_key = ErrorCodes.CannotGetServerIP.value
        actual = Errors(code=error_key, message='Cannot get server ip')
        context.add_error(actual)

        assert len(context.errors) == 1
        assert context.errors.get(error_key) == actual

        context.remove_error(error_key)
        assert len(context.errors) == 0

    @pytest.mark.parametrize('actual_ip, expected_result', [
        ('127.0.0.1', '127.*.*.*'),
        ('42.199.100.200', '42.*.*.*'),
        ('42', '42'),
        ('...detecting', '...detecting')
    ])
    def test_get_my_ip_masked(self, actual_ip, expected_result):
        context = Context()
        context.IpInfo.my_start_ip = actual_ip

        assert context.IpInfo.my_ip_masked() == expected_result

