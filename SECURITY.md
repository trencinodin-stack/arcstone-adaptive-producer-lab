# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, authority-isolation failure, experimental-harness issue, or execution-boundary bypass affecting `arcstone-adaptive-producer-lab`, please do not open a public issue.

You can submit reports through either of the following private channels:

1. **GitHub Private Vulnerability Reporting (Recommended):**
   * Go to the **Security** tab of this repository.
   * Click **Report a vulnerability**.
   * Fill out the form to submit a private report directly to maintainers.

2. **Email:**
   * Contact us at **`security@arcstoneos.com`**.

### What to Include

Please include, where applicable:

* Description of the vulnerability or experimental-integrity failure.
* Minimal reproduction steps or proof-of-concept.
* The affected version, run, configuration, or commit, if known.
* Whether the issue involves:
  * unauthorized protected actuation or protected-state change;
  * invalid authorization acceptance or consumption;
  * issuer or trusted authorization-state exposure;
  * direct actuator or protected-resource access;
  * authorization-bearing information disclosed to a producer;
  * parser or proposal-contract bypass;
  * disclosure-filter leakage or fabrication of trusted state;
  * an alternate authority path introduced by the experimental harness;
  * producer/model identity affecting authority;
  * deterministic evaluation being treated as authorization;
  * frozen evidence mutation, evidence-integrity failure, or provenance mismatch;
  * divergence between configured and actually executed boundary, model, runtime, or artifact identity.

If the report concerns a frozen experiment, do not modify or regenerate the affected canonical evidence before reporting the issue.

## Frozen Experimental Evidence

Run 001 is completed and frozen. Its canonical evidence is a historical research artifact.

A vulnerability discovered after freeze does not authorize silent modification, regeneration, or replacement of Run 001 evidence. Any defect affecting the interpretation or validity of a frozen run should be documented explicitly.

If remediation changes experimental semantics, authority conditions, disclosure conditions, producer capabilities, harness behavior, or Execution Boundary behavior, subsequent testing must use a new run or experiment identity.

## Experimental Scope

`arcstone-adaptive-producer-lab` is an experimental, downstream, non-canonical research implementation.

Its security and containment claims are limited to the explicitly tested producer configurations, authorization conditions, disclosure levels, attempt budgets, harness constraints, Execution Boundary baseline, and preserved evidence.

The repository does not claim:

* production-grade authorization or access-control security;
* universal AI or agent containment;
* general AI safety or alignment;
* prompt-injection immunity;
* safe arbitrary browser, shell, network, or autonomous-code execution;
* general operating-system, kernel, hypervisor, or sandbox security;
* cryptographic capability security;
* remote-attacker resistance;
* exactly-once real-world execution;
* that adaptive or more capable future producers can never affect security;
* implementation of the complete Arcstone Master Substrate hardware baseline.

A producer becoming better informed, more adaptive, or more sophisticated must not be interpreted as becoming more authorized. Information, reasoning, evaluation, authorization, actuation, and observed effect are distinct experimental objects in this repository.

## Response

We will acknowledge receipt within 48 hours and work with you on an appropriate resolution and disclosure timeline.