from abc import ABC, abstractmethod
from datetime import datetime

VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}

class BaseEntity(ABC):
    """
    Abstract base for every entity.  
    Subclasses must implement validate().
    """

    @abstractmethod
    def validate(self):
        pass

    def to_dict(self):
        return {key : value for key, value in self.__dict__.items()}

# Reporter model
class Reporter(BaseEntity):

    def __init__(self,id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        """Validate the reporter object"""

        if not isinstance(self.id, int):
            raise ValueError("Reporter Id must be an intger")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Name cannot be empty")
        if not isinstance(self.email, str) or "@" not in self.email:
            raise ValueError("Invalid Email")

class Issue(BaseEntity):

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        self.created-at = created_at or str(datetime.now())

    def validate(self):
        if not isinstance(self.id, int):
            raise ValueError("Issue Id must be Integer")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"Invalid Status. Must be one of : {', '.join(sorted(VALID_STATUSES))}"
            )
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid propertiy. Must be one of : {', '.join(sorted(VALID_PRIORITIES))}"
            )
        if not isinstance(self.reporter_id, int):
            raise ValueError("Reported_id must be an Integer")

    def describe(self):
        return f"{self.title} [{self.priority}]"

class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} -- needs immediate attention"

class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} -- low priority, handle when free"
        



        