# MongoDB Setup and Initial User Database Configuration

This guide will walk you through downloading MongoDB, setting up `mongosh`, and initializing a sample user database.

## Prerequisites

- MongoDB Community (MSI installer)
- MongoDB Shell (`mongosh`)

## Installation Steps

1. **Download MongoDB Community**  
   Download the MongoDB Community Server MSI installer from the official [MongoDB website](https://www.mongodb.com/try/download/community).

2. **Download MongoDB Shell (mongosh)**  
   Download the `mongosh` ZIP file from the MongoDB tools section [here](https://www.mongodb.com/try/download/shell).

3. **Unzip `mongosh`**  
   - Unzip the downloaded `mongosh` ZIP file.
   - Move the extracted contents into the MongoDB installation directory.
  
4. **Add `mongosh` filepath to system environment** 
   - Unzip the downloaded `mongosh` ZIP file.
   - Move the extracted contents into the MongoDB installation directory.

5. **Run MongoDB Shell (mongosh)**  
   Open Command Prompt and navigate to the MongoDB installation directory, then start `mongosh` by typing:
   ```bash
   mongosh
   
   use user_database
   
   db.createCollection("users")
   db.users.insertOne({
       "username": "testuser",
       "password": "hashed_pw_test"
   })

   
