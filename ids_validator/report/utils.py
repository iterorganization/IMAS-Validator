from dataclasses import dataclass
from typing import List

from ids_validator.validate.result import (
    IDSValidationResult,
    IDSValidationResultCollection,
)


@dataclass
class CustomRuleObject:
    """
    Represents single rule applied to data being validated.
    It is a helper class used during report generation.
    """

    rule_name: str
    message: str
    traceback: str
    passed_nodes: List[str]
    failed_nodes: List[str]


@dataclass
class CustomResultCollection:
    """
    Stores all validation data for single (ids, occurrence) pair.
    It is a helper class used during report generation.
    """

    ids: str
    occurrence: int
    result_list: List[IDSValidationResult]
    rules: List[CustomRuleObject]


def convert_result_into_custom_collection(
    validation_result: IDSValidationResultCollection,
) -> List[CustomResultCollection]:
    """
    Converts IDSValidationResultCollection into List[CustomResultCollection]
    in order to group validation results by (ids, occurrence)

    Args:
        validation_result: IDSValidationResultCollection - validation result

    Returns:
        List[CustomResultCollection]
    """
    # This function has two steps:

    # 1. Put (ids, occurrence) pair and List[IDSValidationResult]
    # together in CustomResultCollection objects

    # 2. Extract rules that failed from List[IDSValidationResult]
    # and also put them in CustomResultCollection

    result_collection: List[CustomResultCollection] = []

    # Step 1:
    for single_validation_result in validation_result.results:
        for ids, occurrence in single_validation_result.idss:
            if (ids, occurrence) not in [
                (x.ids, x.occurrence) for x in result_collection
            ]:
                # If object representing (ids, occurrence) doesn't exists
                result_collection.append(
                    CustomResultCollection(
                        ids=ids,
                        occurrence=occurrence,
                        result_list=[single_validation_result],
                        rules=[],
                    )
                )
            else:
                # If it already exists, find element and
                # append IDSValidationResult into it's result list
                target_element = next(
                    x
                    for x in result_collection
                    if x.ids == ids and x.occurrence == occurrence
                )
                target_element.result_list.append(single_validation_result)

    # Step 2:
    # For every ids:occurrence
    for custom_result_collection in result_collection:
        ids = custom_result_collection.ids
        occurrence = custom_result_collection.occurrence

        # For every IDSValidationResult in custom structure
        for result_object in custom_result_collection.result_list:

            affected_nodes = list(
                result_object.nodes_dict.get((ids, occurrence), set())
            )
            # If there is no CustomRuleObject in CustomResultCollection.rules
            # that matches result_object.rule.name: create new CustomRuleObject
            if result_object.rule.name not in [
                custom_rule_object.rule_name
                for custom_rule_object in custom_result_collection.rules
            ]:
                new_custom_rule_object = CustomRuleObject(
                    rule_name=result_object.rule.name,
                    message=result_object.msg,
                    traceback=str(result_object.tb[-1])
                    .replace("<", "")
                    .replace(">", ""),
                    passed_nodes=[],
                    failed_nodes=[],
                )
                if result_object.success:
                    new_custom_rule_object.passed_nodes += affected_nodes
                else:
                    new_custom_rule_object.failed_nodes += affected_nodes
                custom_result_collection.rules.append(new_custom_rule_object)

            else:
                # If CustomRuleObject already exists, just append list of affected nodes
                target_custom_rule_object = next(
                    rule_object
                    for rule_object in custom_result_collection.rules
                    if rule_object.rule_name == result_object.rule.name
                )
                if result_object.success:
                    target_custom_rule_object.passed_nodes += affected_nodes
                else:
                    if affected_nodes:
                        target_custom_rule_object.failed_nodes += affected_nodes
                    else:  # if rule failed, but no node is affected, add empty string
                        target_custom_rule_object.failed_nodes.append("")

    # sort result collection alphabetically
    result_collection = sorted(result_collection, key=lambda x: (x.ids, x.occurrence))

    # sort rule lists alphabetically
    for custom_result_collection in result_collection:
        custom_result_collection.rules = sorted(
            custom_result_collection.rules, key=lambda x: x.rule_name
        )

        for rule_object in custom_result_collection.rules:
            rule_object.passed_nodes.sort()
            rule_object.failed_nodes.sort()

    return result_collection
