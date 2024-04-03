# Message App

This is a Django application for managing threads and messages.

## Installation

1. Clone the repository:
```
git clone https://github.com/olegbuno/SimpleChat.git
cd message_app
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Apply migrations:
```
python manage.py migrate
```

4. Run the following command to load the data into the database:
```
python manage.py loaddata db_dump.json
```

5. Run the development server:
```
python manage.py runserver
```

## Usage
- Access the admin interface at http://localhost:8000/admin/ and log in using the superuser credentials.
- Access the API endpoints at http://localhost:8000/api/.
- Use authentication tokens for accessing protected endpoints. Obtain tokens using the /api/token/ endpoint.

## API Endpoints
- GET /api/threads/: List all threads.
- GET /api/threads/user_threads/: List threads for the current user.
- POST /api/threads/: Create a new thread.
- DELETE /api/threads/{thread_id}/: Delete a thread. Only a participant of the thread can delete a specific thread.
- POST /api/threads/{thread_id}/create_message/: Create a message in a thread.
- PATCH /api/threads/{thread_id}/mark_as_read/: Mark a message as read in a thread by passing specific id message
  (for example: {"id": 1}) in the body.
- GET /api/threads/unread_messages_count/?user_id=<user_id>/: Retrieve a number of unread messages for the user.
- GET /api/messages/: List all messages.
- POST /api/messages/: Create a message by chosen sender and chosen thread.
- GET /api/messages/?thread_id={thread_id}: List messages for a specific thread.

## Pagination
Pagination is implemented using the LimitOffsetPagination class. Each page contains 10 items by default.
