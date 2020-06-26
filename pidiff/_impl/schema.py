import jsonschema  # type: ignore

param_kind_schema = {
    "enum": ["POSITIONAL_OR_KEYWORD", "VAR_POSITIONAL", "KEYWORD_ONLY", "VAR_KEYWORD"]
}

ref_pattern = "^[0-9a-f\\-]+$"

optional_boolean = {"enum": [True, False, None]}

children_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "ref": {"type": "string", "regex": ref_pattern},
        },
        "required": ["name", "ref"],
        "additionalProperties": False,
    },
}

object_schema = {
    "type": "object",
    "properties": {
        # file where object is declared, if known
        # (note: this concept is sort of broken,
        # this should be moved to the symbol)
        "file": {"type": "string"},
        # line number where object was declared, if known
        "lineno": {"type": "integer"},
        # true if object lives outside of any tested roots
        "is_external": optional_boolean,
        # true if object is callable
        "is_callable": optional_boolean,
        # signature of callable - all parameters, in defined order
        "signature": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "kind": param_kind_schema,
                    "has_default": {"type": "boolean"},
                },
                "required": ["name", "kind", "has_default"],
                "additionalProperties": False,
            },
        },
        # For display purposes only
        "object_type": {"enum": ["function", "method", "class", "module", "object"]},
        # children of this object (e.g. classes within a module,
        # functions within a class, properties within an object)
        "children": children_schema,
    },
    "required": ["is_external", "is_callable", "object_type"],
    "additionalProperties": False,
}

object_db_schema = {
    "type": "object",
    "patternProperties": {ref_pattern: object_schema},
    "additionalProperties": False,
}

root_schema = {
    "type": "object",
    "properties": {
        # name of root
        "name": {"type": "string"},
        # version of object, if available (e.g. from __version__ or
        # from egg metadata)
        "version": {"type": "string"},
        # reference to the module object
        "ref": {"type": "string", "regex": ref_pattern},
    },
    "required": ["name", "ref"],
    "additionalProperties": False,
}

dump_schema = {
    "type": "object",
    "properties": {"root": root_schema, "objects": object_db_schema},
    "required": ["root", "objects"],
    "additionalProperties": False,
}


class BadRefException(ValueError):
    pass


def validate(instance) -> None:
    # jsonschema validation
    jsonschema.validate(instance, dump_schema)

    # now ensure all object refs are OK
    object_db = instance["objects"]
    root_ref = instance["root"]["ref"]
    if root_ref not in object_db:
        raise BadRefException("Missing object for root ref %s" % root_ref)

    for ob_data in object_db.values():
        refs = [child["ref"] for child in ob_data.get("children", [])]
        for ref in refs:
            if ref not in object_db:
                raise BadRefException("Missing object for ref %s" % ref)
