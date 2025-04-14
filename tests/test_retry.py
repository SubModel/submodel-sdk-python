import unittest
from unittest.mock import patch, MagicMock, call
import time
import requests
from submodel.sdk.utils import retry

class TestRetry(unittest.TestCase):
    def test_non_retryable_exception(self):
        """Test non-retryable exception"""
        @retry(retryable_exceptions=(ValueError,))
        def test_function():
            raise KeyError("Not retryable")
            
        with self.assertRaises(KeyError):
            test_function()

    def test_retry_decorator_without_params(self):
        """Test retry decorator without parameters"""
        failure_count = 0
        
        @retry()
        def test_function():
            nonlocal failure_count
            failure_count += 1
            if failure_count < 2:
                raise requests.ConnectionError("Connection failed")
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(failure_count, 2)

    @patch('time.sleep')
    def test_retry_max_attempts_exceeded(self, mock_sleep):
        """Test retry attempts exceeding maximum limit"""
        failure_count = 0
        
        @retry(max_retries=2, delay=0.1, backoff_factor=2)
        def test_function():
            nonlocal failure_count
            failure_count += 1
            raise requests.ConnectionError("Connection failed")
        
        with self.assertRaises(requests.ConnectionError):
            test_function()
        
        self.assertEqual(failure_count, 3)  # 1 initial + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_has_calls([
            call(0.1),      # First retry: initial delay
            call(0.2),      # Second retry: initial delay * (2^1)
        ])

    @patch('time.sleep')
    def test_retry_success_after_failures(self, mock_sleep):
        """Test success after failures"""
        failure_count = 0
        
        @retry(max_retries=3, delay=0.1, backoff_factor=2)
        def test_function():
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 2:
                raise requests.ConnectionError("Connection failed")
            return "success"
        
        result = test_function()
        
        self.assertEqual(result, "success")
        self.assertEqual(failure_count, 3)  # 2 failures + 1 success
        self.assertEqual(mock_sleep.call_count, 2)  # Only sleep after failures
        mock_sleep.assert_has_calls([
            call(0.1),      # First retry: initial delay
            call(0.2),      # Second retry: initial delay * (2^1)
        ])

    def test_retry_with_different_exceptions(self):
        """Test different types of exceptions"""
        @retry(retryable_exceptions=(ValueError, KeyError))
        def test_function():
            raise ValueError("Test error")
            
        with self.assertRaises(ValueError):
            test_function()

if __name__ == '__main__':
    unittest.main()