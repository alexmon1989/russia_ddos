class AttackMethod:
    """Abstract attack method."""

    @property
    def name(self):
      raise NotImplemented

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def validate(self):
      return True