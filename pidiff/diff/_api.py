import os


class InternalError(RuntimeError):
    pass


class Signature:
    def __init__(self, raw):
        self._raw = raw

    @property
    def named_kwargs(self):
        out = set()
        for param in self._raw:
            if param['kind'] in ['POSITIONAL_OR_KEYWORD', 'KEYWORD_ONLY']:
                out.add(param['name'])
        return out

    @property
    def has_var_keyword(self):
        return any([param['kind'] == 'VAR_KEYWORD' for param in self._raw])


class Api:
    def __init__(self, raw, parent=None):
        self._raw = raw
        self.parent = parent

    @property
    def file(self):
        return self._raw.get('file')

    @property
    def is_callable(self):
        return self._raw['is_callable']

    @property
    def is_external(self):
        return self._raw['is_external']

    @property
    def signature(self):
        if not self.is_callable:
            raise InternalError('signature called on non-callable')
        return Signature(self._raw.get('signature'))

    @property
    def lineno(self):
        return self._raw.get('lineno') or 0

    @property
    def display_file(self):
        full_path = self.file
        if full_path:
            return os.path.relpath(full_path, os.getcwd())
        return ''

    @property
    def symbol_type(self):
        return self._raw['symbol_type']

    @property
    def name(self):
        return self._raw['name']

    @property
    def version(self):
        return self._raw.get('version')

    @property
    def children(self):
        children_raw = self._raw.get('children') or []
        return [Api(x, self) for x in children_raw]

    @property
    def children_by_name(self):
        return {api.name: api for api in self.children}
