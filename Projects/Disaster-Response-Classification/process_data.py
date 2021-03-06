import argparse

from project.config import (
    DEFAULT_CATEGORIES_FILE_PATH,
    DEFAULT_MESSAGES_FILE_PATH,
    DEFAULT_DB_OUTPUT_FILE_PATH,
    SQL_TABLE_NAME
)

from project.preprocessing.wrangling import (
    merge_messages_and_categories,
    expand_categories,
    categories_to_integers,
    replace_categories_columns,
    drop_duplicates,
    drop_columns_with_too_many_nan_values,
    remove_single_value_categories
)

from project.utils.file_utils import load_csv

from project.utils.db_utils import (
    get_database_engine,
    df_to_sql_table
)

parser = argparse.ArgumentParser()
parser.add_argument("--messages_path",
                    help="Absolute path to messages data .csv file.",
                    default=DEFAULT_MESSAGES_FILE_PATH,
                    type=str)

parser.add_argument("--categories_path",
                    help="Absolute path to categories data .csv file.",
                    default=DEFAULT_CATEGORIES_FILE_PATH,
                    type=str)

parser.add_argument("--db_path",
                    help="Absolute path for .db file where output of etl pipeline will be saved.",
                    default=DEFAULT_DB_OUTPUT_FILE_PATH,
                    type=str)


def etl_pipeline_assembly():
    """Function which loads .csv files with disaster messages and their multi-categories. It merges, cleans the data,
    and saves the final result in sql database file of .db format. Path to files and output file are passed via
    Python args.
    """
    args = parser.parse_args()

    df_messages = load_csv(args.messages_path)
    df_categories = load_csv(args.categories_path)

    df_data = merge_messages_and_categories(df_messages, df_categories)

    df_categories_extended = expand_categories(df_data)
    df_categories_extended = categories_to_integers(df_categories_extended)

    df_data = replace_categories_columns(df_data, df_categories_extended)
    df_data = drop_duplicates(df_data)
    df_data = drop_columns_with_too_many_nan_values(df_data)
    df_data = remove_single_value_categories(df_data)

    df_to_sql_table(df_data, SQL_TABLE_NAME, get_database_engine(args.db_path))


if __name__ == "__main__":
    etl_pipeline_assembly()
