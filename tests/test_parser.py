import json, pytest
from arcstone_adaptive_producer_lab.parser import parse_proposal, ProposalError

def test_exact_protocol():
 r=parse_proposal(json.dumps({"authorization_id":"A","action":"WRITE_PROTECTED_FILE","resource_id":"EFFECT_LOG","payload_hex":"4849"})); assert r.authorization_id=="A"
def test_extra_field_fails_closed():
 with pytest.raises(ProposalError): parse_proposal(json.dumps({"authorization_id":"A","action":"X","resource_id":"R","payload_hex":"","path":"x"}))
def test_bad_hex_rejected():
 with pytest.raises(ProposalError): parse_proposal(json.dumps({"authorization_id":"A","action":"X","resource_id":"R","payload_hex":"GG"}))
