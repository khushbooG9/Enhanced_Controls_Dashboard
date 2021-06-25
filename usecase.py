class Config:
    key: str
    value: str
    data_type: str

    @staticmethod
    def from_json():
        pass

class UseCase:
    name: str
    is_rule_based: bool
    priority: int
    configuration: dict(str, Config)

    