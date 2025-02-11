from dataclasses import field, dataclass


@dataclass
class Component:
    id: int = field(
        default=None, metadata={"desc": "Id of the component"}
    )
    name: str = field(
        default=None, metadata={"desc": "Description of the component"}
    )
    bound: list = field(
        default=None, metadata={"desc": "Bound of the component"}
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bound': self.bound,
        }