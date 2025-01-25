# Use an official Python image as base
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI default port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]