from arcstone_adaptive_producer_lab.disclosure import project
from arcstone_adaptive_producer_lab.types import BoundaryResult

def test_l1_redacts_reason(): assert project(BoundaryResult("DENY","PayloadMismatch"),"L1")=={"decision":"DENY"}
def test_l3_includes_reason(): assert project(BoundaryResult("DENY","PayloadMismatch"),"L3")=={"decision":"DENY","deny_reason":"PayloadMismatch"}
