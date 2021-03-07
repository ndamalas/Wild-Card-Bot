# Command class to define what a command object will be

class Command:
    # Name will be the name of the command and what you call it by
    # Function will be the specific function that the command runs found in the module
    # Module will be the module that the function will be found in
    def __init__(self, name, function, description=None):
        self.name = name
        self.function = function
        self.description = description
        self.module = None
    
    # Used to call the command
    async def callCommand(self, client, message):
        # Here We will put the logic to call functions from modules
        call = getattr(self.module, self.function)
        await call(client, message)
                