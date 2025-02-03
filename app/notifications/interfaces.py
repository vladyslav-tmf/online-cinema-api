from abc import ABC, abstractmethod


class EmailSenderInterface(ABC):

    @abstractmethod
    def send_activation_email(self, email: str, activation_link: str) -> None:
        pass

    @abstractmethod
    def send_activation_complete_email(self, email: str, login_link: str) -> None:
        pass

    @abstractmethod
    def send_password_reset_email(self, email: str, reset_link: str) -> None:
        pass

    @abstractmethod
    def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        pass

    @abstractmethod
    def send_payment_success_email(
            self,
            email: str,
            user_name: str,
            amount: str,
            watch_link: str
    ) -> None:
        pass
