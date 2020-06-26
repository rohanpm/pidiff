import shlex


class PipArgs:
    def __init__(self, pidiff_args):
        self.pidiff_args = pidiff_args

    @property
    def excluding_requirements(self):
        out = []

        if self.pidiff_args.index_url:
            out.extend(["-i", self.pidiff_args.index_url])

        for url in self.pidiff_args.extra_index_url or []:
            out.extend(["--extra-index-url", url])

        if self.pidiff_args.pip_args:
            out.extend(shlex.split(self.pidiff_args.pip_args))

        return out

    @property
    def all(self):
        out = self.excluding_requirements

        for x in self.pidiff_args.requirement or []:
            out.extend(["-r", x])

        for x in self.pidiff_args.constraint or []:
            out.extend(["-c", x])

        if self.pidiff_args.pre:
            out.append("--pre")

        return out
