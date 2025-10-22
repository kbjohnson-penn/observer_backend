"""
Database router for Observer platform.

Routes models to appropriate databases based on app labels:
- accounts app -> accounts database (observer_accounts)
- clinical app -> clinical database (observer_clinical)
- research app -> research database (observer_research)
"""


class DatabaseRouter:
    """
    A router to control all database operations on models
    """

    route_app_labels = {
        "accounts": "accounts",
        "clinical": "clinical",
        "research": "research",
        # Route Django's auth models to accounts database
        "auth": "accounts",
        "contenttypes": "accounts",
        "sessions": "accounts",
        "admin": "accounts",
        "token_blacklist": "accounts",
    }

    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if model._meta.app_label in self.route_app_labels:
            return self.route_app_labels[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if model._meta.app_label in self.route_app_labels:
            return self.route_app_labels[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations only within the same database."""
        return obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label in self.route_app_labels:
            return db == self.route_app_labels[app_label]
        elif db in self.route_app_labels.values():
            # If the database is one of the routed databases, but the app is not routed to it, don't migrate.
            return False
        # For any other app (Django built-ins), only migrate to 'default' database
        return db == "default"
