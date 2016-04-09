import yaml


class PermissionsManager:
    def __init__(self):
        self.dump = None
        self.load_permissions()

    def load_permissions(self):
        with open("config/permissions.yml", 'r') as stream:
            try:
                self.dump = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def has_permissions(self, member, permission):
        for role in member.roles:
            if self.has_group_permission(role.name.replace("@", ""), permission):
                return True

        return False

    def has_group_permission(self, group, permission):
        if self.dump is None:
            print('Failed to read permissions.yml.')
            return False
        permissions = self.dump['ranks'][group]['permissions']
        if permissions is not None and permission in permissions:
            return True
        else:
            if group != "everyone":
                return self.has_group_permission(self.dump['ranks'][group]['inherits'], permission)
            else:
                return False

    def save_permissions(self):
        with open('permissions.yml', 'w') as savefile:
            savefile.write(yaml.dump(self.dump, default_flow_style=True))
