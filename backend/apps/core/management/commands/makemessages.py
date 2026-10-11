from django.core.management.commands import makemessages


class Command(makemessages.Command):
    # Без «нечёткого» подбора: gettext иначе подставляет похожие, но неверные переводы
    # (например, «Orders» → «Под заказ»), помечая их fuzzy
    msgmerge_options = [*makemessages.Command.msgmerge_options, "--no-fuzzy-matching"]
