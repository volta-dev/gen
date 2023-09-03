exchange = "user"

types {
    CreateUser = {
        Username = ["string", "required"]
        Email = [string, required]
        Password = [string, required]
    }
    User = {
        Id = [string]
        Username = [string]
        Email = [string]
        Password = [string]
    }
}

actions {
    Register = {
        input = "CreateUser"
        output = "User"
        routing = "user.create"
    }

    GetUser = {
        input = "GetUser"
        output = "User"
        routing = "user.get"
    }
}