# -*- coding: utf-8 -*-
"""
Formatters for Analytics Module
Centralized formatting utilities for dates, currency, and numbers
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class DateFormatter:
    """Utility class for date formatting"""

    @staticmethod
    def format_short(date_value: Optional[Union[datetime, date, str]]) -> str:
        """
        Format date to short format: DD/MM

        Args:
            date_value: Date object, datetime object, or string

        Returns:
            Formatted date string like "24/11" or "N/A" if invalid

        Examples:
            >>> DateFormatter.format_short(datetime(2025, 11, 24))
            '24/11'
        """
        if date_value is None:
            return "N/A"

        try:
            if isinstance(date_value, str):
                return date_value  # Assume already formatted
            if isinstance(date_value, (datetime, date)):
                return date_value.strftime('%d/%m')
            return str(date_value)
        except Exception as e:
            logger.warning(f"Error formatting date (short): {e}")
            return "N/A"

    @staticmethod
    def format_full(date_value: Optional[Union[datetime, date, str]]) -> str:
        """
        Format date to full format: DD/MM/YYYY

        Args:
            date_value: Date object, datetime object, or string

        Returns:
            Formatted date string like "24/11/2025" or "N/A" if invalid

        Examples:
            >>> DateFormatter.format_full(datetime(2025, 11, 24))
            '24/11/2025'
        """
        if date_value is None:
            return "N/A"

        try:
            if isinstance(date_value, str):
                # Try to parse if it's a string
                try:
                    parsed = datetime.strptime(date_value, '%Y-%m-%d')
                    return parsed.strftime('%d/%m/%Y')
                except:
                    return date_value  # Return as-is if can't parse
            if isinstance(date_value, (datetime, date)):
                return date_value.strftime('%d/%m/%Y')
            return str(date_value)
        except Exception as e:
            logger.warning(f"Error formatting date (full): {e}")
            return "N/A"

    @staticmethod
    def format_range(
        start_date: Optional[Union[datetime, date]],
        end_date: Optional[Union[datetime, date]]
    ) -> str:
        """
        Format date range: DD/MM - DD/MM

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Formatted range string like "01/11 - 30/11" or "N/A" if invalid

        Examples:
            >>> DateFormatter.format_range(datetime(2025, 11, 1), datetime(2025, 11, 30))
            '01/11 - 30/11'
        """
        if start_date is None or end_date is None:
            return "N/A"

        try:
            start_str = DateFormatter.format_short(start_date)
            end_str = DateFormatter.format_short(end_date)
            return f"{start_str} - {end_str}"
        except Exception as e:
            logger.warning(f"Error formatting date range: {e}")
            return "N/A"

    @staticmethod
    def format_datetime(datetime_value: Optional[datetime]) -> str:
        """
        Format datetime to full format: DD/MM/YYYY HH:MM:SS

        Args:
            datetime_value: Datetime object

        Returns:
            Formatted datetime string or "N/A" if invalid

        Examples:
            >>> DateFormatter.format_datetime(datetime(2025, 11, 24, 15, 30, 45))
            '24/11/2025 15:30:45'
        """
        if datetime_value is None:
            return "N/A"

        try:
            if isinstance(datetime_value, datetime):
                return datetime_value.strftime('%d/%m/%Y %H:%M:%S')
            return str(datetime_value)
        except Exception as e:
            logger.warning(f"Error formatting datetime: {e}")
            return "N/A"


class CurrencyFormatter:
    """Utility class for currency formatting"""

    @staticmethod
    def format(
        amount: Optional[Union[float, int, Decimal, str]],
        currency_symbol: str = "$",
        decimals: int = 2
    ) -> str:
        """
        Format amount as currency with thousands separator

        Args:
            amount: Numeric value to format
            currency_symbol: Currency symbol (default: "$")
            decimals: Number of decimal places (default: 2)

        Returns:
            Formatted currency string like "$1,234.56" or "$0.00" if invalid

        Examples:
            >>> CurrencyFormatter.format(1234.56)
            '$1,234.56'
            >>> CurrencyFormatter.format(1000000)
            '$1,000,000.00'
        """
        if amount is None:
            return f"{currency_symbol}0.00"

        try:
            # Convert to float
            if isinstance(amount, str):
                amount = float(amount.replace(',', ''))
            else:
                amount = float(amount)

            # Format with thousands separator
            return f"{currency_symbol}{amount:,.{decimals}f}"
        except Exception as e:
            logger.warning(f"Error formatting currency: {e}")
            return f"{currency_symbol}0.00"

    @staticmethod
    def format_compact(
        amount: Optional[Union[float, int, Decimal, str]],
        currency_symbol: str = "$"
    ) -> str:
        """
        Format amount as compact currency (K, M, B)

        Args:
            amount: Numeric value to format
            currency_symbol: Currency symbol (default: "$")

        Returns:
            Formatted compact string like "$1.2K", "$3.5M", "$1.2B"

        Examples:
            >>> CurrencyFormatter.format_compact(1234)
            '$1.2K'
            >>> CurrencyFormatter.format_compact(1234567)
            '$1.2M'
            >>> CurrencyFormatter.format_compact(1234567890)
            '$1.2B'
        """
        if amount is None:
            return f"{currency_symbol}0"

        try:
            # Convert to float
            if isinstance(amount, str):
                amount = float(amount.replace(',', ''))
            else:
                amount = float(amount)

            # Determine magnitude
            if abs(amount) >= 1_000_000_000:
                return f"{currency_symbol}{amount / 1_000_000_000:.1f}B"
            elif abs(amount) >= 1_000_000:
                return f"{currency_symbol}{amount / 1_000_000:.1f}M"
            elif abs(amount) >= 1_000:
                return f"{currency_symbol}{amount / 1_000:.1f}K"
            else:
                return f"{currency_symbol}{amount:.0f}"
        except Exception as e:
            logger.warning(f"Error formatting compact currency: {e}")
            return f"{currency_symbol}0"


class NumberFormatter:
    """Utility class for number formatting"""

    @staticmethod
    def format_with_commas(
        number: Optional[Union[float, int, Decimal, str]],
        decimals: int = 0
    ) -> str:
        """
        Format number with thousands separator

        Args:
            number: Numeric value to format
            decimals: Number of decimal places (default: 0)

        Returns:
            Formatted number string like "1,234" or "1,234.56"

        Examples:
            >>> NumberFormatter.format_with_commas(1234)
            '1,234'
            >>> NumberFormatter.format_with_commas(1234.56, decimals=2)
            '1,234.56'
        """
        if number is None:
            return "0"

        try:
            # Convert to float
            if isinstance(number, str):
                number = float(number.replace(',', ''))
            else:
                number = float(number)

            # Format with thousands separator
            if decimals == 0:
                return f"{number:,.0f}"
            else:
                return f"{number:,.{decimals}f}"
        except Exception as e:
            logger.warning(f"Error formatting number: {e}")
            return "0"

    @staticmethod
    def format_percentage(
        value: Optional[Union[float, int, Decimal, str]],
        decimals: int = 1
    ) -> str:
        """
        Format value as percentage

        Args:
            value: Numeric value to format (already as percentage, not decimal)
            decimals: Number of decimal places (default: 1)

        Returns:
            Formatted percentage string like "45.6%" or "0.0%"

        Examples:
            >>> NumberFormatter.format_percentage(45.6)
            '45.6%'
            >>> NumberFormatter.format_percentage(100)
            '100.0%'
        """
        if value is None:
            return "0.0%"

        try:
            # Convert to float
            if isinstance(value, str):
                value = float(value.replace('%', '').replace(',', ''))
            else:
                value = float(value)

            # Format with specified decimals
            return f"{value:.{decimals}f}%"
        except Exception as e:
            logger.warning(f"Error formatting percentage: {e}")
            return "0.0%"

    @staticmethod
    def format_compact(number: Optional[Union[float, int, Decimal, str]]) -> str:
        """
        Format number in compact form (K, M, B)

        Args:
            number: Numeric value to format

        Returns:
            Formatted compact string like "1.2K", "3.5M", "1.2B"

        Examples:
            >>> NumberFormatter.format_compact(1234)
            '1.2K'
            >>> NumberFormatter.format_compact(1234567)
            '1.2M'
        """
        if number is None:
            return "0"

        try:
            # Convert to float
            if isinstance(number, str):
                number = float(number.replace(',', ''))
            else:
                number = float(number)

            # Determine magnitude
            if abs(number) >= 1_000_000_000:
                return f"{number / 1_000_000_000:.1f}B"
            elif abs(number) >= 1_000_000:
                return f"{number / 1_000_000:.1f}M"
            elif abs(number) >= 1_000:
                return f"{number / 1_000:.1f}K"
            else:
                return f"{number:.0f}"
        except Exception as e:
            logger.warning(f"Error formatting compact number: {e}")
            return "0"


class PeriodConverter:
    """Utility class for converting period strings to days"""

    # Period to days mapping
    PERIOD_MAP = {
        '1D': 1,
        '7D': 7,
        '15D': 15,
        '30D': 30,
        '60D': 60,
        '90D': 90,
        '180D': 180,
        '6M': 180,
        '1Y': 365,
        'Todo': 9999,
        'ALL': 9999
    }

    @staticmethod
    def to_days(period_str: str) -> int:
        """
        Convert period string to number of days

        Args:
            period_str: Period identifier like "7D", "30D", "1Y", etc.

        Returns:
            Number of days (default: 30 if invalid)

        Examples:
            >>> PeriodConverter.to_days("7D")
            7
            >>> PeriodConverter.to_days("1Y")
            365
            >>> PeriodConverter.to_days("Todo")
            9999
        """
        days = PeriodConverter.PERIOD_MAP.get(period_str, 30)
        logger.debug(f"Period '{period_str}' converted to {days} days")
        return days

    @staticmethod
    def to_label(period_str: str) -> str:
        """
        Convert period string to human-readable label

        Args:
            period_str: Period identifier like "7D", "30D", "1Y"

        Returns:
            Human-readable label

        Examples:
            >>> PeriodConverter.to_label("7D")
            'Últimos 7 días'
            >>> PeriodConverter.to_label("1Y")
            'Último año'
        """
        labels = {
            '1D': 'Último día',
            '7D': 'Últimos 7 días',
            '15D': 'Últimos 15 días',
            '30D': 'Últimos 30 días',
            '60D': 'Últimos 60 días',
            '90D': 'Últimos 90 días',
            '180D': 'Últimos 180 días',
            '6M': 'Últimos 6 meses',
            '1Y': 'Último año',
            'Todo': 'Todo el historial',
            'ALL': 'Todo el historial'
        }
        return labels.get(period_str, f"Últimos {PeriodConverter.to_days(period_str)} días")

    @staticmethod
    def get_all_periods() -> list:
        """
        Get list of all available periods

        Returns:
            List of period strings

        Examples:
            >>> PeriodConverter.get_all_periods()
            ['1D', '7D', '15D', '30D', '60D', '90D', '180D', '6M', '1Y', 'Todo']
        """
        return ['1D', '7D', '15D', '30D', '60D', '90D', '180D', '6M', '1Y', 'Todo']
