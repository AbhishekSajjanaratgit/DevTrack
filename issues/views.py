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

        reporters = read_json(reporter.to_dict())
        write_json(REPORTERS_FILE, reporters)

        return Response(reporter.to_dict(), status=status.HTTP_201_CREATED)

class IssueView(APIView):

    def get(self, request):
        issues = read_json(ISSUES_FILE)