from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.auth import login_required
from app.services.analytics_service import AnalyticsService
from app.services.spark_service import SparkService

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/')
@login_required
def index():
    """Render comprehensive analytics powered by Pandas and NumPy, with PySpark section."""
    summary = AnalyticsService.generate_summary_metrics()
    dept_stats = AnalyticsService.department_wise_analytics()
    company_stats = AnalyticsService.company_wise_analytics()
    year_stats = AnalyticsService.year_wise_analytics()
    cgpa_stats = AnalyticsService.cgpa_vs_placement_analytics()

    # Fetch latest PySpark analysis results
    spark_data = SparkService.get_latest_spark_results(auto_run_if_missing=False)

    return render_template(
        'analytics.html',
        summary=summary,
        dept_stats=dept_stats,
        company_stats=company_stats,
        year_stats=year_stats,
        cgpa_stats=cgpa_stats,
        spark_data=spark_data
    )


@analytics_bp.route('/spark-run', methods=['POST'])
@login_required
def run_spark():
    """Trigger distributed PySpark analysis from web interface."""
    results = SparkService.trigger_spark_job()
    if results.get('success'):
        flash('PySpark distributed job completed successfully!', 'success')
    else:
        error_msg = results.get('error', 'Execution failed')
        flash(f'PySpark Execution Note: {error_msg}', 'warning')
    return redirect(url_for('analytics.index'))

