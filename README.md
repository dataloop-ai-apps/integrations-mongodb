# MongoDB Integration

This repository provides a service that enables seamless interaction between **MongoDB** and **Dataloop** using **user-password authentification**. The integration is designed to streamline data processing, collection updates, and data uploads between MongoDB and Dataloop datasets.

## Features

- **Secure Authentication** with **user-password authentication** for MongoDB access, ensuring secure and restricted access to sensitive data.
- **Dynamic Document Structure Creation and Updates**: Automatically create and update MongoDB collections based on Dataloop dataset information, allowing flexible schema-less data storage.
- **Flexible Query Execution**: Execute complex MongoDB queries directly from Dataloop using the integrated service, enabling seamless data retrieval and manipulation.
- **Seamless Data Upload**: Upload MongoDB query results directly to Dataloop datasets, streamlining data integration and accessibility across platforms.

## Prerequisites

To set up the integration, you'll need the following information:

- **Host**: The MongoDB server address.
- **User**: The MongoDB username with required permissions.
- **Password**: The password for the specified user.
- **Database and Collection**: In MongoDB, specify the database and collection with at least the following key:
  - **`prompt`**: Represents the prompt to be created in Dataloop.

## Pipeline Nodes

- **Import MongoDB**

  - This node retrieves prompts from a specified MongoDB collection and adds them to a designated dataset in Dataloop, creating prompt items accordingly.

- **Export MongoDB**
  - This node takes the response marked as the best and updates the corresponding document in the MongoDB collection with the response, model name, and ID from Dataloop.

## Acknowledgments

This project makes use of the following open-source software:

- **[PyMongo](https://github.com/mongodb/mongo-python-driver)**: The MongoDB Python driver, distributed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0). PyMongo provides tools for interacting with MongoDB in Python. For more information about PyMongo, visit its [documentation](https://pymongo.readthedocs.io/) or [GitHub repository](https://github.com/mongodb/mongo-python-driver).
