#     Copyright (C) 2023  Coretex LLC

#     This file is part of Coretex.ai

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

from decimal import Decimal, ROUND_HALF_UP


def mathematicalRound(value: float, decimalPlaces: int) -> float:
    """
        Performes mathematical (ROUND_HALF_UP) rounding
        Ex. >= 1.5 will be rounded to 2, < 1.5 will be rounded to 1

        Parameters
        ----------
        value : float
            value to be rounded
        decimalPlaces : int
            amount of decimal places to which the value will be rounded

        Returns
        -------
        float -> the rounded value
    """

    decimal = Decimal(str(value))
    places = Decimal(10) ** -decimalPlaces

    return float(decimal.quantize(places, rounding = ROUND_HALF_UP))


def formatBytes(value: int, precision = 2):
    """
    Format a size in bytes into a human-readable format.

    Parameters:
        value (int): The size in bytes.
        precision (int): Number of decimal places (default is 2).

    Returns:
        str: Formatted string with size and appropriate unit.
    """

    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    index = 0

    while value >= 1024 and index < len(suffixes) - 1:
        index += 1
        value /= 1024.0

    return f"{value:.{precision}f} {suffixes[index]}"
