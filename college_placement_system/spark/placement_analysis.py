import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'sample_placement_data.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'spark', 'output')


def get_spark_session():
    """
    Initialize and return a configured SparkSession.
    Configured for local distributed processing with graceful fallback.
    """
    try:
        from pyspark.sql import SparkSession
        spark = (
            SparkSession.builder
            .appName("CollegePlacementAnalyticsEngine")
            .master("local[2]")
            .config("spark.driver.host", "127.0.0.1")
            .config("spark.driver.bindAddress", "127.0.0.1")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )
        return spark
    except Exception as e:
        print(f"Warning: SparkSession initialization failed: {e}")
        print("Note: PySpark requires a compatible Java JRE/JDK (Java 8/11/17/21/25) on your system path.")
        return None


def run_spark_analysis(csv_path=None, output_dir=None):
    """
    Perform distributed placement data analysis using PySpark DataFrames.
    Calculates department, company, salary, and year-wise aggregates.
    Saves and returns structured JSON analytical results.
    """
    if csv_path is None:
        csv_path = DATA_PATH
    if output_dir is None:
        output_dir = OUTPUT_DIR

    os.makedirs(output_dir, exist_ok=True)

    spark = get_spark_session()
    if spark is None:
        return {
            'success': False,
            'error': 'SparkSession could not be initialized. Please ensure Java is installed and JAVA_HOME is configured.',
            'timestamp': str(os.path.getmtime(csv_path) if os.path.exists(csv_path) else '')
        }

    try:
        from pyspark.sql import functions as F

        print(f"Loading data into PySpark from: {csv_path}")
        df = spark.read.csv(csv_path, header=True, inferSchema=True)

        total_records = df.count()
        placed_df = df.filter(F.col("placement_status") == "Placed")
        total_placed = placed_df.count()

        # 1. Overall Metrics
        salary_stats = placed_df.select(
            F.round(F.avg("salary"), 2).alias("avg_salary"),
            F.round(F.max("salary"), 2).alias("max_salary"),
            F.round(F.min("salary"), 2).alias("min_salary")
        ).first()

        avg_salary = float(salary_stats["avg_salary"]) if salary_stats["avg_salary"] is not None else 0.0
        max_salary = float(salary_stats["max_salary"]) if salary_stats["max_salary"] is not None else 0.0
        min_salary = float(salary_stats["min_salary"]) if salary_stats["min_salary"] is not None else 0.0
        placement_pct = round((total_placed / total_records * 100), 2) if total_records > 0 else 0.0

        overall_metrics = {
            'total_students': total_records,
            'total_placed': total_placed,
            'total_unplaced': total_records - total_placed,
            'placement_percentage': placement_pct,
            'average_salary': avg_salary,
            'highest_salary': max_salary,
            'minimum_salary': min_salary
        }

        # 2. Department-wise Aggregation
        dept_df = df.groupBy("department").agg(
            F.count("register_number").alias("total_students"),
            F.sum(F.when(F.col("placement_status") == "Placed", 1).otherwise(0)).alias("placed_students"),
            F.round(F.avg(F.when(F.col("placement_status") == "Placed", F.col("salary")).otherwise(None)), 2).alias("avg_salary"),
            F.round(F.max(F.when(F.col("placement_status") == "Placed", F.col("salary")).otherwise(None)), 2).alias("max_salary")
        ).withColumn(
            "placement_percentage",
            F.round((F.col("placed_students") / F.col("total_students")) * 100.0, 2)
        ).orderBy(F.col("placement_percentage").desc())

        dept_results = [row.asDict() for row in dept_df.collect()]

        # 3. Company-wise Recruitment Statistics
        company_df = placed_df.filter(F.col("company_name").isNotNull() & (F.col("company_name") != "")).groupBy("company_name").agg(
            F.count("register_number").alias("placed_count"),
            F.round(F.avg("salary"), 2).alias("avg_package"),
            F.round(F.max("salary"), 2).alias("max_package")
        ).orderBy(F.col("placed_count").desc())

        company_results = [row.asDict() for row in company_df.collect()]

        # 4. Year-wise Placement Analysis
        year_df = df.groupBy("graduation_year").agg(
            F.count("register_number").alias("total_students"),
            F.sum(F.when(F.col("placement_status") == "Placed", 1).otherwise(0)).alias("placed_students"),
            F.round(F.avg(F.when(F.col("placement_status") == "Placed", F.col("salary")).otherwise(None)), 2).alias("avg_package")
        ).withColumn(
            "placement_percentage",
            F.round((F.col("placed_students") / F.col("total_students")) * 100.0, 2)
        ).orderBy(F.col("graduation_year").asc())

        year_results = [row.asDict() for row in year_df.collect()]

        results = {
            'success': True,
            'engine': f'PySpark {spark.version}',
            'overall_metrics': overall_metrics,
            'department_aggregates': dept_results,
            'company_statistics': company_results,
            'year_trends': year_results
        }

        # Save to output file
        output_file = os.path.join(output_dir, 'spark_analysis_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)

        print(f"PySpark analysis finished. Results saved to {output_file}")
        return results

    finally:
        try:
            spark.stop()
        except Exception:
            pass


if __name__ == '__main__':
    res = run_spark_analysis()
    print("PySpark Execution Result:", "Success" if res.get('success') else "Failed")

