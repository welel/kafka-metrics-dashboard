import enum


class ControlCommands(str, enum.Enum):
    """Control commands for the parser consumer.

    Commands:
        dashboard - get the dashboard data.

    """
    DASHBOARD = "dashboard"
