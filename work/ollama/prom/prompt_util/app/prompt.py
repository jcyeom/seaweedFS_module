import requests
from typing import List
from .util.logger import factory

logger = factory(__name__)

class PromptClient:
    def __init__(self, ip: str = "192.168.192.87", port: str = "8000") -> None:
        self.base_url = ip + ":" +port
        logger.info(f"PromptClient initialized with {self.base_url}")
    
    def typo_correction(self, data: List[str]) -> List[str]:
        """
        Return a list of corrections for typos in the input data.

        Args:
            data (List[str]): List of strings to check for typos.

        Returns:
            List[str]: List of corrected strings.
        """
        logger.info("prompt - func call: typo_correction")
        result = []
        for item in data:
            # Replace with actual Ollama API call or logic
            result.append(item)
        return result

    def typo_detection(self, data: List[str]) -> (bool, List[str]): # type: ignore
        """
        Detect typos in the input data.

        Args:
            data (List[str]): List of strings to detect typos.

        Returns:
            bool: Whether typos were found.
            List[str]: List of strings with potential typos.
        """
        logger.info("prompt - func call: typo_detection")
        has_typos = False
        result = []
        for item in data:
            # Replace with actual Ollama API call or logic
            result.append(item)
        return has_typos, result

    def classify(self, data: List[str]) -> List[str]:
        """
        Classify the input data.

        Args:
            data (List[str]): List of strings to classify.

        Returns:
            List[str]: List of classifications.
        """
        logger.info("prompt - func call: classify")
        result = []
        for item in data:
            # Replace with actual Ollama API call or logic
            result.append(item)
        # Replace with actual classification logic
        return result