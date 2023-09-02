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
```
exchange = "user" # exchange name, required field.

types { # types used in the schema, required block.
    CreateUser { # DTO struct name with block start.
        name string # field name and type.
        email int # field name and type.
        password bool # field name and type.
    }
    ReturnUser {
        id int
    }
}

actions { # actions, required block. There you declare the functions that will be generated.
    Register(ReturnUser) ReturnUser @routingKey("user.register") # function name, func argument, return type, routing key.
    
    # You can also declare functions without return type and without arguments.
    <functionName>(<function argument, optional>) <returnValue, optional> @routingKey("<routing key, required>")
}
```

### 🚀 Running

```bash
volta-gen -f ./schema.volta -o ./output.go
```
