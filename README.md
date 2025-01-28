
---

# **Video Editor API**

This is a Django-based project providing REST APIs for video file management. It includes functionalities like video upload, trimming, merging, and sharing videos with expiration links.

## **Setup Instructions**

### **Requirements**
- **Python**: 3.9 or higher
- **Django**: 4.x
- **FFmpeg**: Ensure FFmpeg is installed and added to your system's PATH. You can download FFmpeg from [here](https://ffmpeg.org/download.html).

---

### **Step 1: Clone the Repository**
```bash
git clone <repository_url>
cd video_editor
```

---

### **Step 2: Set Up the Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate    # On Linux/Mac
venv\Scripts\activate       # On Windows
```

---

### **Step 3: Install Dependencies**
Install the required Python packages:
```bash
pip install -r requirements.txt
```

---

### **Step 4: Apply Migrations**
Set up the database by running:
```bash
python manage.py migrate
```

---

### **Step 5: Run the Server**
Start the Django development server:
```bash
python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000/`.

---

## **Running the Test Suite**

To execute all tests and check coverage:
```bash
python manage.py test
```

---

## **Available API Endpoints**

The API provides the following endpoints:

1. **Upload Video**
   - URL: `/api/videos/upload/`
   - Method: `POST`

2. **Trim Video**
   - URL: `/api/videos/<id>/trim/`
   - Method: `POST`

3. **Merge Videos**
   - URL: `/api/videos/merge/`
   - Method: `POST`

4. **Generate Shareable Link**
   - URL: `/api/videos/<id>/share/`
   - Method: `POST`

For detailed API usage, import the Postman collection from the provided `postman_collection.json` https://www.postman.com/binoyoza/workspace/video-editor/collection/11066510-5fc5cb38-a0dd-483d-9cec-4ee5aa94d1a2?action=share&creator=11066510.

---

## **Future Scope/Improvements**
- Modularize code to handle core logic of validation of upload video, trim and merge video.
- Video upload process can be made async using queue mechanism.
- Use of CDN service to include cache to use already trimmed videos for further trim request.
- Replace static token based authentication with JWT token authentication.

---


## **Notes**
- Ensure FFmpeg is correctly installed and accessible, as it's required for video processing.
- SQLite is used as the database for simplicity. For production, configure a more robust database like PostgreSQL.

---
