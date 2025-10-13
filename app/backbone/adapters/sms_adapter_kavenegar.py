# adapters/sms/kavenegar_adapter.py
import asyncio
from kavenegar import KavenegarAPI, APIException, HTTPException  # type: ignore
from typing import Optional, List, Union
import logging


class SMSAdapter:
    """
    Adapter class for interacting with Kavenegar SMS service.
    """

    def __init__(self, api_key: str, sender: Optional[str] = None):
        """
        Initialize the Kavenegar adapter.

        :param api_key: API key from Kavenegar panel
        :param sender: Optional sender number (e.g., "1000xxxx")
        """
        self.api_key = api_key
        self.sender = sender
        try:
            self.api = KavenegarAPI(api_key)
        except Exception as e:
            logging.error("Failed to initialize KavenegarAPI: %s", e)
            raise e

    async def send_sms(
        self,
        receptor: Union[str, List[str]],
        message: str,
        sender: Optional[str] = None,
    ) -> bool:
        """
        Send an SMS message via Kavenegar.

        :param receptor: recipient phone number or list of numbers
        :param message: text message to send
        :param sender: optional sender number (overrides default)
        :return: True if sent successfully, False otherwise
        """
        try:
            params = {
                "receptor": receptor,
                "message": message,
                "sender": sender or self.sender,
            }

            response = self.api.sms_send(params)
            logging.info("SMS sent successfully: %s", response)
            return True

        except HTTPException as e:
            logging.error("HTTPException while sending SMS: %s", e)
        except APIException as e:
            logging.error("APIException while sending SMS: %s", e)
        except Exception as e:
            logging.error("Unexpected error: %s", e)

        return False

    async def verify_lookup(self, receptor: str, token: str, template: str) -> bool:
        """
        Send a verification SMS using predefined template (Lookup API).

        :param receptor: recipient phone number
        :param token: token or code to insert in message
        :param template: name of template in Kavenegar panel
        :return: True if sent successfully
        """
        try:
            params = {
                "receptor": receptor,
                "token": token,
                "template": template,
            }
            response = self.api.verify_lookup(params)
            logging.info("Verification SMS sent: %s", response)
            return True
        except (HTTPException, APIException) as e:
            logging.error("Error in verify_lookup: %s", e)
        return False


async def main():
    api_key = "5661426B7A486A717448424C52486C38346654574B33744967624F5A4F706234333055724836526969396F3D"
    sender = "2000660110"
    sms = SMSAdapter(api_key, sender)

    # ارسال پیام ساده
    success = await sms.send_sms("09904572066", "سلام! این یک پیام تستی است.")
    print("SMS sent:", success)

    # ارسال پیام با الگو (template)
    # verify = await sms.verify_lookup(
    #     "09904572066", token="12345", template="verify-code"
    # )
    # print("Verify SMS:", verify)


if __name__ == "__main__":

    asyncio.run(main())
