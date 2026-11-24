"""Central role-to-permission policy for GTD Hub v0.2.5.

Programme Administrators have full programme-wide access across institutions.
Organisation Administrators are restricted to their own institution.
"""
from types import MappingProxyType

ROLE_PERMISSIONS = MappingProxyType({
    "Member": frozenset({
        "dashboard:read", "support:read", "reporting:create",
        "mentorship:read", "community:read", "learning:read",
    }),
    "Mentor": frozenset({
        "dashboard:read", "mentorship:read", "mentorship:manage_own",
        "community:read", "learning:read",
    }),
    "Moderator": frozenset({
        "dashboard:read", "community:read", "community:moderate", "learning:read",
    }),
    "Case Handler": frozenset({
        "dashboard:read", "support:read", "cases:read", "cases:manage",
    }),
    "Organisation Administrator": frozenset({
        "dashboard:read", "organisation:read", "organisation:manage_users",
        "administration:read", "institution:read",
    }),
    "Programme Administrator": frozenset({
        "dashboard:read", "support:read", "reporting:create",
        "mentorship:read", "mentorship:manage_own",
        "community:read", "community:moderate", "learning:read",
        "cases:read", "cases:manage",
        "organisation:read", "organisation:manage_users",
        "administration:read", "institution:read",
        "institution:read_all", "institution:manage_all",
        "programme:read", "programme:manage",
    }),
})

ALL_PERMISSIONS = frozenset(
    permission for permissions in ROLE_PERMISSIONS.values() for permission in permissions
)

def permissions_for_role(role: str) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(role, frozenset())

def role_has_permission(role: str, permission: str) -> bool:
    return permission in permissions_for_role(role)

def role_can_access_institution(role: str, user_institution_id: int | None, target_institution_id: int) -> bool:
    if role == "Programme Administrator":
        return True
    if role == "Organisation Administrator":
        return user_institution_id is not None and user_institution_id == target_institution_id
    return False
