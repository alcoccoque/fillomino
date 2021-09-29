#!/usr/bin/env -S python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 hirmiura <https://github.com/hirmiura>


class FillominoError(Exception):
    """フィルオミノのエラー
    """
    pass


class WrongAnswerError(FillominoError):
    """答えが間違っているエラー
    """
    pass
