import jsonschema  # type: ignore

param_kind_schema = {
    'enum': ['POSITIONAL_OR_KEYWORD', 'VAR_POSITIONAL',
             'KEYWORD_ONLY', 'VAR_KEYWORD'],
}

api_schema = {
    "$id": "pidiff-schema",
    "type": "object",
    "properties": {
        # name of symbol within current namespace - e.g. module name,
        # class or function name.
        "name": {"type": "string"},

        # file containing symbol, if known
        "file": {"type": "string"},

        # line number where symbol was declared, if known
        "lineno": {"type": "integer"},

        # true if this is outside of any tested roots
        "is_external": {"type": "boolean"},

        # true if this symbol is callable
        "is_callable": {"type": "boolean"},

        # signature of callable - all parameters, in defined order
        "signature": {
            "type": "array",
            "items": [
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "kind": param_kind_schema,
                        "has_default": {"type": "boolean"},
                    },
                    "required": ["name", "kind", "has_default"],
                }
            ]
        },

        # For display purposes only
        "symbol_type": {
            "enum": ["function", "class", "module", "object"],
        },

        # children of this symbol (e.g. classes within a module,
        # functions within a class, properties within an object)
        "children": {
            "type": "array",
            "items": {"$ref": "pidiff-schema"},
        }
    },
    "required": ["name", "is_external", "is_callable", "symbol_type"]
}


def validate(instance):
    return jsonschema.validate(instance, api_schema)
