from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Reporter, Issue, CriticalIssue, LowPriorityIssue, VALID_STATUSES
)

from .storage import (
    read_json, write_json, ISSUES_FILE, REPORTERS_FILE
)

def error(message, code=status.HTTP_400_BAD_REQUEST):
    return Response({"error" : message}, status=code)

def missing_fileds(data, required):
    return [f for f in required if f not in data]

def find_by_id(records, record_id):
    for record in records:
        if record["id"] == record_id:
            return record

    return None

class ReporterView(APIView):

    def get(self, request):
        reporters = read_json(REPORTERS_FILE)
        raw_id = request.query_params.get("id")

        if raw_id is None:
            return Response(reporters, status=status.HTTP_200_OK)

        try:
            reporter_id = int(raw_id)
        except ValueError:
            return error("Id must be an Integer")

        reporter = find_by_id(reporters, reporter_id)

        if reporter is None:
            return error("Reporter not found", status.HTTP_404_NOT_FOUND)

        return Response(reporter, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data

        if not isinstance(data, dict):
            return error("Request body must be a JSON object")

        missing = missing_fileds(data, ["id","name","email","team"])

        if missing:
            return error(f"Missing fileds :  {', '.join(missing)}")

        reporter = Reporter(data["id"], data["name"], data["email"], data["team"])

        try:
            reporter.validate()
        except ValueError as e:
            return error(str(e))

        reporters = read_json(REPORTERS_FILE)
        if find_by_id(reporters, reporter.id) is not None:
            return error("Reporter id already exists")

        reporters.append(reporter.to_dict())
        write_json(REPORTERS_FILE, reporters)

        return Response(reporter.to_dict(), status=status.HTTP_201_CREATED)

class IssueView(APIView):

    def get(self, request):
        issues = read_json(ISSUES_FILE)
        raw_id = request.query_params.get("id")
        status_filter = request.query_params.get("status")

        # id takes priority over status when both are sent

        if raw_id is not None:
            try:
                issue_id = int(raw_id)
            except ValueError:
                return error("Id must be an Integer")

            issue =find_by_id(issues, issue_id)
            if issue is None:
                return error("Issue not found", status.HTTP_404_NOT_FOUND)
            return Response(issue, status.HTTP_200_OK)

        if status_filter is not None:
            if status_filter not in VALID_STATUSES:
                return error(
                    "Invalid status. Must be one of :"
                    + ", ".join(sorted(VALID_STATUSES))
                )
            issues = [i for i in issues if i["status"] == status_filter]

        return Response(issues, status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        if not isinstance(data, dict):
            return error("Request body must be a JSON object")

        missing = missing_fileds(
            data,
            ["id","title","description","status","priority","reporter_id"]
        )
        if missing:
            return error(f"Missing fields : {', '.join(missing)}")

        # Pick the subclass from the priority
        fields = (
            data["id"], data["title"], data["description"], data["status"], data["priority"], data["reporter_id"],
        )

        if data["priority"] == "critical":
            issue = CriticalIssue(*fields)
        elif data["priority"] == "low":
            issue = LowPriorityIssue(*fields)
        else:
            issue = Issue(*fields)

        try:
            issue.validate()
        except ValueError as e:
            return error(str(e))
        except TypeError:
            return error("status and priority must be strings")

        # Validation passed. Now check with the stored data
        if find_by_id(read_json(REPORTERS_FILE), issue.reporter_id) is None:
            return error(f"Reporter with id {issue.reporter_id} does not exists.")

        issues = read_json(ISSUES_FILE)
        if find_by_id(issues, issue.id) is not None:
            return error("Issue id already exists.")

        issues.append(issue.to_dict())
        write_json(ISSUES_FILE, issues)

        response_data = issue.to_dict()
        response_data["message"] = issue.describe()

        return Response(response_data, status=status.HTTP_201_CREATED)
    

