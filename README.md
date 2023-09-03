# 🐰 volta-gen
⚡Automatically generate functions to process and send messages to RabbitMQ using Volta Gen.

### 📥 Installation
```bash
pip install git+https://github.com/volta-dev/gen.git
```

### 📖 Usage
To use volta-gen, you need to create schema files with __.volta__ extension.
The schema files are used to generate the functions that will be used to process and send messages to RabbitMQ.

Schema files have the following structure:
```hcl
exchange = "user" # rabbitmq exchange name for this service

types { # DTO types what we can use in actions
    CreateUser = {
        Username = ["string"] # first element in array is a type,
                              # second is tags what will be done soon
    }
}

actions { # actions what we can call from client
    Register = {
        input = "CreateUser" # input is a CreateUser type
        output = "" # no output from this action
        routing = "user.create" # rabbitmq routing key
    }
}
```

### 🚀 Running

```bash
volta-gen -f ./schema.volta -o ./output.go
```
