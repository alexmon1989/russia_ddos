import pytest as pytest

from ripper.context import *


class TestContext:
    def test_can_store_error_details(self):
        context = Context()
        context.errors.clear()

        actual = Errors(code='send UDP packet', message='Cannot get server ip')
        uuid = actual.uuid
        context.errors[uuid] = actual

        assert len(context.errors) == 1
        assert context.errors.get(uuid).code == 'send UDP packet'
        assert context.errors.get(uuid).count == 1
        assert context.errors.get(uuid).message == 'Cannot get server ip'

    def test_can_count_the_same_error(self):
        context = Context()
        context.errors.clear()

        assert len(context.errors) == 0

        actual = Errors(code='send UDP packet', message='Cannot get server ip')
        uuid = actual.uuid
        context.add_error(actual)

        assert len(context.errors) == 1
        assert context.errors.get(uuid) == actual
        assert context.errors.get(uuid).count == 1
        assert context.errors.get(uuid).code == 'send UDP packet'

        context.add_error(actual)
        assert len(context.errors) == 1
        assert context.errors.get(uuid).count == 2

    def test_can_delete_existing_error(self):
        context = Context()
        context.errors.clear()

        actual = Errors(code='send UDP packet', message='Cannot get server ip')
        uuid = actual.uuid
        context.add_error(actual)

        assert len(context.errors) == 1
        assert context.errors.get(uuid) == actual

        context.remove_error(uuid)
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

