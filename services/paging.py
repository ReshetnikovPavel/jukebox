from collections.abc import Callable
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

Item = dict[str, Any]


def make_paging_keyboard(
    items: list[Item],
    id_key: str,
    from_id: str | None,
    take: int,
    make_item_button: Callable[[Item], InlineKeyboardButton],
    make_left_button: Callable[[str], InlineKeyboardButton],
    make_right_button: Callable[[str], InlineKeyboardButton],
) -> InlineKeyboardMarkup:
    from_index = 0
    if from_id is not None:
        for i, item in enumerate(items):
            if item[id_key] == from_id:
                from_index = i
                break

    keyboard = [
        [make_item_button(item)] for item in items[from_index : from_index + take]
    ]

    paging_row = []

    if from_index != 0:
        prev_from_id = items[max(from_index - take, 0)][id_key]
        paging_row.append(make_left_button(prev_from_id))

    if from_index + take < len(items):
        next_from_id = items[from_index + take][id_key]
        paging_row.append(make_right_button(next_from_id))

    keyboard.append(paging_row)

    return InlineKeyboardMarkup(keyboard)
