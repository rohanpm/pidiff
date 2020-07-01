import shlex
import os


class PipArgs:
    def __init__(self, pidiff_args, workdir=None):
        self.pidiff_args = pidiff_args
        self.workdir = workdir or os.getcwd()

    def _absolutize(self, path):
        # if path is relative and points at an existing file,
        # then return absolute form of the path.
        if not os.path.isabs(path):
            candidate = os.path.join(self.workdir, path)
            candidate = os.path.abspath(candidate)
            if os.path.exists(candidate):
                return candidate
        return path

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
            out.extend(["-r", self._absolutize(x)])

        for x in self.pidiff_args.constraint or []:
            out.extend(["-c", self._absolutize(x)])

        if self.pidiff_args.pre:
            out.append("--pre")

        return out
