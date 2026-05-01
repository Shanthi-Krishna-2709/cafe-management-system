from django.db.utils import OperationalError, ProgrammingError

from .menu_catalog import MENU_CATALOG
from .models import Category, Menu


def sync_menu_catalog(sender, **kwargs):
    """
    Keep menu/category rows available after a fresh migrate.
    The operation is idempotent, so it is safe on every post_migrate run.
    """
    try:
        for section in MENU_CATALOG:
            category, _ = Category.objects.get_or_create(name=section["category"])
            for item_data in section["items"]:
                Menu.objects.update_or_create(
                    name=item_data["name"],
                    defaults={
                        "price": item_data["price"],
                        "category": category,
                    },
                )
    except (OperationalError, ProgrammingError):
        # During partial migration states Django may emit post_migrate before
        # every table is ready. A later post_migrate signal will complete the sync.
        return
