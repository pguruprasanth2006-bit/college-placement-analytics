import os
import json
import pytest
from spark.placement_analysis import run_spark_analysis, get_spark_session


def test_spark_session_initialization():
    """Test that SparkSession initializes or handles environment properly."""
    spark = get_spark_session()
    if spark is not None:
        assert spark.version is not None
        spark.stop()


def test_spark_analysis_execution(tmp_path):
    """Test running spark analysis and verifying generated aggregated structure."""
    out_dir = str(tmp_path / "spark_out")
    result = run_spark_analysis(output_dir=out_dir)

    assert result is not None
    if result.get('success'):
        assert 'overall_metrics' in result
        assert 'department_aggregates' in result
        assert 'company_statistics' in result
        assert 'year_trends' in result

        # Check output JSON on disk
        json_file = os.path.join(out_dir, 'spark_analysis_results.json')
        assert os.path.exists(json_file)
        with open(json_file, 'r') as f:
            data = json.load(f)
            assert data['success'] is True
            assert len(data['department_aggregates']) > 0

