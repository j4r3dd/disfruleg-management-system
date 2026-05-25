# -*- coding: utf-8 -*-
"""
UI Package para módulo de deudas
"""

from typing import TYPE_CHECKING

# Importar componentes de UI
from .components import *

if TYPE_CHECKING:
    from ..business import DebtService