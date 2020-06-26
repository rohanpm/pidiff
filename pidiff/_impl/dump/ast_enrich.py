import logging
import uuid
from typing import Optional

import astroid
from astroid.nodes import AssignAttr, FunctionDef, ClassDef, Name
from astroid.node_classes import NodeNG

LOG = logging.getLogger("pidiff.ast")


class AstEnricher:
    ERROR = object()

    def __init__(self):
        self._parsed_files = {}

    def parse(self, filename) -> Optional[NodeNG]:
        out = self._parsed_files.get(filename)
        if out is self.ERROR:
            return None
        if out:
            return out

        try:
            with open(filename) as f:
                out = astroid.parse(f.read())
            self._parsed_files[filename] = out
        except Exception:
            LOG.debug("Can't parse %s", filename, exc_info=True)
            self._parsed_files[filename] = self.ERROR
            out = None

        return out

    def enrich_object(self, object_dump, o):
        if o.get("object_type") != "class":
            # we only know how to enrich classes at the moment
            return

        file = o.get("file")
        lineno = o.get("lineno")

        # if any location info is missing, we can't match up with AST
        if not file or not lineno:
            LOG.debug("Can't enrich due to missing location: %s", o)
            return

        file_node = self.parse(file)
        if not file_node:
            LOG.debug("Can't enrich, could not parse: %s", o)
            return

        class_def = self.find_class_def(file_node, lineno)
        if not class_def:
            LOG.debug("Can't enrich, no ClassDef matched: %s", o)
            return

        self.add_assigns(object_dump, o, class_def)

    def add_assigns(self, object_dump, o, class_def):
        attr_assigns = []

        remaining = [class_def]
        while remaining:
            next_node = remaining.pop()
            remaining.extend(next_node.get_children())

            if not isinstance(next_node, AssignAttr):
                continue

            function_def = next_node.frame()
            if not isinstance(function_def, FunctionDef):
                continue

            if function_def.name != "__init__":
                continue

            parent_frame = function_def.parent.frame()
            if parent_frame is not class_def:
                continue

            assign_expr = next_node.expr
            if not isinstance(assign_expr, Name):
                continue
            if assign_expr.name != "self":
                continue

            attr_assigns.append(next_node)

        for assign in attr_assigns:
            name = assign.attrname
            if name.startswith("_"):
                continue

            ref = str(uuid.uuid4())
            obj = {
                "object_type": "object",
                "file": o["file"],
                "lineno": assign.lineno,
                "is_external": None,
                "is_callable": None,
            }
            object_dump[ref] = obj
            o.setdefault("children", []).append({"name": name, "ref": ref})

    def find_class_def(self, node, lineno) -> Optional[ClassDef]:
        remaining = [node]
        while remaining:
            next_node = remaining.pop()
            if isinstance(next_node, ClassDef) and next_node.lineno == lineno:
                return next_node
            remaining.extend(next_node.get_children())
        return None

    def run(self, raw_dump: dict):
        object_dump = raw_dump.get("objects") or {}
        object_values = [o for o in object_dump.values()]

        for o in object_values:
            self.enrich_object(object_dump, o)
