import os
import json
from flask import current_app
from spark.placement_analysis import run_spark_analysis


class SparkService:
    """Service providing distributed processing capabilities through PySpark integration."""

    @classmethod
    def get_latest_spark_results(cls, auto_run_if_missing: bool = True) -> dict:
        """
        Retrieve existing cached PySpark analysis results or execute distributed processing.
        """
        output_dir = current_app.config.get('SPARK_OUTPUT_DIR')
        result_file = os.path.join(output_dir, 'spark_analysis_results.json')

        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading spark output file: {e}")

        if auto_run_if_missing:
            return cls.trigger_spark_job()

        return {'success': False, 'message': 'No PySpark results available.'}

    @classmethod
    def trigger_spark_job(cls) -> dict:
        """
        Execute PySpark distributed processing job directly from Flask backend.
        Exports database records or uses sample data CSV as source.
        """
        data_path = current_app.config.get('DATA_PATH')
        output_dir = current_app.config.get('SPARK_OUTPUT_DIR')

        try:
            results = run_spark_analysis(csv_path=data_path, output_dir=output_dir)
            return results
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'java_guidance': 'PySpark requires Java 8/11/17/21/25 installed with JAVA_HOME environment variable set.'
            }

