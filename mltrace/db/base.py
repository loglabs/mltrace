from sqlalchemy.ext.declarative import declarative_base


def _todict(obj: object) -> dict:
    """Return the object's dict excluding private attributes,
    sqlalchemy state and relationship attributes.
    """
    excl = ("_sa_adapter", "_sa_instance_state")
    return {
        k: v
        for k, v in vars(obj).items()
        if not k.startswith("_") and not any(hasattr(v, a) for a in excl)
    }


class BaseWithRepr:
    def __repr__(self):
        params = ", ".join(f"{k}={v}" for k, v in _todict(self).items())
        return f"{self.__class__.__name__}({params})"


Base = declarative_base(cls=BaseWithRepr)
