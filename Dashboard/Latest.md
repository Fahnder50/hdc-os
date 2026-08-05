# HDC-OS Operations Cockpit

## Overall Health

**CRITICAL**

## Today's Summary — Daily Briefing

- No important changes since the previous cockpit run.

## Agents

**HEALTHY — SUCCESS**

One registered agent: Procurement Agent v1.

- **Registered Agents:** procurement-agent
- **Last Run:** 2026-08-05T07:01:14+00:00
- **Next Run:** 2026-08-06T07:00+02:00
- **Result:** SUCCESS
- **Duration Seconds:** 62.696023
- **Provider:** deterministic-fallback
- **Model:** rules-v1
- **Fallback Used:** True

## Assets

**HEALTHY — OPERATIONAL**

1 productive asset; no known acceptance blockers.

- **Productive Assets:** 1
- **Asset Health:** HEALTHY
- **Critical Assets:** UPS-RTR-01
- **Last Acceptance Status:** UPS-RTR-01: PRODUCTION on 2026-08-04

## Deployment

**CRITICAL — NOT_READY**

First Deployment is blocked by missing firewall, managed switch, and open readiness evidence.

- **Gates:** Gate: Hardware Ready, Status: FAIL; Gate: Configuration Ready, Status: FAIL; Gate: Installation Ready, Status: FAIL; Gate: Test Ready, Status: FAIL; Gate: Rollback Ready, Status: FAIL; Gate: Architecture Conformity, Status: PASS
- **Bottleneck:** Firewall and Managed Switch are missing; further WO-0041 evidence is open.
- **Missing Hardware:** OPNsense Firewall, Managed Switch
- **First Deployment Progress:** 1/6 gates PASS (17%)

## Procurement

**HEALTHY — SUCCESS**

4 procurement cases analyzed by deterministic fallback; 3 changed.

- **Active Cases:** 4
- **Last Run:** 2026-08-05T07:01:14+00:00
- **Next Run:** 2026-08-06T07:00+02:00
- **Agent Status:** SUCCESS
- **Current Recommendations:** Case Id: PC-0002, Recommendation: KEEP_WATCHING, Information Status: INFORMATION, Reason: Deterministic fallback derived from QUALIFYING.; Case Id: PC-0003, Recommendation: KEEP_WATCHING, Information Status: INFORMATION, Reason: Deterministic fallback derived from WATCHING.; Case Id: PC-0004, Recommendation: KEEP_WATCHING, Information Status: INFORMATION, Reason: Deterministic fallback derived from QUALIFYING.; Case Id: PC-0005, Recommendation: KEEP_WATCHING, Information Status: INFORMATION, Reason: Deterministic fallback derived from QUALIFYING.

## Recommended Actions

- deployment-hardware: Procure and qualify the Horizon-1 firewall and managed switch.
- deployment-gates: Close the remaining WO-0041 readiness evidence before deployment.
