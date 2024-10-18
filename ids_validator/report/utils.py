from dataclasses import dataclass
from typing import List

from ids_validator.validate.result import (
    IDSValidationResult,
    IDSValidationResultCollection,
)


@dataclass
class CustomRuleObject:
    rule_name: str
    success: bool
    message: str
    traceback: str
    nodes: List[str]


@dataclass
class CustomResultCollection:
    ids: str
    occurrence: int
    result_list: List[IDSValidationResult]
    rules: List[CustomRuleObject]


def convert_result_into_custom_collection(
    validation_result: IDSValidationResultCollection,
) -> List[CustomResultCollection]:
    """ """
    result_collection: List[CustomResultCollection] = []

    for single_validation_result in validation_result.results:
        for ids, occurrence in single_validation_result.idss:
            if (ids, occurrence) not in [
                (x.ids, x.occurrence) for x in result_collection
            ]:
                result_collection.append(
                    CustomResultCollection(
                        ids=ids,
                        occurrence=occurrence,
                        result_list=[single_validation_result],
                        rules=[],
                    )
                )
            else:
                target_element = next(
                    x
                    for x in result_collection
                    if x.ids == ids and x.occurrence == occurrence
                )
                target_element.result_list.append(single_validation_result)

    for custom_result_collection in result_collection:
        ids = custom_result_collection.ids
        occurrence = custom_result_collection.occurrence
        # prepare output data and put it into single dictionary
        # this part of code focuses on putting all failed nodes under
        # single 'rule' entry
        for result_object in custom_result_collection.result_list:

            affected_node = list(result_object.nodes_dict.get((ids, occurrence), set()))

            if result_object.rule.name not in [
                custom_rule_object.rule_name
                for custom_rule_object in custom_result_collection.rules
            ]:
                custom_result_collection.rules.append(
                    CustomRuleObject(
                        rule_name=result_object.rule.name,
                        success=result_object.success,
                        message=result_object.msg,
                        traceback=str(result_object.tb[-1])
                        .replace("<", "")
                        .replace(">", ""),
                        nodes=affected_node,
                    )
                )

            else:
                target_cutom_rule_object = next(
                    rule_object
                    for rule_object in custom_result_collection.rules
                    if rule_object.rule_name == result_object.rule.name
                )
                target_cutom_rule_object.nodes += affected_node
    return result_collection
