# Workplan Management System

This Workplan Management System is designed to streamline the process of creating, approving, and managing workplans within an organization. It provides functionalities for vehicle allotment, role-based access control, and real-time updates on workplan statuses.

## Key Features

- **Workplan Management**: Users can create, submit for approval, and manage workplans.
- **Vehicle Allotment**: Manage and allocate vehicles for employee use.
- **User Roles and Permissions**: System access is controlled through customizable user roles and permissions.
- **Real-Time Updates**: Users receive updates on workplan changes and approvals.
- **Multi-Tenant Support**: Supports multiple tenants or departments within a single instance.

## Database Models Overview

The system's data structure is organized into several models, each representing a different aspect of the system:

- **User Roles and Users**: Manage user authentication, roles, and their associated permissions.
- **Tenancy**: Supports multiple tenants or departments within the system.
- **Employees and Departments**: Organize employees within departments and manage their associated details.
- **Work Plans**: Core of the system where work plans are created, reviewed, and approved.
- **Sites and Locations**: Manage geographical locations and sites where work plans are executed.
- **Trips and Vehicles**: Handle logistics related to vehicle management and trip planning.
- **Issues and Meetings**: Track issues arising from work plans and manage meetings and action points.

### Model Relationships

- Users can have multiple roles and belong to specific departments or tenancies.
- Work plans are associated with employees, sites, and can be linked to specific trips for logistical purposes.
- Vehicles are assigned to trips and require regular maintenance, which is also tracked within the system.
- Issues can be logged against work plans or trips and are managed through meetings where action points are assigned.

## Getting Started

To set up the system locally for development or testing, follow these steps:

1. Clone the repository:
 git clone https://github.com/nelson-ust/workplan_manager.git


2. Install dependencies:

pip install -r requirements.txt

