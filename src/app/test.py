from datetime import date, timedelta
from sqlalchemy import case, func
from db.database import get_db
from models.all_models import SRT, Department, Location, ThematicArea, Unit, WorkPlan, WorkPlanSource

# def fetch_pending_work_plans_for_week(db_session):
#     current_week = date.today().isocalendar()[1]  # Week number of the year

#     # Define cases for implementing team based on workplan_source name
#     implementing_team = case(
#         [
#             (WorkPlanSource.name == "SRT", SRT.name),
#             (WorkPlanSource.name == "Unit", Unit.name),
#             (WorkPlanSource.name == "Department", Department.name),
#             (WorkPlanSource.name == "Thematic Area", ThematicArea.name),
#         ],
#         else_="Unknown"
#     )

#     # Query to fetch the required fields along with conditional implementing team
#     work_plans = db_session.query(
#         WorkPlan.activity_title,
#         WorkPlan.activity_date,
#         Location.name.label("location_name"),
#         WorkPlanSource.name.label("workplan_source_name"),
#         implementing_team.label("implementing_team")
#     ).join(
#         WorkPlan.locations
#     ).join(
#         WorkPlan.workplan_source
#     ).filter(
#         WorkPlan.status == "Pending",
#         func.extract('week', WorkPlan.activity_date) == current_week,
#         WorkPlan.activity_date >= date.today(),
#         WorkPlan.activity_date <= date.today() + timedelta(days=6 - date.today().weekday())
#     ).all()

#     return [{
#         "activity_title": wp.activity_title,
#         "activity_date": wp.activity_date.strftime('%Y-%m-%d'),
#         "location_name": wp.location_name,
#         "workplan_source_name": wp.workplan_source_name,
#         "implementing_team": wp.implementing_team
#     } for wp in work_plans]


def fetch_pending_work_plans_for_week(db_session):
    current_week = date.today().isocalendar()[1]  # Week number of the year

    # Define cases for implementing team based on workplan_source name
    implementing_team = case(
        [
            (WorkPlanSource.name == "SRT", SRT.name),
            (WorkPlanSource.name == "Unit", Unit.name),
            (WorkPlanSource.name == "Department", Department.name),
            (WorkPlanSource.name == "Thematic Area", ThematicArea.name),
        ],
        else_="Unknown"
    )

    # Query to fetch the required fields along with conditional implementing team
    work_plans = db_session.query(
        WorkPlan.activity_title,
        WorkPlan.activity_date,
        Location.name.label("location_name"),
        WorkPlanSource.name.label("workplan_source_name"),
        implementing_team.label("implementing_team")
    ).join(
        WorkPlan.locations
    ).join(
        WorkPlan.workplan_source
    ).filter(
        WorkPlan.status == "Pending"
    ).all()

    return [{
        "activity_title": wp.activity_title,
        "activity_date": wp.activity_date.strftime('%Y-%m-%d'),
        "location_name": wp.location_name,
        "workplan_source_name": wp.workplan_source_name,
        "implementing_team": wp.implementing_team
    } for wp in work_plans]

# Usage example
db_session = get_db()  # Assuming this gets a session
print(fetch_pending_work_plans_for_week(db_session))
