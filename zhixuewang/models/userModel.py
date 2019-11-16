from .personModel import schoolModel, personModel
from .urlModel import TEST_URL


class User(personModel):
    def __init__(self, session):
        super().__init__()
        self._session = session
        self.role = ""
    
    def change_password(self):
        raise NotImplementedError()

    def _get_info(self):
        raise NotImplementedError()
    