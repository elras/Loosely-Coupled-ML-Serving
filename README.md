### Accompanying code for the InfoQ article: Benefits of Loosely Coupled Deep Learning Serving
This is a basic template deployment code to Azure, hence specific details are avoided for brevity. The idea is extensible and cloud/language agnostic

#### Procedure
- Check [run.py]("") and change it according to your needs (how to download input images, upload output results etc.)
- Create the initial Azure resources from portal/cli according to the previous step: K8s cluster, Container Registry, Service Bus (queue), Azure Storage (blob), and optional database
- Create an Azure Durable function (enabling event server) and an optional API Management Service to handle external API requests. This part is not descirbed in the repo, see the official example: https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-external-events?tabs=python#send-events
- Add your dependencies to [requirements.txt]("")
- Run [init_k8s.sh]("") after connecting to the created K8s cluster
- Set container image details and run [build_push_container.sh]("")
- Set deployment details in [deploy.sh]("") and run it to complete setting up pods
- We are ready to go (:
