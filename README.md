# Policy Catalog

A standalone command-line application for managing insurance policy
types using Python and SQLite. It supports creating, viewing, filtering,
updating, and deleting policy records.

## Features

-   Create policy types with an automatically generated Policy ID.
-   View all saved policies.
-   Filter policies by category.
-   Update policy details using the Policy ID.
-   Delete policies by ID after confirmation.
-   Store records persistently in SQLite.
-   Validate policy names, categories, premium ranges, and coverage
    amounts.
-   Insert fictional sample records during startup without duplicating
    existing sample records.

## Technology Stack

-   **Language:** Python 3
-   **Database:** SQLite (`sqlite3`, included with Python)
-   **Interface:** Command-line menu

No external database server is required.

## Project Structure

``` text
policy_catalog/
├── main.py          # Command-line menu and application flows
├── database.py      # SQLite connection and database operations
├── policy_catalog.db  # SQLite database; created automatically
└── README.md        # Project documentation
```

The database file is generated automatically when the application
initializes. Do not commit real customer, policyholder, claims, KYC, or
payment data.

## Requirements

-   Python 3 installed
-   A terminal or command prompt

Check your Python installation:

``` powershell
python --version
```

## How to Run

1.  Open a terminal in the project directory.

2.  Run the application:

    ``` powershell
    python main.py
    ```

3.  Use the displayed menu to select an operation.

The application initializes the SQLite database when it starts. If the
sample-data seeding function is enabled in `main.py`, it checks and
inserts the sample records without duplicating matching name/category
pairs.

## Menu Options

  -----------------------------------------------------------------------
  Option                  Operation               Description
  ----------------------- ----------------------- -----------------------
  1                       Create Policy           Add a policy with its
                                                  name, category, minimum
                                                  premium, maximum
                                                  premium, and coverage
                                                  amount.

  2                       View Policies           View all policies or
                                                  filter by category.

  3                       Update Policy           Update a policy by its
                                                  ID.

  4                       Delete Policy           Review a policy and
                                                  confirm before deleting
                                                  it.

  5                       Exit                    Close the application.
  -----------------------------------------------------------------------

## Policy Fields

  Field               Description
  ------------------- -------------------------------------------
  `policy_type_id`    Automatically generated unique identifier
  `name`              Policy name
  `category`          Insurance category
  `min_premium`       Minimum premium amount
  `max_premium`       Maximum premium amount
  `coverage_amount`   Coverage amount offered by the policy

## Validation Rules

-   Policy name cannot be empty.
-   Policy name must be unique within its category.
-   Category must be one of: `Motor`, `Health`, `Life`, `Travel`,
    `Home`, or `Other`.
-   Minimum and maximum premiums must be positive numbers.
-   Minimum premium must be less than maximum premium.
-   Coverage amount must be positive and at least equal to the maximum
    premium.
-   Invalid or nonexistent policy IDs should produce a clear message
    rather than crash the application.
-   Deletion requires confirmation.

### Category Update Decision

Changing a policy's category after creation is allowed. The new category
must be in the approved list, and the resulting policy name/category
combination must remain unique.

## Sample Data

The application can seed fictional sample policies across the allowed
categories, such as Motor Comprehensive, Family Health Insurance, Term
Life Secure, Travel Protect Plus, Home Shield, and Personal Accident
Cover.

Only fictional test data should be used.

## Database and Persistence

The application uses SQLite and stores data in `policy_catalog.db` in
the project directory. Records remain saved after the application closes
and restarts. Policy IDs may have gaps after records are deleted; IDs
are not intended to be consecutive.

## Manual Test Checklist

-   [ ] Create a valid policy and confirm that an ID is generated.
-   [ ] View all policies.
-   [ ] Filter by a category and confirm only matching policies appear.
-   [ ] Filter a category with no records and confirm a "No policies
    found" message appears.
-   [ ] Reject an empty policy name.
-   [ ] Reject a category outside the allowed list.
-   [ ] Reject non-positive premiums, a minimum premium greater than or
    equal to the maximum, and non-positive coverage.
-   [ ] Reject a duplicate name in the same category.
-   [ ] Update a policy and confirm the stored values change.
-   [ ] Try updating or deleting a nonexistent ID.
-   [ ] Delete an existing policy with confirmation and verify it
    remains deleted after restarting.
-   [ ] Restart the application and verify records persist and sample
    data is not duplicated.

## Git Workflow

Commit the work in meaningful stages, for example:

1.  Set up SQLite database and schema.
2.  Implement policy creation and validation.
3.  Implement listing and category filtering.
4.  Implement policy updates.
5.  Implement deletion with confirmation.
6.  Add sample data and documentation.

Push the completed branch to the repository and open a pull request for
review according to your team's Git workflow.

## Scope

This is a small standalone policy-type catalog. It is not a customer
policy management, claims, KYC, or payment system.
