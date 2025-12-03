# Use an official lightweight Python image.
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the requirements file and install dependencies
COPY pyproject.toml .
RUN uv pip install --system --no-cache --compile -r pyproject.toml

# FROM python:3.11-slim as final
# Set the working directory
# WORKDIR /app

# Copy the installed dependencies from the builder stage
# COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
