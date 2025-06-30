import pytest
import time
from unittest.mock import Mock, patch
from submodel.sdk.job import Job
from submodel.sdk.client import SubModelClient


class TestJob:
    """Test Job class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client"""
        return Mock(spec=SubModelClient)
    
    @pytest.fixture
    def job(self, mock_client):
        """Create job instance"""
        return Job(mock_client, "test-inst-id", "test-job-id")
    
    def test_init(self, mock_client):
        """Test initialization"""
        job = Job(mock_client, "inst-123", "job-456")
        assert job.client == mock_client
        assert job.inst_id == "inst-123"
        assert job.job_id == "job-456"
    
    def test_get_status(self, job, mock_client):
        """Test get_status method"""
        expected_response = {"status": "running", "progress": 50}
        mock_client.get.return_value = expected_response
        
        result = job.get_status()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/status/test-job-id")
        assert result == expected_response
    
    def test_cancel(self, job, mock_client):
        """Test cancel method"""
        expected_response = {"status": "cancelled"}
        mock_client.get.return_value = expected_response
        
        result = job.cancel()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/cancel/test-job-id")
        assert result == expected_response
    
    def test_wait_completed(self, job, mock_client):
        """Test wait method when job completes successfully"""
        mock_client.get.return_value = {"status": "completed", "result": "success"}
        
        with patch('time.sleep') as mock_sleep:
            result = job.wait()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/status/test-job-id")
        mock_sleep.assert_not_called()
        assert result == {"status": "completed", "result": "success"}
    
    def test_wait_failed(self, job, mock_client):
        """Test wait method when job fails"""
        mock_client.get.return_value = {"status": "failed", "error": "Processing error"}
        
        with patch('time.sleep') as mock_sleep:
            result = job.wait()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/status/test-job-id")
        mock_sleep.assert_not_called()
        assert result == {"status": "failed", "error": "Processing error"}
    
    def test_wait_cancelled(self, job, mock_client):
        """Test wait method when job is cancelled"""
        mock_client.get.return_value = {"status": "cancelled"}
        
        with patch('time.sleep') as mock_sleep:
            result = job.wait()
        
        mock_client.get.assert_called_once_with("sl/test-inst-id/status/test-job-id")
        mock_sleep.assert_not_called()
        assert result == {"status": "cancelled"}
    
    def test_wait_with_polling(self, job, mock_client):
        """Test wait method with polling until completion"""
        mock_client.get.side_effect = [
            {"status": "running", "progress": 30},
            {"status": "completed", "result": "success"}
        ]
        
        with patch('time.sleep') as mock_sleep:
            result = job.wait()
        
        assert mock_client.get.call_count == 2
        mock_sleep.assert_called_once_with(1)
        assert result == {"status": "completed", "result": "success"}
    
    def test_wait_timeout(self, job, mock_client):
        """Test wait method with timeout"""
        mock_client.get.return_value = {"status": "running", "progress": 30}
        
        with patch('time.sleep') as mock_sleep, patch('time.time') as mock_time:
            mock_time.side_effect = [0, 5, 11]
            
            with pytest.raises(TimeoutError, match="Job wait timeout"):
                job.wait(timeout=10)
        
        assert mock_client.get.call_count == 2
        mock_sleep.assert_called_with(1)
    
    def test_wait_no_timeout(self, job, mock_client):
        """Test wait method without timeout"""
        mock_client.get.side_effect = [
            {"status": "running", "progress": 10},
            {"status": "running", "progress": 50},
            {"status": "completed", "result": "success"}
        ]
        
        with patch('time.sleep') as mock_sleep:
            result = job.wait()
        
        assert mock_client.get.call_count == 3
        assert mock_sleep.call_count == 2
        assert result == {"status": "completed", "result": "success"}
