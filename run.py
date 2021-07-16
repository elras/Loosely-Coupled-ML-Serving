from azure.servicebus import ServiceBusClient, ServiceBusReceiveMode, TransportType
import requests
import json
import os
import signal
from network import Classify


class Worker(object):
    __slots__ = ["classifier", "bus_queue_name", "_exit"]

    def __init__(self):
        """Download custom weights here from a blob storage if necessary"""
        self.classify = Classify(tuned_weights=None)
        self.bus_queue_name = ""  # SET the queue name
        self._exit = False
        signal.signal(signal.SIGTERM, self._set_exit_signal)

    def _set_exit_signal(self, signum, frame):
        """To handle K8s SIGTERM, see https://docs.python.org/3/library/signal.html"""
        self._exit = True

    def _download_image(self, sas_url):
        """Download image from a blob storage"""
        pass

    def _upload_results(self, results):
        """Upload outputs (e.g., to a blob storage or (No)SQL Server)"""
        pass

    def receive(self):
        try:
            # See deploy.sh for setting env. variables
            servicebus_client = ServiceBusClient.from_connection_string(
                conn_str=os.environ["SERVICE_BUS_CONNECTION_STRING"],
                transport_type=TransportType.Amqp,
                retry_total=3,
                retry_backoff_factor=5,
                logging_enable=True,
            )

            with servicebus_client:
                receiver = servicebus_client.get_queue_receiver(
                    queue_name=self.bus_queue_name,
                    receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                    max_wait_time=None,
                )

                with receiver:
                    for message in receiver:
                        if not self._exit:
                            data = json.loads(str(message))

                            try:
                                # ----------- Inference block ---------- #
                                image = self._download_image(data["blob_url"])
                                class_probobalities = self.classifier(image)
                                # -------------------------------------------- #

                                resp = requests.post(
                                    data["function_event_url"],
                                    json=True, # Notify durable function it succeeded
                                    timeout=10,
                                    headers={"Content-Type": "application/json"},
                                )

                                if resp.status_code == 200:
                                    receiver.complete_message(message)
                                    self._upload_results(class_probobalities)
                                else:
                                    # Failed due to request-reply issue, log here
                                    receiver.dead_letter_message(
                                        message,
                                        reason=str(resp.status_code),
                                        error_description="reply-error",
                                    )

                            except Exception as exception_instance:
                                # Failed due to exception, log here
                                receiver.dead_letter_message(
                                    message,
                                    reason=str(exception_instance),
                                    error_description="python-error",
                                )
                                _ = requests.post(
                                    data["function_event_url"],
                                    json=False, # Notify durable function it failed
                                    timeout=10,
                                    headers={"Content-Type": "application/json"},
                                )

                        else:
                            # Stop the container after receiving K8s SIGTERM
                            receiver.abandon_message(message)
                            return True

        except Exception as exception_instance:
            # General failure, log here
            raise


if __name__ == "__main__":
    worker = Worker()
    worker.receive()
