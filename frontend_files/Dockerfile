# Use a minimal base image with Python 3.9 installed
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Step 1: Copy ONLY requirements.txt to leverage Docker layer caching
COPY requirements.txt .

# Step 2: Install Python dependencies ( cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# Step 3: Copy the rest of your app code (recopies instantly when source code changes)
COPY . .

# Define the command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
