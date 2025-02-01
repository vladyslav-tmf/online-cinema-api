from abc import ABC, abstractmethod
from typing import Union


class S3StorageInterface(ABC):
    @abstractmethod
    def upload_file(self, file_name: str, file_data: Union[bytes, bytearray]) -> None:
        pass

    @abstractmethod
    def get_file_url(self, file_name: str) -> str:
        pass
