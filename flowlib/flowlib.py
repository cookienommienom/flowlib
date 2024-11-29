# flowlib/flowlib.py

import discord
import inspect
import uuid
import asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

# Internal variables (not exposed to users)
_Base = declarative_base()
_engine = None
_SessionLocal = None
_bot_instance = None

def initialize_flow_library(bot, database_url="sqlite+aiosqlite:///flowlib.db"):
    """
    Initialize the flow library with the bot instance and database configuration.

    Parameters:
    - bot: The instance of the discord.py bot.
    - database_url: Database URL for SQLAlchemy (async).
    """
    global _engine, _SessionLocal, _bot_instance

    _engine = create_async_engine(database_url, echo=False)
    _SessionLocal = async_sessionmaker(bind=_engine, expire_on_commit=False)
    _bot_instance = bot

    # Register the on_ready event handler
    bot.add_listener(_on_bot_ready)

async def _on_bot_ready():
    # Create tables if they don't exist
    async with _engine.begin() as conn:
        await conn.run_sync(_Base.metadata.create_all)

    # Load active states and register views
    async with _SessionLocal() as session:
        result = await session.execute(_UserState.__table__.select())
        active_states = result.fetchall()
        for state in active_states:
            user_id = state.user_id
            step = state.step
            view_class = _get_view_class_for_step(step)
            if view_class:
                view = view_class(user_id=user_id)
                _bot_instance.add_view(view)
    print(f'Flow library initialized and views registered.')

def _get_view_class_for_step(step):
    return _VIEW_REGISTRY.get(step)

# Internal UserState model
class _UserState(_Base):
    __tablename__ = 'user_states'
    user_id = Column(String, primary_key=True)
    step = Column(String)
    confirmed = Column(Boolean)

# Decorator to register views
_VIEW_REGISTRY = {}

def register_view(step_name):
    def decorator(cls):
        _VIEW_REGISTRY[step_name] = cls
        return cls
    return decorator

def button(label, style=discord.ButtonStyle.primary, next_step=None, custom_id=None, **kwargs):
    """
    Decorator to define a button on a FlowView.

    Parameters:
    - label: The text displayed on the button.
    - style: The button style.
    - next_step: The name of the next step/view.
    - custom_id: Custom identifier for the button (optional).
    - **kwargs: Additional keyword arguments for discord.ui.Button.
    """
    def decorator(func):
        func._button_config = {
            'label': label,
            'style': style,
            'custom_id': custom_id or str(uuid.uuid4()),
            **kwargs
        }
        func._next_step = next_step
        return func
    return decorator

class FlowView(discord.ui.View):
    def __init__(self, *, timeout=None, user_id=None):
        super().__init__(timeout=timeout)
        self.user_id = str(user_id)
        self._build_buttons()

    def _build_buttons(self):
        for _, method in inspect.getmembers(self, predicate=inspect.iscoroutinefunction):
            if hasattr(method, '_button_config'):
                config = method._button_config
                button = discord.ui.Button(**config)
                button.callback = self._wrap_callback(method)
                self.add_item(button)

    def _wrap_callback(self, method):
        async def callback(interaction: discord.Interaction):
            await method(self, interaction)
            next_step = getattr(method, '_next_step', None)
            if next_step:
                view_class = _get_view_class_for_step(next_step)
                if view_class:
                    view = view_class(user_id=self.user_id)
                    await interaction.response.edit_message(view=view)
                    # Re-register the new view
                    _bot_instance.add_view(view)
                else:
                    await interaction.response.defer()
            else:
                await interaction.response.defer()
        return callback

    async def update_state(self, **kwargs):
        """Update the user's state in the database."""
        async with _SessionLocal() as session:
            state = await session.get(_UserState, self.user_id)
            if not state:
                state = _UserState(user_id=self.user_id)
                session.add(state)
            for key, value in kwargs.items():
                setattr(state, key, value)
            await session.commit()

    async def get_state(self):
        """Retrieve the user's state from the database."""
        async with _SessionLocal() as session:
            state = await session.get(_UserState, self.user_id)
            return state
