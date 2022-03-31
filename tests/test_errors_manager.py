import pytest as pytest

from ripper.errors import Error
from ripper.errors_manager import ErrorsManager, merge_error_dicts


class FakeError(Error):
    def __init__(self):
        super().__init__(code='Fake Error', message='Fake Error', count=1)


class DescribeError:
    def it_can_clone_error(self):
        fe1 = FakeError()
        fe2 = fe1.clone()
        assert fe1 != fe2
        assert fe1.uuid == fe2.uuid
        assert fe1.count == fe2.count
        fe1.count += 10
        assert fe1.count == fe2.count + 10


class DescribeErrorsManager:
    def it_can_merge_error_dicts(self):
        error2 = Error(code='XYZ', message='1-2-3')
        em1 = ErrorsManager()
        em1.add_error(FakeError())
        em1.add_error(FakeError())
        em1.add_error(FakeError())
        em1.add_error(error2)
        assert em1.errors[FakeError().uuid].count == 3
        assert em1.errors[error2.uuid].count == 1
        em2 = ErrorsManager()
        assert em1._errors != em2._errors
        em2.add_error(FakeError())
        em2.add_error(FakeError())
        assert em2.errors[FakeError().uuid].count == 2
        assert em1.errors[FakeError().uuid].count == 3
        merged_errors = merge_error_dicts(em1.errors, em2.errors)
        assert merged_errors[FakeError().uuid].count == 5
        assert merged_errors[error2.uuid].count == 1

    def it_can_construct_errors_single_level(self):
        em = ErrorsManager()
        assert not em.has_errors()
        em.add_error(FakeError())
        assert em.has_errors()
        em.remove_error(FakeError().uuid)
        assert not em.has_errors()

    # def it_can_store_error_details(self):
    #     em = ErrorsManager()
    #     em.clear_errors()

    #     actual = Error(code='send UDP packet', message='Cannot get server ip')
    #     uuid = actual.uuid
    #     em.add_error(actual)

    #     assert len(em.errors) == 1
    #     assert em.errors.get(uuid).code == 'send UDP packet'
    #     assert em.errors.get(uuid).count == 1
    #     assert em.errors.get(uuid).message == 'Cannot get server ip'

    # def it_can_count_the_same_error(self):
    #     em = ErrorsManager()

    #     assert len(em.errors) == 0

    #     actual = Error(code='send UDP packet', message='Cannot get server ip')
    #     uuid = actual.uuid
    #     em.add_error(actual)

    #     assert len(em.errors) == 1
    #     assert em.errors.get(uuid) == actual
    #     assert em.errors.get(uuid).count == 1
    #     assert em.errors.get(uuid).code == 'send UDP packet'

    #     em.add_error(actual)
    #     assert len(em.errors) == 1
    #     assert em.errors.get(uuid).count == 2

    # def it_can_delete_existing_error(self):
    #     context = Context(self.args)
    #     context.errors.clear()

    #     actual = Error(code='send UDP packet', message='Cannot get server ip')
    #     uuid = actual.uuid
    #     context.add_error(actual)

    #     assert len(context.errors) == 1
    #     assert context.errors.get(uuid) == actual

    #     context.remove_error(uuid)
    #     assert len(context.errors) == 0
