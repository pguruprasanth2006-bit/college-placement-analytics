import pandas as pd
import numpy as np
import pytest
from app.models import Placement
from app.services.analytics_service import AnalyticsService


def test_empty_dataset_handling():
    """Verify that empty DataFrame does not raise division by zero or errors."""
    empty_df = pd.DataFrame(columns=[
        'student_id', 'register_number', 'name', 'cgpa', 'arrears', 'graduation_year',
        'department_name', 'department_code', 'is_placed', 'salary', 'company_name'
    ])
    summary = AnalyticsService.generate_summary_metrics(empty_df)
    assert summary['total_students'] == 0
    assert summary['placement_percentage'] == 0.0
    assert summary['average_package'] == 0.0

    dept_stats = AnalyticsService.department_wise_analytics(empty_df)
    assert dept_stats == []

    comp_stats = AnalyticsService.company_wise_analytics(empty_df)
    assert comp_stats == []


def test_placement_percentage_and_salary_stats(db, seed_basic_data):
    """Test accurate computation of placement percentage and salary stats."""
    alice = seed_basic_data['student_alice']
    google = seed_basic_data['comp_google']

    # Record placement for Alice
    placement = Placement(
        student_id=alice.id,
        company_id=google.id,
        status='Selected',
        salary=22.0
    )
    db.session.add(placement)
    db.session.commit()

    summary = AnalyticsService.generate_summary_metrics()
    assert summary['total_students'] == 2
    assert summary['total_placed'] == 1
    assert summary['total_unplaced'] == 1
    assert summary['placement_percentage'] == 50.0
    assert summary['average_package'] == 22.0
    assert summary['highest_package'] == 22.0


def test_department_wise_calculations(db, seed_basic_data):
    """Test department level breakdown statistics."""
    alice = seed_basic_data['student_alice']
    google = seed_basic_data['comp_google']

    placement = Placement(
        student_id=alice.id,
        company_id=google.id,
        status='Selected',
        salary=20.0
    )
    db.session.add(placement)
    db.session.commit()

    dept_stats = AnalyticsService.department_wise_analytics()
    assert len(dept_stats) == 2

    cse_stat = next(d for d in dept_stats if d['department_code'] == 'CSE')
    assert cse_stat['total_students'] == 1
    assert cse_stat['placed_students'] == 1
    assert cse_stat['placement_percentage'] == 100.0

    mech_stat = next(d for d in dept_stats if d['department_code'] == 'MECH')
    assert mech_stat['total_students'] == 1
    assert mech_stat['placed_students'] == 0
    assert mech_stat['placement_percentage'] == 0.0

