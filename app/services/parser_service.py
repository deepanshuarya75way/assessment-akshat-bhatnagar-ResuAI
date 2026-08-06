import base64
import re


class EmailParser:

    @staticmethod
    def get_headers(payload):

        headers = {}

        for header in payload.get("headers", []):

            headers[header["name"]] = header["value"]

        return headers

    @staticmethod
    def get_body(payload):

        body = ""

        if "parts" in payload:

            for part in payload["parts"]:

                if part["mimeType"] == "text/plain":

                    data = part["body"].get("data")

                    if data:

                        body = base64.urlsafe_b64decode(
                            data
                        ).decode()

                        break

        else:

            data = payload["body"].get("data")

            if data:

                body = base64.urlsafe_b64decode(
                    data
                ).decode()

        return body

    @staticmethod
    def extract_links(text):

        pattern = r'https?://\S+'

        return re.findall(pattern, text)