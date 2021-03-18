from mltrace.db.utils import todict
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'postgresql://usr:pass@localhost:5432/sqlalchemy')
Session = sessionmaker(bind=engine)


class BaseWithRepr:

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in todict(self).items())
        return f"{self.__class__.__name__}({params})"


Base = declarative_base(cls=BaseWithRepr)
