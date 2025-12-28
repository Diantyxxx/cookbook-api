from database import Base
from sqlalchemy.orm import Mapped, mapped_column


class Recipe(Base):
    __tablename__ = "recipes"

    recipe_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True, nullable=False)
    cooking_time: Mapped[int] = mapped_column(nullable=False)
    ingredients: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    views: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return (
            f"Recipe(id={self.recipe_id}, "
            f"title={self.title}, "
            f"cooking time={self.cooking_time})"
        )
