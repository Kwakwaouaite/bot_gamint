

class PermissionManager:
    master_roles = []
    upper_bound_role = None

    # Met à jour le role "Master"
    def add_master_role(self, role):
        self.master_roles.append(role)

    def remove_master_role(self, role):
        self.master_roles.remove(role)

    def check_master_permission(self, author):
        for e in self.master_roles:
            if e in author.roles:
                return True
        return False

    def updt_upper_bound_role(self, role):
        self.upper_bound_role = role

    # Check if the role is one we can freely join
    def check_join_permission(self, role):
        if not self.upper_bound_role:
            return True
        else:
            return self.upper_bound_role > role
