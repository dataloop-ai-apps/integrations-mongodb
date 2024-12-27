import os
import logging
import dtlpy as dl
from pymongo import MongoClient
from bson import ObjectId

logger = logging.getLogger(name="mongodb-connect")


class MongodbBase(dl.BaseServiceRunner):
    """
    A class for running a service that interacts with MongoDB.
    """

    def __init__(self):
        """
        Initializes the ServiceRunner with MongoDB credentials.
        """
        self.logger = logger

    def get_client(
        self,
        username: str,
        host: str,
        db_name: str,
        collection: str,
    ):
        """
        Retrieves a MongoClient object for the specified MongoDB server.

        :param username: The username for the MongoDB server.
        :param host: The hostname of the MongoDB server.
        :param db_name: The name of the MongoDB database.
        :param collection: The name of the MongoDB collection.
        :return: A MongoClient object for the specified server.
        """

        self.logger.info(
            "Executing query on server '%s' for collection '%s'.", host, collection
        )

        password = os.environ.get("MONGODB_PASSWORD")

        return MongoClient(
            f"mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority"
        )

    def mongodb_to_dataloop(
        self,
        username: str,
        host: str,
        db_name: str,
        collection: str,
        dataset_id: str,
    ):
        """
        Creates a PromptItem for each document in the specified MongoDB collection and uploads them to the specified Dataloop dataset.

        :param username: The username for the MongoDB server.
        :param host: The hostname of the MongoDB server.
        :param db_name: The name of the MongoDB database.
        :param collection: The name of the MongoDB collection.
        :param dataset_id: The ID of the Dataloop dataset.
        :return: A list of the uploaded PromptItems or None if an error occurs.
        """

        self.logger.info(
            "Creating table for dataset '%s' and collection '%s'.",
            dataset_id,
            collection,
        )

        try:
            dataset = dl.datasets.get(dataset_id=dataset_id)
            self.logger.info("Successfully retrieved dataset with ID '%s'.", dataset_id)
        except dl.exceptions.NotFound as e:
            self.logger.error("Failed to get dataset with ID '%s': %s", dataset_id, e)
            return None

        with self.get_client(username, host, db_name, collection) as client:
            db = client[db_name]
            col = db[collection]
            documents = col.find()

            prompt_items = []
            for document in documents:
                prompt_item = dl.PromptItem(name=str(document["_id"]))
                prompt_item.add(
                    message={
                        "role": "user",
                        "content": [
                            {
                                "mimetype": dl.PromptType.TEXT,
                                "value": document["prompt"],
                            }
                        ],
                    }
                )
                prompt_items.append(prompt_item)

        result = dataset.items.upload(local_path=prompt_items, overwrite=True)

        # Ensure result is iterable, then convert to a list
        items = list(
            result
            if isinstance(result, (list, tuple, set)) or hasattr(result, '__iter__')
            else [result]
        )

        self.logger.info(
            "Successfully uploaded %d items to dataset '%s'.", len(items), dataset_id
        )
        return items

    def update_record(
        self, item: dl.Item, username: str, host: str, db_name: str, collection: str
    ):
        """
        Updates the specified MongoDB collection with the best response for the specified item.

        :param item: The item to update.
        :param username: The username for the MongoDB server.
        :param host: The hostname of the MongoDB server.
        :param db_name: The name of the MongoDB database.
        :param collection: The name of the MongoDB collection.
        :return: The updated item or None if an error occurs.
        """

        self.logger.info(
            "Updating collection '%s' for item with ID '%s'.", collection, item.id
        )

        prompt_item = dl.PromptItem.from_item(item)
        first_prompt_key = prompt_item.prompts[0].key

        # Find the best response based on annotation attributes
        best_response = None
        model_id, name = None, "human"  # Default value for 'name' if not found

        for resp in item.annotations.list():
            try:
                is_best = resp.attributes.get("isBest", False)
            except AttributeError:
                is_best = False
            if is_best and resp.metadata["system"].get("promptId") == first_prompt_key:
                best_response = resp.coordinates
                model_info = resp.metadata.get("user", {}).get("model", {})
                model_id = model_info.get("model_id", "")
                name = model_info.get("name", "human")
                break

        if best_response is None:
            self.logger.error("No best response found for item ID: '%s'", item.id)
            return None

        with self.get_client(username, host, db_name, collection) as client:
            db = client[db_name]
            col = db[collection]
            col.update_one(
                {"_id": ObjectId(prompt_item.name[:-5])},
                {
                    "$set": {
                        "response": best_response,
                        "model_id": model_id,
                        "name": name,
                    }
                },
            )
        self.logger.info(
            "Successfully updated collection '%s' for item with ID '%s'.",
            collection,
            item.id,
        )
        return item
