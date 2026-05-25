# -*- coding: utf-8 -*-
"""
Business Layer - UbicuoAI Module
Business logic services
"""

from .parser_service import EnhancedParserService
from .matcher_service import MatcherService
from .learning_service import LearningService
from .ubicuoai_service import EnhancedUbicuoAIService
from .section_manager import SectionManager

# Aliases para compatibilidad
ParserService = EnhancedParserService
UbicuoAIService = EnhancedUbicuoAIService

__all__ = [
    'EnhancedParserService',
    'ParserService',
    'MatcherService',
    'LearningService',
    'EnhancedUbicuoAIService',
    'UbicuoAIService',
    'SectionManager',
]
