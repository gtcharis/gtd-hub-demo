from app.role_policy import permissions_for_role, role_can_access_institution

def test_programme_admin_has_full_institution_permissions():
    permissions = permissions_for_role("Programme Administrator")
    assert "institution:read_all" in permissions
    assert "institution:manage_all" in permissions
    assert "programme:manage" in permissions

def test_organisation_admin_is_not_granted_cross_institution_permissions():
    permissions = permissions_for_role("Organisation Administrator")
    assert "institution:read" in permissions
    assert "institution:read_all" not in permissions
    assert "institution:manage_all" not in permissions

def test_institution_scope_policy():
    assert role_can_access_institution("Programme Administrator", None, 99)
    assert role_can_access_institution("Organisation Administrator", 4, 4)
    assert not role_can_access_institution("Organisation Administrator", 4, 5)
    assert not role_can_access_institution("Member", 4, 4)
