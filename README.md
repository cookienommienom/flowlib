# FlowLib

A Python library that extends `discord.py` to simplify creating workflows consisting of views with buttons. These buttons can perform actions or transition to other views. The library supports persistent flows using an asynchronous database backend with SQLAlchemy and is compatible with both SQLite and PostgreSQL.

## Features

- **Simplified Workflow Creation**: Easily create interactive workflows with minimal code.
- **Persistent Flows**: Workflows persist between bot restarts.
- **Asynchronous Database Support**: Uses SQLAlchemy's async ORM with support for `aiosqlite` (SQLite) and `asyncpg` (PostgreSQL).
- **User-Friendly Decorators**: Use `@button` and `@register_view` decorators to define buttons and views.

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/your_project.git
    cd your_project

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt

## Usage

### **1. Set Up Your Bot**

Create a bot script or use the provided example in `examples/bot.py`.

    ```bash
    import discord
    from discord.ext import commands
    from flowlib import initialize_flow_library, FlowView, button, register_view
    import asyncio

    bot = commands.Bot(command_prefix='!')

    # Initialize the flow library
    initialize_flow_library(bot)

    # Define your views and buttons using the decorators
    ...

    bot.run('YOUR_BOT_TOKEN')

### **2. Define Views and Buttons**

Use the `@register_view` and `@button` decorators to define your workflow steps and buttons.

    ```bash
    @register_view('start')
    class StartView(FlowView):
        ...


### **3. Run the Bot**

Start your bot by running your bot script.

    ```bash
    python bot.py

    ## Configuration

    ### **Database Configuration**

    By default, the library uses SQLite with `aiosqlite`. To use PostgreSQL with `asyncpg`, modify the `initialize_flow_library` call:

    ```bash
    initialize_flow_library(bot, database_url="postgresql+asyncpg://user:password@localhost/dbname")

Replace `user`, `password`, and `dbname` with your PostgreSQL credentials.

## Examples

Check out the `examples/` directory for a working example of how to use the library.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
