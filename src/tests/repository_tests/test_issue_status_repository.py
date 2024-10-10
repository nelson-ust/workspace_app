import sys
import os

# Add the `src` directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))

import pytest
from unittest import mock
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

# Adjust the imports to match your project structure
from app.models.all_models import IssueStatus
from app.repositories.issue_status_repository import IssueStatusRepository
from app.schemas.issue_status_schemas import IssueStatusCreate, IssueStatusUpdate

@pytest.fixture
def db_session():
    return mock.Mock()

@pytest.fixture
def issue_status_repo(db_session):
    return IssueStatusRepository(db_session)

def test_create_issue_status_success(issue_status_repo, db_session, mocker):
    issue_status_data = IssueStatusCreate(status="New Status")
    db_session.query.return_value.filter.return_value.first.return_value = None
    issue_status = IssueStatus(id=1, status="New Status")
    issue_status_repo.create = mocker.Mock(return_value=issue_status)

    result = issue_status_repo.create_issue_status(issue_status_data)

    assert result.status == "New Status"
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()

def test_create_issue_status_duplicate(issue_status_repo, db_session):
    issue_status_data = IssueStatusCreate(status="Duplicate Status")
    existing_issue_status = IssueStatus(id=1, status="Duplicate Status")
    db_session.query.return_value.filter.return_value.first.return_value = existing_issue_status

    with pytest.raises(HTTPException) as exc_info:
        issue_status_repo.create_issue_status(issue_status_data)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "An issue_status with the name Duplicate Status already exists"

def test_update_issue_status_success(issue_status_repo, db_session):
    issue_status_data = IssueStatusUpdate(status="Updated Status")
    existing_issue_status = IssueStatus(id=1, status="Old Status")
    db_session.query.return_value.get.return_value = existing_issue_status
    db_session.commit.return_value = None

    result = issue_status_repo.update_issue_status(1, issue_status_data)

    assert result.status == "Updated Status"
    db_session.commit.assert_called_once()

def test_update_issue_status_not_found(issue_status_repo, db_session):
    issue_status_data = IssueStatusUpdate(status="Updated Status")
    db_session.query.return_value.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        issue_status_repo.update_issue_status(1, issue_status_data)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "An issue_status with the id 1 does not exist"

def test_get_all_issue_status_success(issue_status_repo, db_session):
    issue_status_list = [IssueStatus(id=1, status="Status 1"), IssueStatus(id=2, status="Status 2")]
    db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = issue_status_list

    result = issue_status_repo.get_all_issue_status()

    assert len(result) == 2
    assert result[0].status == "Status 1"
    assert result[1].status == "Status 2"

def test_get_issue_status_by_id_success(issue_status_repo, db_session):
    issue_status = IssueStatus(id=1, status="Status")
    db_session.query.return_value.get.return_value = issue_status

    result = issue_status_repo.get_issue_status_by_id(1)

    assert result.status == "Status"

def test_get_issue_status_by_id_not_found(issue_status_repo, db_session):
    db_session.query.return_value.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        issue_status_repo.get_issue_status_by_id(1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Failed to retrieve issue_status"

def test_delete_issue_status_success(issue_status_repo, db_session, mocker):
    issue_status = IssueStatus(id=1, status="Status")
    db_session.query.return_value.get.return_value = issue_status
    db_session.commit.return_value = None

    issue_status_repo.delete_hard = mocker.Mock()

    issue_status_repo.delete_issue_status(1)

    issue_status_repo.delete_hard.assert_called_once_with(1)
    db_session.commit.assert_called_once()

def test_delete_issue_status_not_found(issue_status_repo, db_session):
    db_session.query.return_value.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        issue_status_repo.delete_issue_status(1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "issue_status 1 not found"
