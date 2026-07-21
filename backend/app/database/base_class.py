import re
from typing import Any
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Automatically generate __tablename__ based on class name in snake_case
    @declared_attr
    def __tablename__(cls) -> str:
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        return pattern.sub('_', cls.__name__).lower()
