from string import Formatter


class PromptTemplate:
    def __init__(self, name, template):
        self.name = name
        self.template = template

    def __call__(self, **kwargs):
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            required_keys = set(
                [x[1] for x in Formatter().parse(self.template) if x[1]]
            )
            missing_keys = required_keys - set(kwargs.keys())
            raise KeyError(f"Missing keys: {', '.join(missing_keys)}") from e
