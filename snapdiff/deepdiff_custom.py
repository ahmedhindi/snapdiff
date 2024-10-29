from deepdiff.operator import BaseOperator
from pathlib import Path
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.compose import ColumnTransformer


class PathComparisonOperator(BaseOperator):
    def match(self, level):
        # Ensure both objects at this level are Path instances
        return isinstance(level.t1, Path) and isinstance(level.t2, Path)

    def give_up_diffing(self, level, diff_instance):
        # Convert paths to lowercase and resolve for comparison
        path1, path2 = map(
            lambda p: p.resolve().as_posix().lower(), (level.t1, level.t2)
        )
        if path1 != path2:
            # Use custom_report_result to add a custom difference entry
            diff_instance.custom_report_result(
                "path_difference", level, {"old_value": path1, "new_value": path2}
            )
            return True  # Stop further diffing at this level
        return False  # Paths are the same, continue with standard diffing


class compareDataFrames(BaseOperator):
    def __init__(self, shallow_diff=True):
        self.shallow_diff = shallow_diff

    def match(self, level):
        from pandas import DataFrame

        # Only match when both objects are DataFrames
        return isinstance(level.t1, DataFrame) and isinstance(level.t2, DataFrame)

    def shalow_diff(self, level):
        diff_shape = False

        shadow_diff = {}
        if level.t1.shape != level.t2.shape:
            shadow_diff["shape"] = {
                "old_value": level.t1.shape,
                "new_value": level.t2.shape,
            }
            diff_shape = True

        old_cols = set(level.t1.columns)
        new_cols = set(level.t2.columns)
        if old_cols != new_cols:
            shadow_diff["columns"] = {
                "columns in old df not in new": old_cols - new_cols,
                "columns in new df not in old": new_cols - old_cols,
            }

        old_types_dict = level.t1.dtypes.to_dict()
        new_types_dict = level.t2.dtypes.to_dict()
        types_diff = {}
        for col in old_cols.intersection(new_cols):
            if old_types_dict[col] != new_types_dict[col]:
                types_diff[col] = {
                    "old_value": old_types_dict[col],
                    "new_value": new_types_dict[col],
                }
        if types_diff:
            shadow_diff["column_types"] = types_diff

        if not diff_shape:
            # index changed
            if not level.t1.index.equals(level.t2.index):
                shadow_diff["index"] = "index changed"

        return shadow_diff

    def give_up_diffing(self, level, diff_instance):
        if self.shallow_diff:
            diff = self.shalow_diff(level)
            if diff:
                diff_instance.custom_report_result("DataFrame_difference", level, diff)
                return True
        return False


class CompareSeries(BaseOperator):
    def __init__(self, shallow_diff=True):
        self.shallow_diff = shallow_diff

    def match(self, level):
        from pandas import Series

        # Only match when both objects are Series
        return isinstance(level.t1, Series) and isinstance(level.t2, Series)

    def shalow_diff(self, level):
        diff_shape = False
        shadow_diff = {}
        old_len = len(level.t1)
        new_len = len(level.t2)
        if old_len != new_len:
            shadow_diff["shape"] = {
                "old_value": old_len,
                "new_value": new_len,
            }
            diff_shape = True
        if not diff_shape:
            # index changed
            if not level.t1.index.equals(level.t2.index):
                shadow_diff["index"] = "index changed"
        return shadow_diff

    def give_up_diffing(self, level, diff_instance):
        if self.shallow_diff:
            diff = self.shalow_diff(level)
            if diff:
                diff_instance.custom_report_result("Series_difference", level, diff)
                return True
        return False


class CompareSkModels(BaseOperator):
    def __init__(self, shallow_diff=True):
        self.shallow_diff = shallow_diff

    def match(self, level):
        from sklearn.base import BaseEstimator

        # Only match when both objects are Series
        return isinstance(level.t1, BaseEstimator) and isinstance(
            level.t2, BaseEstimator
        )

    def shalow_diff(self, level):
        shadow_diff = {}
        if level.t1.get_params() != level.t2.get_params():
            shadow_diff["params"] = {
                "old_value": level.t1.get_params(),
                "new_value": level.t2.get_params(),
            }
        return shadow_diff

    def give_up_diffing(self, level, diff_instance):
        if self.shallow_diff:
            diff = self.shalow_diff(level)
            if diff:
                diff_instance.custom_report_result("Model_difference", level, diff)
                return True
        return False


def get_pipeline_params(pipeline):
    def retrieve_params(step, step_name=""):
        params_dict = {}

        if isinstance(step, Pipeline):
            # Handle standard pipeline
            for sub_step_name, sub_step in step.steps:
                full_step_name = (
                    f"{step_name}__{sub_step_name}" if step_name else sub_step_name
                )
                params_dict[full_step_name] = retrieve_params(sub_step, full_step_name)

        elif isinstance(step, FeatureUnion):
            # Handle FeatureUnion specifically
            for sub_step_name, sub_step in step.transformer_list:
                full_step_name = (
                    f"{step_name}__{sub_step_name}" if step_name else sub_step_name
                )
                params_dict[full_step_name] = retrieve_params(sub_step, full_step_name)

        elif isinstance(step, ColumnTransformer):
            # Handle ColumnTransformer specifically
            for sub_step_name, sub_step, _ in step.transformers:
                full_step_name = (
                    f"{step_name}__{sub_step_name}" if step_name else sub_step_name
                )
                params_dict[full_step_name] = retrieve_params(sub_step, full_step_name)

        else:
            # Handle individual transformers or estimators
            params_dict = step.get_params()

        return params_dict

    return retrieve_params(pipeline)


class CompareSklearnPipeline(BaseOperator):
    def __init__(self, shallow_diff=True):
        self.shallow_diff = shallow_diff

    def match(self, level):
        from sklearn.pipeline import Pipeline

        # Only match when both objects are Pipelines
        return isinstance(level.t1, Pipeline) and isinstance(level.t2, Pipeline)

    def get_diff(self, level):
        diff = {}
        old_params = get_pipeline_params(level.t1)
        new_params = get_pipeline_params(level.t2)
        if old_params != new_params:
            diff["params"] = {
                "old_value": old_params,
                "new_value": new_params,
            }
        return diff

    def give_up_diffing(self, level, diff_instance):
        if self.shallow_diff:
            diff = self.get_diff(level)
            if diff:
                diff_instance.custom_report_result("Pipeline_difference", level, diff)
                return True
        return False


df_diff_types = [
    compareDataFrames(),
    CompareSeries(),
    CompareSkModels(),
    CompareSklearnPipeline(),
    PathComparisonOperator(),
]
