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


class Symbol:
    def __init__(self, dump, full_name, object_ref):
        self.dump = dump
        self.full_name = full_name
        self.object_ref = object_ref

    @property
    def version(self):
        # Could support different versions here
        return self.dump['root'].get('version')

    @classmethod
    def from_root(cls, dump):
        root = dump['root']
        full_name = root['name']
        return cls(dump, full_name, root['ref'])

    @property
    def object_data(self):
        return self.dump['objects'][self.object_ref]

    @property
    def ob(self):
        return Object(self.dump, self.object_data)

    @property
    def name(self):
        return self.full_name.split('.')[-1]

    @property
    def children(self):
        out = []
        for child_raw in self.object_data.get('children') or []:
            child_full_name = '.'.join([self.full_name, child_raw['name']])
            ref = child_raw['ref']
            out.append(Symbol(self.dump, child_full_name, ref))
        return out

    @property
    def children_by_name(self):
        return {child.name: child for child in self.children}

    @property
    def display_name(self):
        return self.full_name

    # These location properties are available on the symbol
    # because they really *should* be defined on the symbol rather
    # than the objects (future TODO)
    @property
    def file(self):
        return self.ob.file

    @property
    def lineno(self):
        return self.ob.lineno

    @property
    def display_file(self):
        return self.ob.display_file


class Object:
    def __init__(self, dump, raw):
        self.dump = dump
        self.raw = raw

    @property
    def file(self):
        return self.raw.get('file')

    @property
    def is_callable(self):
        return self.raw['is_callable']

    @property
    def is_external(self):
        return self.raw['is_external']

    @property
    def signature(self):
        if not self.is_callable:
            raise InternalError('signature called on non-callable')
        return Signature(self.raw.get('signature'))

    @property
    def lineno(self):
        return self.raw.get('lineno') or 0

    @property
    def display_file(self):
        full_path = self.file
        if full_path:
            # Make relative to root module
            root_file = Symbol.from_root(self.dump).file
            parent_dir = os.path.dirname(os.path.dirname(root_file))
            if parent_dir in ('', '.'):
                return full_path
            return os.path.relpath(full_path, parent_dir)
        return ''

    @property
    def object_type(self):
        return self.raw['object_type']

    # children comes from symbol and not object
    # @property
    # def children(self):
    #     children_raw = self._raw.get('children') or []
    #     return [Api(x, self) for x in children_raw]
