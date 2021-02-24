# Command class to define what a User object will be

class User:
    def __init__(self, name, roles):
        self.name = name
        self.roles = roles
    
    # Used to check if a user has the required permission
    def hasPermission(self, requiredRole):
        pass