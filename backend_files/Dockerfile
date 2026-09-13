FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Step 1: Copy ONLY the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Step 2: Install dependencies (this layer stays cached unless requirements.txt changes)
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Step 3: Copy the rest of your project files (recopies quickly when code changes)
COPY . .

# Define the command to start the application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
