import pytest
from arcstone_adaptive_producer_lab.boundary import SubprocessBoundary

def test_missing_boundary_binary_fails():
 with pytest.raises(FileNotFoundError): SubprocessBoundary("definitely-not-a-real-arcstone-exec", ".", ["{executable}"])
