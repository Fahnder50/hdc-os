from dataclasses import dataclass
import json


PROFILE_STATUSES = frozenset({"approved"})
REQUIREMENT_STATUSES = frozenset({"CONFIRMED", "PROPOSED", "OPEN", "REJECTED"})
REQUIREMENT_PRIORITIES = frozenset({"MUST", "SHOULD", "PREFERENCE", "INFORMATIONAL"})


class RequirementProfileError(ValueError):
    pass


@dataclass(frozen=True)
class RequirementProfile:
    profile_id: str
    case_id: str
    name: str
    status: str
    version: str
    approved_at: str | None
    requirements: tuple[dict, ...]

    @property
    def is_approved(self):
        return self.status == "approved"

    @property
    def criteria(self):
        values = {}
        for requirement in self.requirements:
            key = requirement.get("engine_key", requirement["id"])
            values[key] = requirement.get("value", requirement.get("description"))
        return values

    @property
    def confirmed_engine_keys(self):
        return {
            requirement.get("engine_key", requirement["id"])
            for requirement in self.requirements
            if requirement["status"] == "CONFIRMED"
        }


def parse_requirement_profile(document, case_id):
    if document is None:
        return None
    if not isinstance(document, dict):
        raise RequirementProfileError(f"{case_id} requirement profile must be a mapping.")
    if document.get("case_id", case_id) != case_id:
        raise RequirementProfileError(f"Requirement profile belongs to another case: {document.get('case_id')}.")
    profile_id = document.get("profile_id")
    name = document.get("name")
    status = document.get("status")
    requirements = document.get("requirements")
    if requirements is None and isinstance(document.get("criteria"), dict):
        requirements = [
            {"id": key, "title": key, "description": str(value), "status": "CONFIRMED", "priority": "MUST", "validation_type": "documented", "source": {"type": "legacy_profile", "reference": "RWO-0019"}, "value": value}
            for key, value in document["criteria"].items()
        ]
    if not profile_id or not name or not isinstance(requirements, list) or not requirements:
        raise RequirementProfileError(f"{case_id} requirement profile is incomplete.")
    if status not in PROFILE_STATUSES:
        raise RequirementProfileError(f"{case_id} requirement profile has invalid status: {status}.")
    normalized = []
    for requirement in requirements:
        required_fields = ("id", "title", "description", "status", "priority", "validation_type", "source")
        if not isinstance(requirement, dict) or any(not requirement.get(field) for field in required_fields):
            raise RequirementProfileError(f"{case_id} contains an incomplete requirement.")
        if requirement["status"] not in REQUIREMENT_STATUSES:
            raise RequirementProfileError(f"{case_id} requirement {requirement.get('id')} has invalid status.")
        if requirement["priority"] not in REQUIREMENT_PRIORITIES:
            raise RequirementProfileError(f"{case_id} requirement {requirement.get('id')} has invalid priority.")
        if not isinstance(requirement["source"], dict):
            raise RequirementProfileError(f"{case_id} requirement {requirement.get('id')} has invalid source.")
        normalized.append(requirement)
    identifiers = [requirement["id"] for requirement in normalized]
    if len(identifiers) != len(set(identifiers)):
        raise RequirementProfileError(f"{case_id} requirement profile contains duplicate requirement IDs.")
    return RequirementProfile(
        profile_id, case_id, name, status, str(document.get("version", "1.0")),
        document.get("approved_at"), tuple(normalized),
    )


def load_requirement_profile(connection, case_db_id):
    row = connection.execute(
        "SELECT profile_id, case_id, name, status, version, approved_at, criteria_json FROM requirement_profiles WHERE case_id = ?",
        (case_db_id,),
    ).fetchone()
    if row is None:
        return None
    return RequirementProfile(row[0], row[1], row[2], row[3], row[4], row[5], tuple(json.loads(row[6])))
