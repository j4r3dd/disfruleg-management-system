# -*- coding: utf-8 -*-
"""
Learning Service - Business Logic Layer
Handles learning and corrections
NO direct database access - uses repositories only!
"""

from typing import Dict, Optional
from datetime import datetime

from ..data.repositories import ILearningRepository
from ..domain.models import LearningCorrection
from ..domain.exceptions import LearningError


class LearningService:
    """
    Learning service for managing corrections
    Handles all learning business logic
    """

    def __init__(self, learning_repo: ILearningRepository):
        """
        Initialize service with injected dependencies

        Args:
            learning_repo: Learning repository interface
        """
        self.learning_repo = learning_repo

    def get_all_corrections(self) -> Dict[str, str]:
        """
        Get all corrections as simple dict

        Returns:
            Dict mapping incorrect -> correct
        """
        corrections = self.learning_repo.get_all_corrections()
        return {
            incorrect: corr.correct
            for incorrect, corr in corrections.items()
        }

    def get_correction(self, incorrect: str) -> Optional[str]:
        """
        Get correction for incorrect text

        Args:
            incorrect: Incorrect text to correct

        Returns:
            Corrected text or None if not found
        """
        # Fail fast: Validate input
        if not incorrect or not incorrect.strip():
            raise ValueError("Incorrect text cannot be empty")

        correction = self.learning_repo.get_correction(incorrect)

        if correction:
            # Increment usage counter
            self.learning_repo.increment_usage(incorrect)
            return correction.correct

        return None

    def add_correction(
        self,
        incorrect: str,
        correct: str
    ) -> bool:
        """
        Add or update a correction

        Args:
            incorrect: Incorrect text
            correct: Correct text

        Returns:
            True if successful

        Raises:
            ValueError: If validation fails
            LearningError: If save operation fails
        """
        # Fail fast: Validate inputs
        if not incorrect or not incorrect.strip():
            raise ValueError("Incorrect text cannot be empty")

        if not correct or not correct.strip():
            raise ValueError("Correct text cannot be empty")

        if incorrect.strip().lower() == correct.strip().lower():
            raise ValueError("Incorrect and correct text must be different")

        # Check if correction already exists
        existing = self.learning_repo.get_correction(incorrect)

        if existing:
            # Update existing correction
            existing.correct = correct
            existing.increment_usage()
            return self.learning_repo.save_correction(existing)
        else:
            # Create new correction
            now = datetime.now()
            correction = LearningCorrection(
                incorrect=incorrect,
                correct=correct,
                times_used=1,
                first_added=now,
                last_used=now
            )
            return self.learning_repo.save_correction(correction)

    def remove_correction(self, incorrect: str) -> bool:
        """
        Remove a correction

        Args:
            incorrect: Incorrect text to remove

        Returns:
            True if successful
        """
        if not incorrect or not incorrect.strip():
            raise ValueError("Incorrect text cannot be empty")

        return self.learning_repo.delete_correction(incorrect)

    def get_statistics(self) -> dict:
        """
        Get learning system statistics

        Returns:
            Dictionary with statistics
        """
        return self.learning_repo.get_statistics()

    def cleanup_old_corrections(
        self,
        max_age_days: int = 180,
        min_usage: int = 1
    ) -> int:
        """
        Clean up old, rarely-used corrections

        Args:
            max_age_days: Maximum age in days
            min_usage: Minimum usage count required

        Returns:
            Number of corrections removed
        """
        # Fail fast: Validate inputs
        if max_age_days < 1:
            raise ValueError("Max age days must be at least 1")

        if min_usage < 0:
            raise ValueError("Min usage cannot be negative")

        return self.learning_repo.cleanup_old_entries(max_age_days, min_usage)
